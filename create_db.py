import sqlite3
import pandas as pd
import os

# Database configuration
DB_PATH = 'agricultural_data.db'
EXCEL_PATH = 'final_combined_dashboard_data_with_flags_cleaned.xlsx'
TABLE_NAME = 'Agricultural_Production_Data'

def create_database():
    """Create a new SQLite database with table from Excel data."""
    try:
        # Check if Excel file exists
        if not os.path.exists(EXCEL_PATH):
            print(f"❌ Excel file not found: {EXCEL_PATH}")
            return False
            
        # Read the Excel file
        print(f"Reading Excel file: {EXCEL_PATH}")
        df = pd.read_excel(EXCEL_PATH)
        print(f"✅ Excel file loaded with {len(df)} rows")
        
        # Print first few columns to verify data
        print("\nFirst 5 columns:")
        for col in list(df.columns)[:5]:
            print(f"- {col}")
        
        # Connect to SQLite database (will create it if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Connected to database: {DB_PATH}")
        
        # Write DataFrame to SQLite table
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        print(f"✅ Data imported to table: {TABLE_NAME}")
        
        # Verify table creation
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = cursor.fetchone()[0]
        print(f"✅ Table created with {count} rows")
        
        # Close connection
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("Creating agricultural database...")
    create_database()
    print("Done!") 