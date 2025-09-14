import os
from dotenv import load_dotenv
from agent import NorthwindAgent

load_dotenv()

def test_agent_initialization():
    """Test if agent can be created successfully"""
    agent = NorthwindAgent()
    assert agent is not None
    assert agent.agent_executor is not None