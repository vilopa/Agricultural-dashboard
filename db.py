import sqlite3
import pandas as pd

# Path to your SQLite database file
DB_PATH = 'agricultural_data.db'

def connect_db():
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        print("✅ Connected to SQLite database successfully.")
        return conn
    except sqlite3.Error as e:
        print("❌ Failed to connect to database:", e)
        return None

def select_all_data():
    """Select all data from Agricultural_Production_Data."""
    try:
        conn = connect_db()
        if conn is None:
            return None

        query = "SELECT * FROM Agricultural_Production_Data LIMIT 10"
        df = pd.read_sql_query(query, conn)
        conn.close()

        print(f"✅ Retrieved data successfully. Total rows: {len(df)}")
        return df

    except Exception as e:
        print("❌ Error retrieving data:", e)
        return None

def select_column_names():
    """Get the column names from the table."""
    try:
        conn = connect_db()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Agricultural_Production_Data)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        return column_names
        
    except Exception as e:
        print("❌ Error retrieving column names:", e)
        return None

# Example usage:
print("\nRetrieving column names:")
columns = select_column_names()
if columns:
    print("Table columns:")
    for col in columns:
        print(f"- {col}")

print("\nRetrieving data sample:")
df = select_all_data()
if df is not None:
    print("\nFirst 5 rows:")
    print(df.head(5))
