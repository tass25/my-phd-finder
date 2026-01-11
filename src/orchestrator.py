from typing import Dict, Any, List
from src.agents import Agent, MessageBus
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
        logger.info("=" * 50)
        logger.info("🔍 PHASE 1: Discovering universities in " + country)
        logger.info("=" * 50)
        disc_res = self.message_bus.send_message("Research", {"action": "find_universities", "country": country})
        logger.info(f"✅ Discovered {disc_res.get('count', 0)} universities")
        
        # Phase 2: Analysis & Matching (for top 5 discovered)
        logger.info("=" * 50)
        logger.info("🎯 PHASE 2 & 3: Analyzing and verifying top universities")
        logger.info("=" * 50)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM universities WHERE country = ? LIMIT 5", (country,))
        unis = cursor.fetchall()
        conn.close()
        
        for idx, (uid, uname) in enumerate(unis, 1):
            logger.info(f"📊 Analyzing university {idx}/5: {uname}")
            # Match
            self.message_bus.send_message("Research", {"action": "analyze_university_match", "university_id": uid, "student_profile": student_profile})
            # Verify
            self.message_bus.send_message("Verification", {"action": "verify_university", "university_id": uid})
            
            # Phase 4: Professor Discovery (for each top university)
            logger.info(f"👨‍🔬 PHASE 4: Finding professors at {uname}")
            self.message_bus.send_message("Research", {"action": "find_professors", "university_id": uid})
            
        # Phase 5: Email Generation (for top 3 professors found)
        logger.info("=" * 50)
        logger.info("📧 PHASE 5: Generating personalized emails")
        logger.info("=" * 50)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM professors LIMIT 3")
        profs = cursor.fetchall()
        conn.close()
        
        for idx, (pid, pname) in enumerate(profs, 1):
            logger.info(f"✍️ Generating email {idx}/3 for {pname}")
            self.message_bus.send_message("Outreach", {"action": "generate_email", "professor_id": pid, "student_profile": student_profile})
        
        logger.info("=" * 50)
        logger.info("✅ FLOW COMPLETED SUCCESSFULLY!")
        logger.info("=" * 50)
            
        return {
            "status": "success",
            "message": "Full autonomous search completed successfully.",
            "data": results
        }

