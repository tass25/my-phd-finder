from typing import Dict, Any, List
from src.agents import Agent
import sqlite3
import json
from config import DB_PATH

class LearningAgent(Agent):
    def __init__(self):
        super().__init__("Learning")

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        if action == "record_feedback":
            return self.record_feedback(message.get("source"), message.get("feedback"))
        return {"status": "error", "message": "Unknown action"}

    def record_feedback(self, source: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        self.log_decision(
            task="Learning from User Feedback",
            decision=f"Updating preferences based on {source} feedback",
            reasoning="Improving future results by learning what the user likes/dislikes.",
            confidence=1.0,
            success=True
        )
        
        # Simple persistence for now
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (key, value)
            VALUES (?, ?)
        """, (f"feedback_{source}_{feedback.get('id')}", json.dumps(feedback)))
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Feedback recorded. I will improve next time!"}
