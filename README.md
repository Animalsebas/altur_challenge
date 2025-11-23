# Altur Sales Calls Analyzer

Altur Sales Calls Analyzer is a complete platform for transcribing, analyzing, and managing sales calls.  
It combines a modern Next.js frontend, a FastAPI backend, and support for both local LLMs via Ollama and remote analysis via OpenAI.

---------------------------------------------------------------------

## Technologies Used and Design Decisions

### Frontend
- Next.js 14 (App Router)
- HeroUI and Tailwind CSS
Chosen for fast development without manually building UI components.

Docker backend uses: node:18-alpine

The frontend includes:
- API routes under `/app/api`
- Components for:
  - Audio upload
  - Tag filtering
  - Table history display
  - Modal/Drawer detailed view
- A history viewer of all previous analyses with options to filter by tag and order by upload timestamp
- A modal that shows the details of an analysis: File metadata, upload timestamp, language of the call, where it was processed (local or with OpenAI API), tags, summary and key information, full transcript and information on the processing time.
- Inside the details modal it is possible to remove tags by clicking the "x" on the side, it is also possible to add a new tag by clicking the "+" button, writing the new tag name and pressing the "Enter" key. There is no need to use a save button since every change is updated in the database automatically.
- There are download buttons on both the history table and the details modal. In the history table the download option will execute the process for the download of all the analyses details that are currently shown in the table (using the current tag filters and order) in JSON format. The download option on the details modal will download the analysis details of the selected call in JSON format.
- Global environment variable:
  `NEXT_PUBLIC_BACKEND_URL` → points to the FastAPI backend
- Integration with backend endpoints:
  - `POST /api/analyze`
  - `GET /api/history`
  - `GET /api/history/{id}`
  - `GET /api/retrieve`
  - `GET /api/retrieve/{id}`
  - `POST /api/updateTags`
- Simple and Intuitive UI with light and dark modes.

### Backend
- FastAPI (Python 3.10 recommended)
- Router modules for analyzing calls, request analysis history, retrieve and download analyses and updating tags (user override)
- Automatic database initialization on startup

Docker backend uses: python:3.10-slim

### Database (Persistent Storage)
- SQLite
Chosen because it's easy to use, lightweight and doesn't require a server (serverless).

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

# How to Run the Project

## 1. Run With Local LLM

### Requirements
- Docker Engine installed
- Clone the main branch of the repository and enter the root folder
- Create a `.env` file in the project root folder (the base folder that has the docker-compose.yml file) with:
    - OPENAI_API_KEY=""
- Close ollama if you have an ollama server already running on 11434

### Linux or macOS
Make the ollama_entrypoint.sh file in the base folder  executable:
- cd ./
- chmod +x ollama_entrypoint.sh

### Windows
Ensure the ollama_entrypoint.sh file uses LF line endings (VSCode → bottom-right → change CRLF to LF).

### Run everything with Docker

From the project root:

- docker compose up --build

Docker will:
- Start the frontend
- Start the backend  
- Initialize the database  
- Start the Ollama server  
- Download the Gemma3:1b model  

You will likely see output such as:
- ollama-1    | pulling manifest ⠧
- gathering model components
- ollama-1    | pulling 7cd4618c1faf 100% ▕███████████████████▏ 815 MB

Wait for the following line in order for the local analysis to be available
- ollama-1    | Model ready. Continuing.

Then go to your browser and open:

- http://localhost:3000

### Run the automated tests
Identify the name of the current backend container
- docker compose ps --format "{{.Names}}"
- Replace the name of the backend container obtained with the command above on the command below to run the tests
- docker exec -it <altur_challenge-backend-index> pytest -q


---------------------------------------------------------------------


## 2. Access to live preview in fly.io (only remote OpenAI API available)
https://altur-sales-call-analyzer.fly.dev/

### Backend URL 
https://altur-backend.fly.dev/


---------------------------------------------------------------------


## 3. Run modules separately for development

There is no one-line Docker command for this mode. For running the front end and back end modules this way you must have NodeJS and Python installed in your system.
- https://www.python.org
- https://nodejs.org/en

### Start the Frontend
- cd ./front
- npm install
- npm run dev


### Start the Backend
- cd ./
- pip install -r ./backend/requirements.txt
- uvicorn back.main:app --reload
If the backend has trouble finding the .env on the root folder copy it into the ./back folder.

### Ollama
If you want to also test the local analysis separately install ollama and gemma3:1B in your system.
- https://ollama.com/

### Run the automated tests without docker
- cd ./
- pytest -q


---------------------------------------------------------------------

## API Endpoints Overview

| Endpoint               | Method | Description                                                           |
|------------------------|--------|-----------------------------------------------------------------------|
| /api/analyze           | POST   | Sends audio and returns LLM analysis                                  |
| /api/history           | GET    | Returns processed call history without details                        |
| /api/history/{id}      | GET    | Returns the full details of a call by ID                              |
| /api/retrieve/{id}     | GET    | Retrieves full JSON analysis by ID                                    |
| /api/retrieve          | GET    | Retrieves full JSON analysis (with tags filter and order asc or desc) |
| /api/updateTags        | POST   | Sends ID and Tags list and updates it in the DB                       |
| /                      | GET    | Welcome message                                                       |

### Example URLs

http://localhost:8000/api/history

http://localhost:8000/api/retrieve/1

http://localhost:8000/api/retrieve/123

https://altur-backend.fly.dev/api/retrieve/1


### Filter by tags

http://localhost:8000/api/retrieve?tags=Client+Needs+Follow-up

http://localhost:8000/api/retrieve?tags=Client+Needs+Follow-up&tags=Budget

### Order by Upload time
http://localhost:8000/api/retrieve?order=desc

### Filter by tags and order by Upload time
http://localhost:8000/api/retrieve/?tags=Demo+Scheduled&order=asc

## Automated Tests

The project includes two automated tests that verify the functionality of the `/api/retrieve` endpoints.  
The instructions for running these tests are already described in the **How to Run the Project** section, where you run:

- docker exec -it altur_challenge-backend-1 pytest -q

### Automated Test 1: Retrieve (Single Record)
- This test validates that the /api/retrieve/{id} endpoint correctly retrieves a single record from the database.

### Automated Test 2: Retrieve List (Ordered Results)
- This test verifies that the /api/retrieve endpoint can return an ordered list of records.
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
- I would also like to add more automated tests to verify all the functions and processes.

## Prompt design:
- I designed the analysis prompts to force the AI to give the output in the most standard way, because I didn't want to spend to much time in reformatting, especially on the tags, so I asked for markdown and json outputs to make the formatting and front-end presentation easier.
- I also gave guidance and examples on the prompts to align the analysis to the required output.
