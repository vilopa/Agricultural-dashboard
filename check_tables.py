import sqlite3

# Path to your SQLite database file
DB_PATH = 'DBeaverSampleDatabase.db'

try:
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query to get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if tables:
        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("No tables found in the database.")
        
    # Close the connection
    conn.close()
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}") 