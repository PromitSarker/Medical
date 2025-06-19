import os
import logging
import httpx
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from App.core.config import settings
from App.core.storage import DataStorage
from typing import Dict, List, Any
from collections import defaultdict
from fastapi import HTTPException

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
        self.storage = DataStorage()
        self.max_history = 15

    def _parse_urgency_level(self, level: str) -> str:
        """Validate and normalize urgency level"""
        valid_levels = {"EMERGENCY", "URGENT", "ROUTINE"}
        if not level:
            return "ROUTINE"
        
        # Clean and normalize the input
        normalized = level.upper().strip()
        
        # Handle variations
        if "EMERG" in normalized:
            return "EMERGENCY"
        elif "URG" in normalized:
            return "URGENT"
        elif "ROUTINE" in normalized or "REGULAR" in normalized:
            return "ROUTINE"
            
        return "ROUTINE"

    def _get_recommendations(self, urgency_level: str) -> List[str]:
        """Get recommendations based on urgency level"""
        recommendations = {
            "EMERGENCY": [
                "Seek immediate emergency care",
                "Call emergency services (911)",
                "Do not drive yourself to the hospital"
            ],
            "URGENT": [
                "Schedule an urgent care visit within 24 hours",
                "Contact your primary care physician immediately",
                "Monitor your symptoms closely"
            ],
            "ROUTINE": [
                "Schedule a regular appointment",
                "Monitor your symptoms",
                "Follow basic self-care guidelines"
            ]
        }
        return recommendations[urgency_level]

    async def get_medical_response(self, message: str, patient_id: str = None) -> Dict[str, Any]:
        try:
            system_prompt = """You are an empathetic medical triage assistant. 
            Analyze the patient's message and provide a structured response.
            
            Your response MUST start with a JSON block containing:
            {
                "urgency": "EMERGENCY" or "URGENT" or "ROUTINE",
                "symptoms": ["symptom1", "symptom2", ...]
            }
            
            Guidelines for urgency levels:
            - EMERGENCY: Life-threatening conditions requiring immediate attention
            - URGENT: Serious conditions needing care within 24 hours
            - ROUTINE: Non-urgent conditions that can wait for regular appointment
            
            After the JSON block, provide your conversational response to the patient."""
            
            # Build conversation history
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            if patient_id:
                history = self.storage.get_patient_history(patient_id)
                for entry in history[-self.max_history:]:
                    messages.extend([
                        {"role": "user", "content": entry["user_message"]},
                        {"role": "assistant", "content": entry["assistant_message"]}
                    ])
            
            # Get AI response
            assistant_message = await self._get_llm_response(messages)
            
            # Extract and parse JSON block
            json_match = re.search(r'\{[\s\S]*?\}', assistant_message)
            if not json_match:
                raise ValueError("No JSON analysis block found in AI response")
            
            try:
                # Clean and parse JSON
                json_str = json_match.group()
                json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
                analysis = json.loads(json_str)
                
                urgency_level = self._parse_urgency_level(analysis.get("urgency"))
                detected_symptoms = analysis.get("symptoms", [])
                
                # Remove JSON from response
                clean_message = assistant_message[json_match.end():].strip()
                
                # Create history entry
                if patient_id:
                    history_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "user_message": message,
                        "assistant_message": clean_message,
                        "triage_level": urgency_level,
                        "symptoms": detected_symptoms
                    }
                    self.storage.add_conversation(patient_id, history_entry)
                
                return {
                    "message": clean_message,
                    "triage_level": urgency_level,
                    "recommendations": self._get_recommendations(urgency_level)
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {e}")
                raise ValueError("Invalid response format from AI")
                
        except Exception as e:
            logger.error(f"Error in get_medical_response: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM"""
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
                raise ValueError(f"API request failed: {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def get_patient_history(self, patient_id: str) -> Dict[str, any]:
        """Retrieve formatted chat history for a specific patient"""
        history = self.storage.get_patient_history(patient_id)
        return {
            "patient_id": patient_id,
            "history": history
        }

    def clear_patient_history(self, patient_id: str) -> None:
        """Clear chat history for a specific patient"""
        self.storage.clear_patient_history(patient_id)