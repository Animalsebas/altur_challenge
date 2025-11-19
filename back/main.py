from fastapi import FastAPI
from routers import items
from analize import router as analyze_router

app = FastAPI()

app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(analyze_router, prefix="/api", tags=["analyze"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Altur Call Analyzer API!"}