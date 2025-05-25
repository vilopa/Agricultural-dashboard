import sqlite3

DB_PATH = 'agricultural_data.db'
TABLE_NAME = 'Agricultural_Production_Data'

try:
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = cursor.fetchall()
    
    print(f"Columns in {TABLE_NAME}:")
    for col in columns:
        # col_id, name, type, notnull, default_value, pk
        print(f"- {col[1]} (Type: {col[2]})")
    
    # Get a sample row
    cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 1")
    sample = cursor.fetchone()
    
    if sample:
        print("\nSample row:")
        for i, col in enumerate(columns):
            print(f"{col[1]}: {sample[i]}")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}") 