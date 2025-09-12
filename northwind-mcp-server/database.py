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

# SCHEMA TOOLS
def get_tables():
    """Get list of all tables"""
    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    return execute_query(sql)

def get_table_columns(table_name):
    """Get columns for a specific table"""
    sql = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = %s AND table_schema = 'public'
    ORDER BY ordinal_position
    """
    return execute_query(sql, [table_name])


# REPORT TOOLS
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
    
    sql += " GROUP BY so.orderid, so.orderdate, c.companyname ORDER BY so.orderdate DESC LIMIT 100"
    
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

    sql += " GROUP BY c.companyname, so.orderid, so.orderdate ORDER BY so.orderdate DESC LIMIT 50"

    return execute_query(sql, params)


# GENERIC QUERY EXECUTION
def execute_query(sql, params=None):
    """Execute SELECT queries only and return results"""
    try:
        # Security check - only allow SELECT queries
        if not sql.strip().upper().startswith('SELECT'):
            return {"success": False, "error": "Only SELECT queries are allowed"}
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return {"success": True, "columns": columns, "rows": rows}
            
    except Exception as e:
        return {"success": False, "error": str(e)}