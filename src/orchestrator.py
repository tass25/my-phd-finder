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
        if action == "start_research":
            return self.start_research(message.get("country"))
        return {"status": "error", "message": "Unknown action"}

    def start_research(self, country: str) -> Dict[str, Any]:
        self.log_decision(
            task=f"Research PhD in {country}",
            decision=f"Initiating research flow for {country}",
            reasoning="User requested PhD search in a specific country. Need to discover universities first.",
            confidence=1.0,
            success=True
        )
        
        # Step 1: Discover Universities (Would delegate to ResearchAgent)
        # For now, we'll just acknowledge the task
        return {
            "status": "success",
            "message": f"Research for {country} started. Orchestrator is planning steps.",
            "next_step": "university_discovery"
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
