from fastapi import APIRouter, UploadFile, HTTPException
from faster_whisper import WhisperModel
import os
import time
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import re

router = APIRouter()

# Configuration
MODEL_SIZE = "tiny"
CPU_THREADS = 6
COMPUTE_TYPE = "int8"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"

# Load the Whisper model once to avoid reloading for every request
print(f"Loading Whisper model '{MODEL_SIZE}'...")
start_load_time = time.time()
model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type=COMPUTE_TYPE,
    cpu_threads=CPU_THREADS
)
load_time = time.time() - start_load_time
print(f"Whisper model loaded successfully in {load_time:.2f} seconds.")

# Thread pool for running transcription tasks
executor = ThreadPoolExecutor(max_workers=2)

def ollama_call(prompt: str):
    """Handles the communication with the Ollama API."""
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_thread": CPU_THREADS,
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "").strip()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ollama API error: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"LLM Summarization Service Unavailable. Ensure Ollama is running and model {OLLAMA_MODEL} is pulled. Error: {e}"
        )
    
def transcribe_file(file_path: str):
    """
    Function to handle the transcription process in a separate thread.
    """
    try:
        print("Starting audio transcription...")
        start_transcribe_time = time.time()
        
        segments, info = model.transcribe(file_path, beam_size=5)

        transcription = "".join([segment.text for segment in segments]).strip()

        transcribe_time = time.time() - start_transcribe_time
        print(f"Transcription complete in {transcribe_time:.2f} seconds.")

        print(f"Detected Language: {info.language.upper()}")

        return {
            "transcription": transcription,
            "language": info.language.upper(),
            "language_probability": info.language_probability,
            "transcribe_time": transcribe_time
        }
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise e

def analyze_transcription(transcription: str):
    """
    Performs two sequential calls to Ollama: 
    1. To generate the detailed summary report.
    2. To generate the tags list based on the summary report.
    """
    
    # --- STEP 1: GENERATE THE DETAILED SUMMARY REPORT (String output) ---
    print("Step 1: Generating detailed summary report...")
    
    summary_prompt = (
        "You are an expert call center analyst. Your task is to provide a detailed, contextual summary of the sales or service call transcript provided below, which involves a conversation between two persons. "
        "This transcript can be in any language, and you must always translate the analysis to English. "
        "Your output MUST contain exactly two sections: a Narrative Summary and a Key Facts Extracted list. "
        "DO NOT include any introductory text, closing remarks, or commentary outside of the requested structure.\n\n"
        
        "### 1. Narrative Summary\n"
        "**Objective:** [State the primary purpose of the call, identifying the seller/agent and the client/customer.]\n"
        "**Client Pain Points/Request:** [Detail the specific issues, challenges, or requests the customer is currently facing, including any mentioned numerical or operational details.]\n"
        "**Resolution/Proposal:** [Explain the specific action taken, the solution provided by the agent, or the offer/proposal made by the seller.] \n"
        "**Next Steps:** [Clearly state the agreed-upon next action, follow-up date, or final commitment.]\n\n"
        
        "### 2. Key Facts Extracted\n"
        "GENERATE a list of exactly four bullet points using only quantifiable facts and specific names/dates found in the transcript. Each bullet point MUST start with the metric name in bold, followed by a colon and the extracted detail.\n"
        "* **Client Name and Role:** [Name and Role]\n"
        "* **Final Action Date/Time:** [The full date and time of the next scheduled meeting or follow-up]\n"
        "* **Associated Product/Service:** [The product, service, or issue at the center of the call]\n\n"
        
        "**TRANSCRIPT:**\n"
        f"---{transcription}---"
    )
    
    summary_report = ollama_call(summary_prompt)
    if not summary_report or "Error" in summary_report:
        # Check for non-Ollama errors caught in ollama_call
        if "Service Unavailable" in summary_report:
            raise HTTPException(status_code=503, detail=summary_report)
        return {
            "summary_report": "Error: Failed to generate summary report.",
            "tags_list": ["Error: Summary generation failed"]
        }

    # --- STEP 2: GENERATE THE TAGS LIST (JSON output based on the summary) ---
    print("Step 2: Generating tags list based on summary...")
    
    tags_prompt = (
        "You are an expert call center analyst. Your task is to read the provided summary report and generate status tags for lead management. "
        "The tags must indicate the immediate status or outcome of the call. "
        "Your output MUST be a **single, valid JSON object** with exactly one top-level key: 'tags_list'. "
        "The value of 'tags_list' must be a JSON list of one or more relevant, precise tags. "
        "**CRITICAL EXAMPLES:** 'Client wants to buy', 'Wrong number', 'Needs follow-up', 'Voicemail', 'Qualified Lead', 'Pricing Inquiry', 'Demo Scheduled', 'Closed Lost'. "
        "**DO NOT** include any surrounding Markdown fences (```json) or commentary. **BEGIN** your response immediately with the opening curly brace '{'.\n\n"
        
        "**SUMMARY REPORT:**\n"
        f"---{summary_report}---"
    )
    
    raw_json_string = ollama_call(tags_prompt)
    
    try:
        match = re.search(r'(\{.*?\})', raw_json_string, re.DOTALL)
        if not match:
            print(f"[ERROR] LLM did not return any JSON object for tags.")
            tags_list = ["Error: Tag generation failed (no JSON object found)"]
        else:
            json_to_parse = match.group(1)
            parsed_data = json.loads(json_to_parse)
            tags_list = parsed_data.get("tags_list", ["Error: Tags list missing or invalid."])

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON for tags: {e}")
        print(f"Raw tag response: {raw_json_string[:500]}...")
        tags_list = [f"Error: JSON Decode Error for tags: {e}"]
        
    return {
        "summary_report": summary_report,
        "tags_list": tags_list
    }
    
# --- Main API Endpoint ---

@router.post("/analyze")
async def analyze_audio(file: UploadFile):
    print(f"\n[REQUEST START] Processing file: {file.filename} (Type: {file.content_type})")
    
    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        print(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload an mp3 or wav file.")

    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Save the file temporarily
        file_content = await file.read()
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        print("Temporary file saved.")
        
        # 1. Run transcription in a separate thread
        future = executor.submit(transcribe_file, temp_file_path)
        transcription_result = future.result() 

        # 2. Get the structured analysis (summary and tags)
        full_transcript = transcription_result["transcription"]
        
        start_summary_time = time.time()
        summary_data = analyze_transcription(full_transcript) 
        summary_time = time.time() - start_summary_time
        print(f"Analysis complete in {summary_time:.2f} seconds.")

        # 3. Combine and return final results
        return {
            "file_name": file.filename,
            "language": transcription_result["language"],
            "transcription": full_transcript,
            "summary": summary_data["summary_report"],
            "tags_list": summary_data["tags_list"],
            "transcribe_time": transcription_result["transcribe_time"],
            "analysis_time": summary_time
        }
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Critical error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Critical error during file analysis: {str(e)}")
        
    finally:
        # Remove the temporary file
        if os.path.exists(temp_file_path):
            print(f"Removing temporary file: {temp_file_path}")
            os.remove(temp_file_path)
        print("[REQUEST END] File processing finished.")