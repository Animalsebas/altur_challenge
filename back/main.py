from fastapi import FastAPI
from routers import analyze
from db import initialize_db

app = FastAPI()

app.include_router(analyze.router, prefix="/api", tags=["analyze"])

@app.on_event("startup")
def on_startup():
    initialize_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Altur Call Analyzer API!"}