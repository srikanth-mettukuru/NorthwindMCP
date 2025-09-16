import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Get a simple database connection"""
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def check_connection():
    """Test if database connection works"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1") # Send "SELECT 1" to database, the result (1,) is stored in the cursor
        result = cursor.fetchone() # Get the result: (1,)
        conn.close()
        return result[0] == 1   # Check if first element equals 1
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# SCHEMA
def get_tables():
    """Get list of all tables"""
    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    return execute_query(sql)

def get_table_columns(table_name):
    """Get columns for a specific table"""

    # First, validate that the table exists
    tables_result = get_tables()
    if not tables_result["success"]:
        return {"success": False, "error": f"Failed to check if table exists: {tables_result['error']}"}
    
    # Extract table names from the result
    existing_tables = [row[0] for row in tables_result["rows"]]
    
    # Check if the requested table exists
    if table_name not in existing_tables:
        return {"success": False, "error": "The table does not exist"}
    
    # If table exists, proceed with getting columns
    sql = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = %s AND table_schema = 'public'
    ORDER BY ordinal_position
    """
    return execute_query(sql, [table_name])


# REPORT
def sales_report(start_date=None, end_date=None):
    """Generate sales report"""
    sql = """
    SELECT so.orderid, so.orderdate, c.companyname, 
           SUM(od.unitprice * od.qty) as total_amount
    FROM salesorder so
    JOIN customer c ON so.custid = CAST(c.custid AS VARCHAR)
    JOIN orderdetail od ON so.orderid = od.orderid
    """
    params = []
    
    if start_date and end_date:
        sql += " WHERE so.orderdate BETWEEN %s AND %s"
        params = [start_date, end_date]
    
    sql += " GROUP BY so.orderid, so.orderdate, c.companyname ORDER BY so.orderdate DESC"
    
    return execute_query(sql, params)

def customer_orders(customer_id=None):
    """Get customer orders"""
    sql = """
    SELECT c.companyname, so.orderid, so.orderdate, 
           SUM(od.unitprice * od.qty) as order_total
    FROM customer c
    JOIN salesorder so ON CAST(c.custid AS VARCHAR) = so.custid
    JOIN orderdetail od ON so.orderid = od.orderid
    """
    params = []
    
    if customer_id:
        sql += " WHERE CAST(c.custid AS VARCHAR) = %s"
        params = [str(customer_id)]

    sql += " GROUP BY c.companyname, so.orderid, so.orderdate ORDER BY so.orderdate DESC"

    return execute_query(sql, params)


# GENERIC QUERY EXECUTION
def execute_query(sql, params=None):
    """Execute SELECT queries only and return results"""

    try:
        sql_clean = sql.strip().upper()

        # Security check 1 - only allow SELECT queries
        if not sql_clean.startswith('SELECT'):
            return {"success": False, "error": "Only SELECT queries are allowed"}
        
        # Security check 2 - Block dangerous SQL keywords
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 
            'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', '--', '/*', '*/',
            'DECLARE', 'GRANT', 'REVOKE', 'BACKUP', 'RESTORE'
        ]

        # Security check 3 - Limit query complexity (optional)
        if sql_clean.count('SELECT') > 3:  # Limit nested SELECTs
            return {"success": False, "error": "Query too complex - multiple SELECT statements detected"}
        
        # Security check 4 - Query length limit
        if len(sql) > 5000:  # Reasonable limit for most queries
            return {"success": False, "error": "Query too long - maximum 5000 characters"}
        
        # Security check 5 - Parameter validation
        if params:
            if len(params) > 20:  # Reasonable parameter limit
                return {"success": False, "error": "Too many parameters - maximum 20 allowed"}
            
            # Check for suspicious parameter values
            for param in params:
                if isinstance(param, str):
                    param_upper = param.upper()
                    for keyword in dangerous_keywords:
                        if keyword in param_upper:
                            return {"success": False, "error": f"Suspicious parameter value detected"}
        
        for keyword in dangerous_keywords:
            if keyword in sql_clean:
                return {"success": False, "error": f"Forbidden keyword '{keyword}' detected"}
            
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return {"success": True, "columns": columns, "rows": rows}
            
    except Exception as e:
        return {"success": False, "error": str(e)}