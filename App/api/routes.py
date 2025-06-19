from fastapi import APIRouter, HTTPException
from App.model.schemas import ChatRequest, ChatResponse
from App.service.chat_service import MedicalChatService

router = APIRouter(prefix="/api/v1")
chat_service = MedicalChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: str):
    response = await chat_service.get_medical_response(message)
    return response

@router.get("/history/{patient_id}")
async def get_history(patient_id: str):
    return chat_service.get_patient_history(patient_id)

@router.delete("/history/{patient_id}")
async def clear_history(patient_id: str):
    chat_service.clear_patient_history(patient_id)
    return {"status": "success", "message": f"History cleared for patient {patient_id}"}