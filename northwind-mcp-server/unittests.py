from database import (
    check_connection, 
    get_tables, 
    get_table_columns, 
    sales_report, 
    customer_orders, 
    execute_query
)
from service import query_database, get_schema_tables, get_schema_table_columns

###
# Database tests (database.py functions)
###

# Basic connection test
def test_database_connection():
    """Test if we can connect to the database"""
    result = check_connection()
    assert result, "Database connection failed"

# Schema tests
def test_get_tables():
    """Test getting list of tables"""
    result = get_tables()
    assert result["success"], f"Failed to get tables: {result.get('error', '')}"
    assert len(result["rows"]) > 0, "No tables found in database"
    
    # Check if we have expected Northwind tables
    table_names = [row[0] for row in result["rows"]]
    expected_tables = ["customer", "employee", "product", "salesorder"]
    for table in expected_tables:
        assert table in table_names, f"Expected table '{table}' not found"

def test_get_table_columns():
    """Test getting columns for a specific table"""
    # Test with customer table
    result = get_table_columns("customer")
    assert result["success"], f"Failed to get columns: {result.get('error', '')}"
    assert len(result["rows"]) > 0, "No columns found for customer table"

def test_get_invalid_table_columns():
    """Test getting columns for a non-existent table"""
    result = get_table_columns("non_existent_table")
    assert not result["success"], "Expected failure for non-existent table"
    assert "The table does not exist" in result["error"], "Should indicate table does not exist"

# Report tests
def test_sales_report():
    """Test sales report generation"""
    result = sales_report()
    assert result["success"], f"Sales report failed: {result.get('error', '')}"   
    assert "rows" in result, "Sales report should return rows"

def test_sales_report_with_dates():
    """Test sales report with date filters"""
    result = sales_report("1996-01-01", "1996-12-31")
    assert result["success"], f"Sales report with dates failed: {result.get('error', '')}"
    assert "rows" in result, "Sales report should return rows"

def test_customer_orders():
    """Test customer orders report"""
    result = customer_orders()
    assert result["success"], f"Customer orders failed: {result.get('error', '')}"
    assert "rows" in result, "Customer orders should return rows"

def test_customer_orders_specific():
    """Test customer orders for specific customer"""
    # Using string customer ID since custid in salesorder table is string
    result = customer_orders("1")  # Using customer ID "1" as string
    assert result["success"], f"Specific customer orders failed: {result.get('error', '')}"
    assert "rows" in result, "Customer orders should return rows"

# Generic query tests
def test_execute_query_select():
    """Test executing a simple SELECT query"""
    result = execute_query("SELECT 1 as test_column")
    assert result["success"], f"Simple SELECT failed: {result.get('error', '')}"
    assert result["rows"][0][0] == 1, "SELECT 1 should return 1"

def test_execute_query_security():
    """Test that non-SELECT queries are blocked"""
    result = execute_query("INSERT INTO customer (custid) VALUES (999)")
    assert not result["success"], "INSERT should be blocked"
    assert "Only SELECT queries are allowed" in result["error"], "Should show security error"
    
    result = execute_query("UPDATE customer SET companyname = 'test'")
    assert not result["success"], "UPDATE should be blocked"
    
    result = execute_query("DELETE FROM customer")
    assert not result["success"], "DELETE should be blocked"

def test_execute_query_invalid_sql():
    """Test handling of invalid SQL"""
    result = execute_query("SELECT * FROM non_existent_table")
    assert not result["success"], "Invalid SQL should fail"
    assert "error" in result, "Should return error message"



###
# Service tests (service.py functions)  
###

#query tests
def test_query_function():
    """Test the query_database function"""
    # Test successful query
    result = query_database("SELECT 1 as test_column")
    assert result["status"] == "success", f"Query function failed: {result}"
    assert result["row_count"] == 1, "Should return 1 row"
    assert result["rows"][0][0] == 1, "Should return value 1"

def test_query_function_security():
    """Test query_database function blocks non-SELECT queries"""
    result = query_database("INSERT INTO customer (custid) VALUES (999)")
    assert result["status"] == "error", "INSERT should be blocked"
    assert "Only SELECT queries are allowed" in result["error"], "Should show security error"

def test_query_function_invalid():
    """Test query_database function with invalid SQL"""
    result = query_database("SELECT * FROM non_existent_table")
    assert result["status"] == "error", "Invalid SQL should return error"


# Schema tests
def test_schema_tables_function():
    """Test the get_schema_tables function"""
    result = get_schema_tables()
    assert result["status"] == "success", f"Schema tables function failed: {result}"
    assert "tables" in result, "Should return tables list"
    assert result["count"] > 0, "Should find some tables"

def test_schema_columns_function():
    """Test the get_schema_columns function"""
    result = get_schema_table_columns("customer")
    assert result["status"] == "success", f"Schema columns function failed: {result}"
    assert result["table"] == "customer", "Should return correct table name"
    assert "columns" in result, "Should return columns list"
    assert result["count"] > 0, "Should find some columns"