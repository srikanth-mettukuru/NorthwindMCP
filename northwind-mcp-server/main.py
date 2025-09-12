import asyncio
from fastmcp import FastMCP
from service import query_database, get_schema_tables, get_schema_table_columns
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Northwind Database Server")


# Create a MCP tool to execute arbitrary SQL queries
   # MCP Clients see:
     # Tool: query                                                        (Since we named the tool "query")
     # Description: Execute a SQL query against the Northwind database.   (FastMCP automatically uses the first line of the function's docstring as the tool description.)
     # Parameters:                                                        (FastMCP reads the 'Args' section to understand parameters)
     #   - sql (str): The SQL SELECT query to execute

@mcp.tool(name="query")  # Tool name exposed to clients as "query"
def query_tool(sql: str) -> dict:           # MCP tool function wraps the Python function
    """
    Execute a SQL query against the Northwind database.
    
    Args:
        sql: The SQL SELECT query to execute            
        
    Returns:
        Dictionary with query results including columns and rows
    """
    return query_database(sql)


# Create a MCP tool to get database schema tables
@mcp.tool(name="get_tables")
def tables_tool() -> dict:
    """
    Get list of all tables in the Northwind database.
    
    Returns:
        Dictionary with list of table names
    """
    return get_schema_tables()


# Create a MCP tool to get columns for a specific table
@mcp.tool(name="get_columns") 
def columns_tool(table_name: str) -> dict:
    """
    Get column information for a specific table.
    
    Args:
        table_name: Name of the table to inspect
        
    Returns:
        Dictionary with column details including names, types, and constraints
    """
    return get_schema_table_columns(table_name)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()