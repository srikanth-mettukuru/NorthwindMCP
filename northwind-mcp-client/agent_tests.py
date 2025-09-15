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
    """Test agent can handle a simple query"""
    agent = NorthwindAgent()
    result = agent.ask("List the first 5 customers")    
    assert result is not None
    # Check for keywords indicating customer data - 'any' function returns True if any keyword from the list is found
    assert any(keyword in result.lower() for keyword in ["5 customers", "five customers"]), f"Result should contain customer-related content: {result}"

def test_complex_query_execution():
    """Test agent can handle a complex query"""
    agent = NorthwindAgent()
    result = agent.ask("Show me orders for customer FAPSM with their product details")
    assert result is not None
    # Check for expected content - either successful data or meaningful "no results" message
    expected_content = ["fapsm", "order id", "product", "quantity", "no orders found", "no results"]
    assert any(keyword in result.lower() for keyword in expected_content), f"Result should contain relevant content: {result}"

def test_schema_tools_get_tables():
    """Test agent can use the schema discovery tool to list tables"""
    agent = NorthwindAgent()
    result = agent.ask("What tables are available in the database?")
    
    # Basic validations
    assert result is not None, "Result should not be None"
    assert isinstance(result, str), "Result should be a string response"
    assert len(result.strip()) > 0, "Result should not be empty"
    
    # Check for successful execution (no errors)
    result_lower = result.lower()
    error_patterns = ["error", "failed", "exception", "tuple index out of range"]
    for pattern in error_patterns:
        assert pattern not in result_lower, f"Result contains error pattern '{pattern}': {result}"
    
    # Check for table listing content
    success_indicators = ["customer", "orderdetail", "product", "employee", "category"]
    assert any(indicator in result_lower for indicator in success_indicators), f"Result should contain table information: {result}"

def test_schema_tools_get_columns():
    """Test agent can get column information for tables"""
    agent = NorthwindAgent()
    result = agent.ask("What columns are in the customer table?")
    
    # Basic validations
    assert result is not None, "Result should not be None"
    assert isinstance(result, str), "Result should be a string response"
    assert len(result.strip()) > 0, "Result should not be empty"
    
    # Check for successful execution (no errors)
    result_lower = result.lower()
    error_patterns = ["error", "failed", "exception", "tuple index out of range"]
    for pattern in error_patterns:
        assert pattern not in result_lower, f"Result contains error pattern '{pattern}': {result}"
    
    # Check for column information content
    success_indicators = ["custid", "companyname", "address", "city"]
    assert any(indicator in result_lower for indicator in success_indicators), f"Result should contain column information: {result}"

def test_sales_report_tool():
    """Test agent can use the sales_report tool"""
    agent = NorthwindAgent()
    result = agent.ask("Generate a sales report for August 2006")
    
    # Basic validations
    assert result is not None, "Result should not be None"
    assert isinstance(result, str), "Result should be a string response"
    assert len(result.strip()) > 0, "Result should not be empty"
    
    # Check for successful execution (no errors)
    result_lower = result.lower()
    error_patterns = ["error", "failed", "exception", "tuple index out of range"]
    for pattern in error_patterns:
        assert pattern not in result_lower, f"Result contains error pattern '{pattern}': {result}"
    
    # Check for sales report content
    success_indicators = ["sales", "report", "order", "total", "revenue", "product", "amount"]
    assert any(indicator in result_lower for indicator in success_indicators), f"Result should contain sales report content: {result}"
    
    # Ensure substantial response
    assert len(result.strip()) > 50, f"Sales report result seems too brief: {result}"

def test_customer_orders_tool():
    """Test agent can use the customer_orders tool"""
    agent = NorthwindAgent()
    result = agent.ask("Show me customer orders report for customer FAPSM")
    
    # Basic validations
    assert result is not None, "Result should not be None"
    assert isinstance(result, str), "Result should be a string response"
    assert len(result.strip()) > 0, "Result should not be empty"
    
    # Check for successful execution (no errors)
    result_lower = result.lower()
    error_patterns = ["error", "failed", "exception", "tuple index out of range"]
    for pattern in error_patterns:
        assert pattern not in result_lower, f"Result contains error pattern '{pattern}': {result}"
    
    # Check for customer orders content
    success_indicators = ["customer", "orders", "company", "order", "total", "custid"]
    assert any(indicator in result_lower for indicator in success_indicators), f"Result should contain customer orders content: {result}"
    
    # Ensure substantial response
    assert len(result.strip()) > 50, f"Customer orders result seems too brief: {result}"

