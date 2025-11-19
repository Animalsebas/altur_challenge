from faster_whisper import WhisperModel
import time
import os

AUDIO_FILE_PATH = r"C:\Users\anima\Downloads\calls\call_02.mp3"
MODEL_SIZE = "medium"
CPU_THREADS = 6
COMPUTE_TYPE = "int8"

def transcribe(audio_path, model_size, threads, compute):
    print("Starting Transcription...")
    print(f"Model: {model_size} | Threads: {threads} | Compute: {compute}")
    
    start_load_time = time.time()
    
    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type=compute,
        cpu_threads=threads 
    )
    
    load_time = time.time() - start_load_time
    print(f"Model loaded in {load_time:.2f} seconds.")

    start_transcribe_time = time.time()
    segments, info = model.transcribe(audio_path, beam_size=5) # language=language_code
    transcribe_time = time.time() - start_transcribe_time
    transcribed_text = "".join([segment.text for segment in segments])

    print(f"File: {audio_path}")
    print(f"Time Taken: {transcribe_time:.2f} seconds")
    print(f"Detected Language: {info.language.upper()} (Probability: {info.language_probability:.4f})")
    
    transcription = transcribed_text.strip()

if __name__ == '__main__':
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"Error: Audio file not found at '{AUDIO_FILE_PATH}'")
    else:
        transcribe(
            AUDIO_FILE_PATH,
            MODEL_SIZE,
            CPU_THREADS,
            COMPUTE_TYPE
        )