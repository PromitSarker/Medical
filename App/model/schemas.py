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

class ChatHistoryEntry(BaseModel):
    timestamp: datetime
    user_message: str
    assistant_message: str
    triage_level: str
    symptoms: List[str]

class ChatHistoryResponse(BaseModel):
    patient_id: str
    history: List[ChatHistoryEntry]