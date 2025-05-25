import pandas as pd
import sqlite3
import os
import re

# Configuration
EXCEL_PATH = 'final_combined_dashboard_data_with_flags_cleaned.xlsx'
DB_PATH = 'agricultural_data.db'

def clean_table_name(name):
    """Convert sheet name to valid SQL table name."""
    # Replace spaces and special chars with underscore
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Remove leading numbers or underscore
    clean_name = re.sub(r'^[0-9_]+', '', clean_name)
    # Ensure name is not empty
    if not clean_name:
        clean_name = 'table'
    return clean_name

def import_sheets_to_db():
    """Import all sheets from Excel file to SQLite database."""
    try:
        # Check if Excel file exists
        if not os.path.exists(EXCEL_PATH):
            print(f"❌ Excel file not found: {EXCEL_PATH}")
            return False
            
        # Open the Excel file
        print(f"Reading Excel file: {EXCEL_PATH}")
        excel_file = pd.ExcelFile(EXCEL_PATH)
        sheet_names = excel_file.sheet_names
        
        # Connect to SQLite database
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Connected to database: {DB_PATH}")
        
        # Get existing tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [table[0] for table in cursor.fetchall()]
        print(f"Found {len(existing_tables)} existing tables in the database")
        
        # Import each sheet
        print(f"\nImporting {len(sheet_names)} sheets to database...")
        for sheet in sheet_names:
            # Create a valid table name
            table_name = clean_table_name(sheet)
            
            # Read the sheet
            try:
                df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
                rows = len(df)
                cols = len(df.columns)
                
                # Skip empty sheets
                if rows == 0 or cols == 0:
                    print(f"⚠️ Skipping empty sheet: {sheet}")
                    continue
                
                print(f"\nProcessing sheet: {sheet} → table: {table_name} ({rows} rows, {cols} columns)")
                
                # If table already exists, ask for confirmation to replace
                if table_name in existing_tables:
                    print(f"⚠️ Table '{table_name}' already exists - replacing")
                
                # Import the data
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"✅ Imported sheet '{sheet}' to table '{table_name}' successfully")
                
            except Exception as e:
                print(f"❌ Error importing sheet {sheet}: {e}")
        
        # Close connection
        conn.close()
        print("\n✅ All sheets imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error importing Excel sheets: {e}")
        return False

def list_database_tables():
    """List all tables in the database with their row counts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\nDatabase '{DB_PATH}' contains {len(tables)} tables:")
        for i, table in enumerate(tables, 1):
            table_name = table[0]
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
            row_count = cursor.fetchone()[0]
            
            # Get column count
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            col_count = len(cursor.fetchall())
            
            print(f"{i}. {table_name} ({row_count} rows, {col_count} columns)")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"❌ Error listing tables: {e}")

if __name__ == "__main__":
    print("===== IMPORTING ALL EXCEL SHEETS TO DATABASE =====")
    if import_sheets_to_db():
        list_database_tables()
        print("\nDone! All sheets have been imported to the database.") 