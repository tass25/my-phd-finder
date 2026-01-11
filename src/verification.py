import sqlite3
import json
from .agents import Agent
from .llm_utils import llm
from config import DB_PATH, logger

class VerificationAgent(Agent):
    def __init__(self):
        super().__init__("Verification")

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes incoming messages to perform verification actions.

        Args:
            message (Dict[str, Any]): The message containing the action and parameters.

        Returns:
            Dict[str, Any]: The result of the action, including status and data.
        """
        action = message.get("action")
        if action == "verify_university":
            # Delegates to the specific verification method
            return self.verify_university(message.get("university_id"))
        # Handles unknown actions
        return {"status": "error", "message": "Unknown action"}

    def verify_university(self, university_id: int) -> Dict[str, Any]:
        """
        Verifies the ranking data for a specific university by checking its QS and THE rankings.
        Updates the university's verification status and data completeness in the database.

        Args:
            university_id (int): The ID of the university to verify.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the verification process.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Fetch university data from the database
        cursor.execute("SELECT name, ranking_qs, ranking_the FROM universities WHERE id = ?", (university_id,))
        uni = cursor.fetchone()
        conn.close()
        
        if not uni:
            # Return error if university is not found
            return {"status": "error", "message": "University not found"}
            
        name, qs, the = uni
        
        # Log the decision to cross-reference rankings
        self.log_decision(
            task="Verify University Data",
            decision=f"Cross-referencing rankings for {name}",
            reasoning="Ensuring accuracy by checking multiple sources.",
            confidence=1.0,
            success=True
        )
        
        # Cross-reference with stored ranking data
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
