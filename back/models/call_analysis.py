from pydantic import BaseModel
from typing import List, Optional

class CallAnalysis(BaseModel):
    file_name: str
    full_transcript: str
    summary: str
    tags: List[str]
    language: str
    uploaded_at: str
    processed_at: Optional[str] = None