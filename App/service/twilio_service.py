from twilio.rest import Client
from App.core.config import settings
from App.service.chat_service import MedicalChatService
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        if not settings.ENABLE_TWILIO:
            self.client = None
            self.phone_number = None
        else:
            if not all([
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_PHONE_NUMBER
            ]):
                raise ValueError("Twilio credentials not properly configured")
                
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID, 
                settings.TWILIO_AUTH_TOKEN
            )
            self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        self.chat_service = MedicalChatService()

    async def handle_incoming_message(self, from_number: str, message_body: str):
        """Handle incoming SMS message"""
        if not settings.ENABLE_TWILIO:
            raise HTTPException(
                status_code=501,
                detail="SMS functionality is not enabled"
            )
            
        try:
            patient_id = from_number.replace('+', '')
            response = await self.chat_service.get_medical_response(
                message=message_body,
                patient_id=patient_id
            )
            
            message_text = (
                f"{response['message']}\n\n"
                f"Urgency Level: {response['triage_level']}\n"
                "Recommendations:\n" + 
                "\n".join(f"- {r}" for r in response['recommendations'])
            )
            
            if self.client:
                self.send_message(to_number=from_number, message=message_text)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling SMS: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def send_message(self, to_number: str, message: str):
        """Send SMS message using Twilio"""
        if not self.client:
            raise HTTPException(
                status_code=501,
                detail="SMS functionality is not enabled"
            )
            
        try:
            self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))