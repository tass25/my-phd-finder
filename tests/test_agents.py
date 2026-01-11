import pytest
from src.agents import MessageBus, Agent
from typing import Dict, Any

class MockAgent(Agent):
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "received": message}

def test_message_bus_registration():
    bus = MessageBus()
    agent = MockAgent("TestAgent")
    bus.register_agent(agent)
    assert "TestAgent" in bus.agents
    assert bus.agents["TestAgent"] == agent

def test_message_bus_send():
    bus = MessageBus()
    agent = MockAgent("TestAgent")
    bus.register_agent(agent)
    response = bus.send_message("TestAgent", {"data": "hello"})
    assert response["status"] == "success"
    assert response["received"]["data"] == "hello"

def test_agent_log_decision(mocker):
    # Mocking sqlite3 to avoid DB writes during tests
    mocker.patch("sqlite3.connect")
    agent = MockAgent("TestAgent")
    agent.log_decision("Task", "Decision", "Reasoning", 0.9, True)
    assert len(agent.history) == 1
    assert agent.history[0]["task"] == "Task"
