from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyze
from routers import history
from routers import retrieve
from routers import update_tags
from db import initialize_db

app = FastAPI()

origins = [
    "https://altur-frontend.fly.dev", 
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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