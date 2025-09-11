from database import check_connection

def test_database_connection():
    """Test if we can connect to the database"""
    result = check_connection()
    assert result, "Database connection failed"

# We'll add more tests here as we build features:
# def test_query_execution():
# def test_report_generation():
# def test_mcp_tools():