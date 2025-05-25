import pandas as pd

EXCEL_PATH = 'final_combined_dashboard_data_with_flags_cleaned.xlsx'

try:
    # Open the Excel file to see all sheets
    print(f"Reading Excel file: {EXCEL_PATH}")
    excel_file = pd.ExcelFile(EXCEL_PATH)
    
    # List all sheet names
    sheet_names = excel_file.sheet_names
    
    print(f"\nFound {len(sheet_names)} sheets in the Excel file:")
    for i, sheet in enumerate(sheet_names, 1):
        # Get a sample of rows to see data size
        df_sample = pd.read_excel(EXCEL_PATH, sheet_name=sheet, nrows=5)
        rows_estimate = len(pd.read_excel(EXCEL_PATH, sheet_name=sheet, nrows=1000))
        if rows_estimate >= 1000:
            rows_txt = "1000+ rows"
        else:
            rows_txt = f"{rows_estimate} rows"
            
        print(f"{i}. {sheet} ({rows_txt}, {len(df_sample.columns)} columns)")
        
        # Show column names for each sheet
        print("   Columns: " + ", ".join(df_sample.columns[:5]) + 
              ("..." if len(df_sample.columns) > 5 else ""))
    
except Exception as e:
    print(f"Error reading Excel file: {e}") 