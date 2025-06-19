from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    patient_message: str
    patient_id: str

class ChatResponse(BaseModel):
    message: str
    triage_level: Optional[str]

class TriageStatus(BaseModel):
    level: str
    recommendations: List[str]
    last_updated: datetime
    symptoms: List[str]