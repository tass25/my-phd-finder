from typing import Dict, Any, List
from .agents import Agent, MessageBus
import sqlite3
from config import DB_PATH

class OrchestratorAgent(Agent):
    def __init__(self, message_bus: MessageBus):
        super().__init__("Orchestrator")
        self.message_bus = message_bus
        self.plan: List[Dict[str, Any]] = []

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        if action == "run_full_flow":
            return self.run_full_flow(message.get("country"), message.get("student_profile"))
        return {"status": "error", "message": "Unknown action"}

    def run_full_flow(self, country: str, student_profile: str) -> Dict[str, Any]:
        self.log_decision(
            task=f"PhD Search Flow: {country}",
            decision="Starting 6-Phase Autonomous Flow",
            reasoning="User requested a full search. Initiating orchestration of specialized agents.",
            confidence=1.0,
            success=True
        )
        
        results = {"universities": [], "professors": [], "emails": []}
        
        # Phase 1: University Discovery
        st_msg = "Phase 1: Discovering universities..."
        logger.info(st_msg)
        disc_res = self.message_bus.send_message("Research", {"action": "find_universities", "country": country})
        
        # Phase 2: Analysis & Matching (for top 5 discovered)
        st_msg = "Phase 2 & 3: Analyzing and verifying top universities..."
        logger.info(st_msg)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM universities WHERE country = ? LIMIT 5", (country,))
        uni_ids = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        for uid in uni_ids:
            # Match
            self.message_bus.send_message("Research", {"action": "analyze_university_match", "university_id": uid, "student_profile": student_profile})
            # Verify
            self.message_bus.send_message("Verification", {"action": "verify_university", "university_id": uid})
            
            # Phase 4: Professor Discovery (for each top university)
            st_msg = f"Phase 4: Finding professors at university {uid}..."
            logger.info(st_msg)
            self.message_bus.send_message("Research", {"action": "find_professors", "university_id": uid})
            
        # Phase 5: Email Generation (for top 3 professors found)
        st_msg = "Phase 5: Generating personalized emails..."
        logger.info(st_msg)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM professors LIMIT 3")
        prof_ids = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        for pid in prof_ids:
            self.message_bus.send_message("Outreach", {"action": "generate_email", "professor_id": pid, "student_profile": student_profile})
            
        return {
            "status": "success",
            "message": "Full autonomous search completed successfully.",
            "data": results
        }

    def save_decision_to_db(self, decision_entry: Dict[str, Any]):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_decisions (agent_name, task, decision, reasoning, confidence, success)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            decision_entry["agent_name"],
            decision_entry["task"],
            decision_entry["decision"],
            decision_entry["reasoning"],
            decision_entry["confidence"],
            decision_entry["success"]
        ))
        conn.commit()
        conn.close()
