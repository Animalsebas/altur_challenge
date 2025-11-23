# Altur Sales Calls Analyzer

Altur Sales Calls Analyzer is a complete platform for transcribing, analyzing, and managing sales calls.  
It combines a modern Next.js frontend, a FastAPI backend, and support for both local LLMs via Ollama and remote analysis via OpenAI.

---------------------------------------------------------------------

## Technologies Used and Design Decisions

### Frontend
- Next.js 14 (App Router)
- HeroUI  
Chosen for fast development without manually building UI components.

Docker backend uses: node:18-alpine

The frontend includes:
- API routes under `/app/api`
- Components for:
  - Audio upload
  - Tag filtering
  - Table history display
  - Modal/Drawer detailed view
- A history viewer
- Global environment variable:
  `NEXT_PUBLIC_BACKEND_URL` → points to the FastAPI backend
- Integration with backend endpoints:
  - `POST /api/analyze`
  - `GET /api/history`
  - `GET /api/history/{id}`
  - `GET /api/retrieve`
  - `GET /api/retrieve/{id}`
- Simple and Intuitive UI with light and dark modes.

### Backend
- FastAPI (Python 3.10 recommended)
- Router modules for analyze, history, and retrieve
- Automatic database initialization on startup

Docker backend uses: python:3.10-slim

### Local LLM (Ollama)
Supports local LLM inference through Ollama using:
- Gemma 3 (1B) for analysis  
- Whisper Tiny for transcription  

Ollama is executed inside Docker using the lightweight alpine/ollama CPU-only image.

Expected Ollama port: 11434  
Ollama + model download size: approximately 880 MB

Purpose:
- Demonstrate fully local, offline AI
- Allow both transcription and analysis without accessing the internet

### OpenAI API
Used when selecting remote processing:
- gpt-4o-transcribe for transcription  
- gpt-4o-mini for analysis  

This minimizes token cost while preserving accuracy.

---------------------------------------------------------------------

## How to Run the Project

# 1. Run With Local LLM

### Requirements
- Docker Engine installed
- Create a `.env` file in the project root with:
    - OPENAI_API_KEY=""

### Linux or macOS
Make the entrypoint executable:
- chmod +x ollama_entrypoint.sh

### Windows
Ensure the file uses LF line endings (VSCode → bottom-right → change CRLF to LF).

### Run everything with Docker

From the project root:

- docker compose up --build

Docker will:
- Start the frontend
- Start the backend  
- Initialize the database  
- Start the Ollama server  
- Download the Gemma3:1b model  

Then go to your browser and open:

- http://localhost:3000

---------------------------------------------------------------------

# 2. Run Without a Local LLM (Remote OpenAI Only)

There is no one-line Docker command for this mode.

### Start the Frontend
- cd ./front
- npm install
- npm run dev


### Start the Backend
- cd ./backend
- pip install -r requirements.txt
- uvicorn main:app --port 8000


---------------------------------------------------------------------

## API Endpoints Overview

| Endpoint               | Method | Description                                                           |
|------------------------|--------|-----------------------------------------------------------------------|
| /api/analyze           | POST   | Sends audio and returns LLM analysis                                  |
| /api/history           | GET    | Returns processed call history without details                        |
| /api/history/{id}      | GET    | Returns the full details of a call by ID                              |
| /api/retrieve/{id}     | GET    | Retrieves full JSON analysis by ID                                    |
| /api/retrieve          | GET    | Retrieves full JSON analysis (with tags filter and order asc or desc) |
| /                      | GET    | Welcome message                                                       |

### Example URLs

http://localhost:8000/api/history

http://localhost:8000/api/retrieve/1

http://localhost:8000/api/retrieve/123


### Filter by tags

http://localhost:8000/api/retrieve?tags=Client+Needs+Follow-up

http://localhost:8000/api/retrieve?tags=Client+Needs+Follow-up&tags=Budget

### Order by Upload time
http://localhost:8000/api/retrieve?order=desc

### Filter by tags and order by Upload time
http://localhost:8000/api/retrieve/?tags=Demo+Scheduled&order=asc


---------------------------------------------------------------------

## Project Structure
- front/ → Next.js App (HeroUI)
- backend/ → FastAPI + routers + DB
- docker-compose.yml
- ollama_entrypoint.sh
- Modelfile
- .env


---------------------------------------------------------------------

## Notes

- Fully supports local-only inference (no internet required)
- Demonstrates privacy-friendly, on-device AI with small models
- Supports remote OpenAI workflows for higher accuracy
- Architecture is optimized for lightweight deployment and testing on systems with low resources.

## Assumptions made:
- I assumed that the web app should only allow one call analysis at a time per user.
- I assumed file re-encoding wouldn't be needed since the user already had their calls in either MP3 or WAV format.

## Architecture/Design Decisions:
- I used NextJS since it is the framework I have the most experience with, and I used HeroUI components to save time on the front end design.
- I implemented "proxy" API routes in the Nextjs App to the FastAPI endpoint to avoid the Access-Control-Allow-Origin error.
- I used FastAPI since I have more experience with Python and that framework 
- For the local analysis, the tiny version of the OpenAI Whisper model was selected for its speed and low system requirements. The same consideration was made for the Gemma 3 1B model. The purpose is only to show that local processing is possible even with low system resources and no GPU. With a GPU and more RAM, it would be possible to use the same models that the OpenAI API has available locally.

## Improvements possible given more time:
- I would like to include the functionality of adding more than one call simultaneously, and if local analysis is selected, I would create a queue to prevent the models from overloading the system's resources and sequentially insert the results into the database, this would allow the user to continue uploading calls while others are being processed.

## Prompt design:
- I designed the analysis prompts to force the AI to give the output in the most standard way, because I didn't want to spend to much time in reformatting, especially on the tags, so I asked for markdown and json outputs to make the formatting and front-end presentation easier.
- I also gave guidance and examples on the prompts to align the analysis to the required output.