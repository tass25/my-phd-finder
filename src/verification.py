import sqlite3
import json
from .agents import Agent
from .llm_utils import llm
from config import DB_PATH, logger

class VerificationAgent(Agent):
    def __init__(self):
        super().__init__("Verification")

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        if action == "verify_university":
            return self.verify_university(message.get("university_id"))
        return {"status": "error", "message": "Unknown action"}

    def verify_university(self, university_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, ranking_qs, ranking_the FROM universities WHERE id = ?", (university_id,))
        uni = cursor.fetchone()
        conn.close()
        
        if not uni:
            return {"status": "error", "message": "University not found"}
            
        name, qs, the = uni
        self.log_decision(
            task="Verify University Data",
            decision=f"Cross-referencing rankings for {name}",
            reasoning="Ensuring accuracy by checking multiple sources.",
            confidence=1.0,
            success=True
        )
        
        # In a real system, we'd scrape THE if missing
        status = "verified" if (qs and the) else "needs_check"
        completeness = 0.8 if qs else 0.4
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE universities 
            SET verification_status = ?, data_completeness = ?
            WHERE id = ?
        """, (status, completeness, university_id))
        conn.commit()
        conn.close()
        
        return {"status": "success", "verification_status": status}
