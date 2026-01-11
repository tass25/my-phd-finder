from abc import ABC, abstractmethod
import json
import sqlite3
import logging
from typing import Dict, Any, List
from config import DB_PATH, logger

class Agent(ABC):
    def __init__(self, name: str, orchestrator=None):
        self.name = name
        self.orchestrator = orchestrator
        self.history: List[Dict[str, Any]] = []

    def log_decision(self, task: str, decision: str, reasoning: str, confidence: float, success: bool):
        decision_entry = {
            "agent_name": self.name,
            "task": task,
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "success": success
        }
        self.history.append(decision_entry)
        
        # Persistent logging to DB
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_decisions (agent_name, task, decision, reasoning, confidence, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.name, task, decision, reasoning, confidence, success))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log decision to DB: {str(e)}")

        logger.info(f"[{self.name}] {decision} (Conf: {confidence})")

    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        pass

class MessageBus:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def send_message(self, recipient_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        if recipient_name not in self.agents:
            raise ValueError(f"Agent {recipient_name} not found")
        return self.agents[recipient_name].process(message)
