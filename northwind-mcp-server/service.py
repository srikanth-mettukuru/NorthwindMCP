from database import execute_query, get_tables, get_table_columns
import logging

logger = logging.getLogger(__name__)

def query_database(sql: str) -> dict:
    """
    Execute a SQL query against the Northwind database.
    
    Args:
        sql: The SQL SELECT query to execute            
        
    Returns:
        Dictionary with query results including columns and rows
    """
    try:
        logger.info(f"Executing query: {sql}")
        result = execute_query(sql)
        
        if result["success"]:
            logger.info(f"Query successful, returned {len(result['rows'])} rows")
            return {
                "status": "success",
                "columns": result["columns"],
                "rows": result["rows"],
                "row_count": len(result["rows"])
            }
        else:
            logger.error(f"Query failed: {result['error']}")
            return {
                "status": "error",
                "error": result["error"]
            }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error", 
            "error": f"Unexpected error: {str(e)}"
        }
    


def get_schema_tables() -> dict:
    """
    Get list of all tables in the database schema.
    
    Returns:
        Dictionary with table information
    """
    try:
        logger.info("Getting database tables")
        result = get_tables()
        
        if result["success"]:
            logger.info(f"Found {len(result['rows'])} tables")
            return {
                "status": "success",
                "tables": [row[0] for row in result["rows"]],
                "count": len(result["rows"])
            }
        else:
            logger.error(f"Failed to get tables: {result['error']}")
            return {
                "status": "error",
                "error": result["error"]
            }
            
    except Exception as e:
        logger.error(f"Unexpected error getting tables: {str(e)}")
        return {
            "status": "error", 
            "error": f"Unexpected error: {str(e)}"
        }


def get_schema_table_columns(table_name: str) -> dict:
    """
    Get columns for a specific table.
    
    Args:
        table_name: Name of the table to inspect
        
    Returns:
        Dictionary with column information
    """
    try:
        logger.info(f"Getting columns for table: {table_name}")
        result = get_table_columns(table_name)
        
        if result["success"]:
            columns_info = []
            for row in result["rows"]:
                columns_info.append({
                    "name": row[0],
                    "type": row[1], 
                    "nullable": row[2],
                    "default": row[3]
                })
            
            logger.info(f"Found {len(columns_info)} columns for {table_name}")
            return {
                "status": "success",
                "table": table_name,
                "columns": columns_info,
                "count": len(columns_info)
            }
        else:
            logger.error(f"Failed to get columns for {table_name}: {result['error']}")
            return {
                "status": "error",
                "error": result["error"]
            }
            
    except Exception as e:
        logger.error(f"Unexpected error getting columns for {table_name}: {str(e)}")
        return {
            "status": "error", 
            "error": f"Unexpected error: {str(e)}"
        }
