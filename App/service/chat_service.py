import os
import logging
import httpx
from datetime import datetime
from dotenv import load_dotenv
from App.core.config import settings
from typing import List, Dict, Tuple
from collections import defaultdict

load_dotenv()

logger = logging.getLogger(__name__)

class MedicalChatService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = settings.GROQ_API_URL
        self.model = settings.LLM_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history = []
        self.max_history = 15

    async def get_medical_response(self, message: str) -> Dict[str, any]:
        urgency_level = "ROUTINE"  # Default value moved to top
        try:
            system_prompt = """You are an empathetic medical triage assistant. 
            Analyze the patient's message and:
            1. Determine if their symptoms indicate an EMERGENCY, URGENT, or ROUTINE situation
            2. List any specific symptoms mentioned
            3. Show empathy while gathering medical information
            4. For serious symptoms, emphasize immediate medical attention
            5. For non-emergency cases, suggest scheduling an appointment
            
            Format your internal analysis as JSON at the start of your response like this:
            {{"urgency": "EMERGENCY|URGENT|ROUTINE", "symptoms": ["symptom1", "symptom2"]}}
            
            Then provide your conversational response to the patient."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            messages.extend(self.conversation_history[-self.max_history:])
            
            # Get AI response
            assistant_message = await self._get_llm_response(messages)
            
            # Extract urgency and symptoms from AI response
            try:
                import json
                import re
                
                # Find JSON block at start of response
                json_match = re.match(r'\{.*?\}', assistant_message.strip())
                if json_match:
                    analysis = json.loads(json_match.group())
                    urgency_level = analysis.get("urgency", "ROUTINE").upper()  # Convert to uppercase
                    detected_symptoms = analysis.get("symptoms", [])
                    
                    # Remove the JSON block from the response
                    assistant_message = assistant_message[json_match.end():].strip()
                else:
                    detected_symptoms = []
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {str(je)}")
                detected_symptoms = []
            except Exception as e:
                logger.error(f"Error processing AI response: {str(e)}")
                detected_symptoms = []
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_message}
            ])
            
            # Add recommendations based on AI-detected urgency
            if urgency_level == "EMERGENCY":
                assistant_message += "\n\nBased on your symptoms, please seek immediate medical attention."
            elif detected_symptoms:
                assistant_message += "\n\nWould you like to schedule an appointment to discuss these symptoms?"
            
            return {
                "message": assistant_message,
                "triage_level": urgency_level,  # This will now reflect the correct urgency
                "recommendations": self._get_recommendations(urgency_level)
            }
            
        except Exception as e:
            logger.error(f"MedicalChatService error: {str(e)}")
            return {
                "message": f"Sorry, I encountered an error: {str(e)}",
                "triage_level": urgency_level,  # Using the same urgency_level
                "recommendations": self._get_recommendations(urgency_level)  # Fixed to use _get_recommendations
            }

    def _get_recommendations(self, urgency_level: str) -> List[str]:
        """Get recommendations based on urgency level"""
        if urgency_level == "EMERGENCY":
            return ["Seek immediate emergency care", "Call emergency services"]
        elif urgency_level == "URGENT":
            return ["Schedule urgent care visit", "Contact your doctor"]
        return ["Schedule a regular appointment if symptoms persist"]

    async def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                
            if response.status_code != 200:
                logger.error(f"API error: {response.text}")
                return "Sorry, I encountered an error while processing your request."
                
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Error in _get_llm_response: {str(e)}")
            return "Sorry, I encountered an error while getting a response."