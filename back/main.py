from fastapi import FastAPI
from routers import analyze
from routers import history
from routers import retrieve
from db import initialize_db

app = FastAPI()

app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(retrieve.router, prefix="/api/retrieve", tags=["retrieve"])

@app.on_event("startup")
def on_startup():
    initialize_db()

@app.get("/")
def read_root():
    return {"message": "Altur Call Analysis Python FastAPI Backend"}