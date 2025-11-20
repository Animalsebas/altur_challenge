from fastapi import APIRouter, UploadFile, HTTPException, File, Form

from services.transcription import transcribe_file
from services.transcription_remote import transcribe_file_remote

from services.analysis import analyze_transcription
from services.analysis_remote import analyze_transcription_remote

from db import get_db_connection
from datetime import datetime, timezone
import pytz
import json
import os
import asyncio
import logging
from sqlite3 import IntegrityError

router = APIRouter()
logger = logging.getLogger("analyze")
logging.basicConfig(level=logging.INFO)
CDMX_TZ = pytz.timezone('America/Mexico_City')

def insert_analysis_record(conn, file_name, transcription, summary, tags_json, language, processed_where, uploaded_at, processed_at, transcribe_time=None, analysis_time=None):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO call_analyses
        (file_name, full_transcript, summary, tags, language, processed_where, uploaded_at, processed_at, transcribe_time, analysis_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (file_name, transcription, summary, tags_json, language, processed_where, uploaded_at, processed_at, transcribe_time, analysis_time)
    )
    conn.commit()
    return cursor.lastrowid


@router.post("/analyze")
async def analyze_audio(file: UploadFile, analysis_mode: str = Form("local")):
    logger.info("Received analyze request. mode=%s filename=%s", analysis_mode, getattr(file, "filename", None))

    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload an mp3 or wav file.")

    temp_file_path = f"temp_{file.filename}"
    uploaded_at = datetime.now(CDMX_TZ).isoformat()

    try:
        # Save temporary copy of the uploaded file
        file_bytes = await file.read()
        await asyncio.to_thread(lambda: open(temp_file_path, "wb").write(file_bytes))
        logger.info("Temporary file saved: %s", temp_file_path)

        # Run transcription in thread
        if analysis_mode == "remote":
            transcription_result = await asyncio.to_thread(transcribe_file_remote, temp_file_path)
        else:
            transcription_result = await asyncio.to_thread(transcribe_file, temp_file_path)
        transcription_text = transcription_result.get("transcription", "")
        transcribe_time = transcription_result.get("transcribe_time", None)
        language = transcription_result.get("language", "UNKNOWN")
        logger.info("Transcription complete in %.2f seconds.", transcribe_time)

        # Run analysis in thread
        logger.info("Starting analysis of transcription...")
        start_analysis_time = datetime.now(CDMX_TZ)
        if analysis_mode == "remote":
            analysis_result = await asyncio.to_thread(analyze_transcription_remote, transcription_text)
        else:
            analysis_result = await asyncio.to_thread(analyze_transcription, transcription_text)
        analysis_time = (datetime.now(CDMX_TZ) - start_analysis_time).total_seconds()
        summary = analysis_result.get("summary_report", "")
        tags_list = analysis_result.get("tags_list", [])
        processed_at = datetime.now(CDMX_TZ).isoformat()
        logger.info("Analysis complete in %.2f seconds.", analysis_time)

        # Save results to DB in a thread
        tags_json = json.dumps(tags_list)
        def db_work():
            conn = get_db_connection()
            try:
                return insert_analysis_record(conn, file.filename, transcription_text, summary, tags_json, language, analysis_mode, uploaded_at, processed_at, transcribe_time, analysis_time)
            finally:
                conn.close()
        try:
            inserted_id = await asyncio.to_thread(db_work)
        except IntegrityError as e:
            logger.exception("DB IntegrityError")
            raise HTTPException(status_code=409, detail="File already processed")

        # Return results
        return {
            "id": inserted_id,
            "file_name": file.filename,
            "language": language,
            "transcription": transcription_text,
            "summary": summary,
            "tags_list": tags_list,
            "transcribe_time": transcribe_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing file")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Remove temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info("Removed temporary file: %s", temp_file_path)
        except Exception:
            logger.exception("Failed to remove temp file")