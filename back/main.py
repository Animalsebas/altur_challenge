from fastapi import FastAPI
from routers import analyze
from routers import history
from routers import retrieve
from routers import update_tags
from db import initialize_db

app = FastAPI()

app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(retrieve.router, prefix="/api/retrieve", tags=["retrieve"])
app.include_router(update_tags.router, prefix="/api", tags=["update_tags"])

@app.on_event("startup")
def on_startup():
    initialize_db()

@app.get("/")
def read_root():
    return {"message": "Altur Call Analysis Python FastAPI Backend"}