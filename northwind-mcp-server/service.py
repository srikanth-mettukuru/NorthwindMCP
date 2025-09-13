from database import execute_query, get_tables, get_table_columns, sales_report, customer_orders
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


def generate_sales_report(start_date: str = None, end_date: str = None) -> dict:
    """
    Generate a sales report with optional date filtering.
    
    Args:
        start_date: Start date for filtering (YYYY-MM-DD format)
        end_date: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        Dictionary with sales report data
    """
    try:
        logger.info(f"Generating sales report from {start_date} to {end_date}")
        result = sales_report(start_date, end_date)

        if result["success"]:
            # Format the report data for better presentation
            report_data = []
            for row in result["rows"]:
                report_data.append({
                    "order_id": row[0],
                    "order_date": str(row[1]),
                    "company_name": row[2],
                    "total_amount": float(row[3])
                })
            
            logger.info(f"Sales report generated with {len(report_data)} records")
            return {
                "status": "success",
                "report_type": "sales_report",
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "data": report_data,
                "record_count": len(report_data)
            }
        else:
            logger.error(f"Failed to generate sales report: {result['error']}")
            return {
                "status": "error",
                "error": result["error"]
            }

    except Exception as e:
        logger.error(f"Unexpected error generating sales report: {str(e)}")
        return {
            "status": "error", 
            "error": f"Unexpected error: {str(e)}"
        }


def generate_customer_orders_report(customer_id: str = None) -> dict:
    """
    Generate a customer orders report.
    
    Args:
        customer_id: Specific customer ID to filter by (optional)
        
    Returns:
        Dictionary with customer orders data
    """
    try:
        logger.info(f"Generating customer orders report for customer: {customer_id}")
        result = customer_orders(customer_id)

        if result["success"]:
            # Format the report data for better presentation
            report_data = []
            for row in result["rows"]:
                report_data.append({
                    "company_name": row[0],
                    "order_id": row[1],
                    "order_date": str(row[2]) if row[2] else None,
                    "order_total": float(row[3]) if row[3] else 0.0
                })
            
            logger.info(f"Customer orders report generated with {len(report_data)} records")
            return {
                "status": "success",
                "report_type": "customer_orders",
                "customer_filter": customer_id,
                "data": report_data,
                "record_count": len(report_data)
            }
        else:
            logger.error(f"Failed to generate customer orders report: {result['error']}")
            return {
                "status": "error",
                "error": result["error"]
            }
    
    except Exception as e:
        logger.error(f"Unexpected error generating customer orders report: {str(e)}")
        return {
            "status": "error", 
            "error": f"Unexpected error: {str(e)}"
        }