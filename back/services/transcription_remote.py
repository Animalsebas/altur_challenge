from dotenv import load_dotenv
import os
import time
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_file_remote(file_path: str):
    """
    Remote transcription using OpenAI gpt-4o-transcribe.
    """
    try:
        start = time.time()

        with open(file_path, "rb") as f:
            response = client.audio.transcriptions.create(
                file=f,
                model="gpt-4o-transcribe",
                response_format="json"
            )
        transcription = response.text.strip()
        language = "UNKNOWN"  # INFO: OpenAI does not currently return detected language

        return {
            "transcription": transcription,
            "language": language,
            "transcribe_time": time.time() - start
        }

    except Exception as e:
        raise RuntimeError(f"Remote transcription error: {str(e)}")
