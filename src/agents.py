from abc import ABC, abstractmethod
import json
from typing import Dict, Any, List

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
        # In a real implementation, we would also write this to the SQLite agent_decisions table
        print(f"[{self.name}] Decision: {decision} (Confidence: {confidence})")

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
