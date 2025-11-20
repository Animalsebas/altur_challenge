from faster_whisper import WhisperModel
import time
import os

MODEL_SIZE = "tiny"
_total_cpus = os.cpu_count() or 1
_SAFETY_RESERVE = 1
CPU_THREADS = max(1, _total_cpus - _SAFETY_RESERVE)
COMPUTE_TYPE = "int8"

# Load the Whisper model once
model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type=COMPUTE_TYPE,
    cpu_threads=CPU_THREADS
)

def transcribe_file(file_path: str):
    try:
        start_time = time.time()
        segments, info = model.transcribe(file_path, beam_size=5)
        transcription = "".join([segment.text for segment in segments]).strip()
        return {
            "transcription": transcription,
            "language": info.language.upper(),
            "transcribe_time": time.time() - start_time,
        }
    except Exception as e:
        raise RuntimeError(f"Error during transcription: {str(e)}")