import json
import os
from typing import Dict, List
from datetime import datetime

class DataStorage:
    def __init__(self):
        self.storage_dir = "data"
        self.history_file = os.path.join(self.storage_dir, "chat_history.json")
        self._ensure_storage_exists()
        self._load_history()

    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        if not os.path.exists(self.history_file):
            self._save_history({})

    def _load_history(self) -> Dict:
        """Load history from file"""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_history(self, history: Dict):
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def add_conversation(self, patient_id: str, entry: Dict):
        """Add a new conversation entry"""
        history = self._load_history()
        if patient_id not in history:
            history[patient_id] = []
        history[patient_id].append(entry)
        self._save_history(history)

    def get_patient_history(self, patient_id: str) -> List[Dict]:
        """Get patient conversation history"""
        history = self._load_history()
        return history.get(patient_id, [])

    def clear_patient_history(self, patient_id: str):
        """Clear history for a specific patient"""
        history = self._load_history()
        if patient_id in history:
            history[patient_id] = []
            self._save_history(history)