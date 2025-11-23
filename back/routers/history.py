from fastapi import APIRouter, HTTPException
from back.db import get_db_connection
import json

router = APIRouter()


@router.get("/history")
def get_history(limit: int = 50):
    """
    Return a list of recent analyses with only id, file_name, uploaded_at, tags.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, file_name, uploaded_at, tags FROM call_analyses ORDER BY uploaded_at DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            raw_tags = r["tags"]
            try:
                tags_list = json.loads(raw_tags) if raw_tags else []
            except Exception:
                tags_list = []
            result.append(
                {
                    "id": r["id"],
                    "file_name": r["file_name"],
                    "uploaded_at": r["uploaded_at"],
                    "tags": tags_list,
                }
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/history/{analysis_id}")
def get_history_item(analysis_id: int):
    """
    Return ALL columns for a single analysis row by id.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM call_analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis not found")

        record = dict(row)

        raw_tags = record.get("tags")
        try:
            record["tags"] = json.loads(raw_tags) if raw_tags else []
        except Exception:
            record["tags"] = []

        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()