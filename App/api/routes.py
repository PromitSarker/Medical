from fastapi import APIRouter, HTTPException, Form, Request
from App.model.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from App.service.chat_service import MedicalChatService
from App.service.twilio_service import TwilioService
from App.core.config import settings

router = APIRouter(prefix="/api/v1")
chat_service = MedicalChatService()
twilio_service = TwilioService()

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

@router.post("/twilio/webhook")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    """Handle incoming Twilio SMS webhook"""
    if not settings.ENABLE_TWILIO:
        raise HTTPException(
            status_code=501,
            detail="SMS functionality is not enabled"
        )
        
    try:
        response = await twilio_service.handle_incoming_message(
            from_number=From,
            message_body=Body
        )
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))