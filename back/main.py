from fastapi import FastAPI
from routers import analyze
from routers import history
from db import initialize_db

app = FastAPI()

app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(history.router, prefix="/api", tags=["history"])

@app.on_event("startup")
def on_startup():
    initialize_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Altur Call Analyzer API!"}