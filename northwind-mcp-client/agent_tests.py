import os
from dotenv import load_dotenv
from agent import NorthwindAgent

load_dotenv()

def test_agent_initialization():
    """Test if agent can be created successfully"""
    agent = NorthwindAgent()
    assert agent is not None
    assert agent.agent_executor is not None

def test_agent_tools_available():
    """Test if all expected tools are available to the agent"""
    agent = NorthwindAgent()
    available_tools = [tool.name for tool in agent.agent_executor.tools]
    assert len(available_tools) > 0

def test_simple_query_execution():
    """Test agent can execute a simple query"""
    agent = NorthwindAgent()
    result = agent.ask("List the first 5 customers")    
    assert result is not None
    
def test_complex_query_execution():
    """Test agent can handle complex queries"""
    agent = NorthwindAgent()
    result = agent.ask("Show me orders for customer FAPSM with their product details")
    assert result is not None