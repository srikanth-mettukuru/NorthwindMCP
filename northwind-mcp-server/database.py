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
