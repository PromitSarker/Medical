from fastapi import APIRouter, HTTPException
from App.model.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from App.service.chat_service import MedicalChatService

router = APIRouter(prefix="/api/v1")
chat_service = MedicalChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await chat_service.get_medical_response(
            message=request.patient_message,
            patient_id=request.patient_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{patient_id}", response_model=ChatHistoryResponse)
async def get_history(patient_id: str):
    return chat_service.get_patient_history(patient_id)

@router.delete("/history/{patient_id}")
async def clear_history(patient_id: str):
    chat_service.clear_patient_history(patient_id)
    return {"status": "success", "message": f"History cleared for patient {patient_id}"}