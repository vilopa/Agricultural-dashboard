from flask import Flask, render_template, jsonify, request
import pandas as pd
import sqlite3
import os
import json
import numpy as np
from datetime import datetime

app = Flask(__name__, static_folder='static')

# Database configuration
DB_PATH = 'agricultural_data.db'

def connect_db():
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def load_data(query):
    """Load data from SQLite database."""
    try:
        conn = connect_db()
        if conn is None:
            return None
            
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

@app.route('/')
def home():
    # Get total record count
    record_count_df = load_data("SELECT COUNT(*) as count FROM Agricultural_Production_Data")
    record_count = record_count_df.iloc[0]['count'] if record_count_df is not None else 0
    
    # Get total value sum
    total_value_df = load_data("SELECT SUM(Value) as total FROM Agricultural_Production_Data")
    total_value = round(float(total_value_df.iloc[0]['total']), 2) if total_value_df is not None else 0
    
    # Get yearly data for chart
    yearly_data_df = load_data("""
        SELECT "Year Id" as Year, SUM(Value) as Production 
        FROM Agricultural_Production_Data 
        GROUP BY "Year Id" 
        ORDER BY "Year Id"
    """)
    
    if yearly_data_df is not None:
        years = yearly_data_df['Year'].tolist()
        production_values = yearly_data_df['Production'].tolist()
    else:
        years = []
        production_values = []
    
    # Get indicators list for filter
    indicators_df = load_data("SELECT * FROM Indicator")
    indicators = indicators_df.to_dict('records') if indicators_df is not None else []
    
    # Get areas list for filter
    areas_df = load_data("SELECT * FROM Area")
    areas = areas_df.to_dict('records') if areas_df is not None else []
    
    return render_template('index.html', 
                           record_count=record_count, 
                           total_value=total_value,
                           years=years,
                           production_values=production_values,
                           indicators=indicators,
                           areas=areas)

@app.route('/strategic')
def strategic_dashboard():
    """Strategic dashboard focused on long-term trends and high-level metrics."""
    
    # Get year range
    year_range_df = load_data("""
        SELECT MIN("Year Id") as min_year, MAX("Year Id") as max_year 
        FROM Agricultural_Production_Data
    """)
    
    year_range = {}
    if year_range_df is not None:
        year_range = {
            'min': int(year_range_df.iloc[0]['min_year']),
            'max': int(year_range_df.iloc[0]['max_year'])
        }
    
    # Get long-term production trend by year
    trend_df = load_data("""
        SELECT "Year Id" as year, SUM(Value) as total_production
        FROM Agricultural_Production_Data
        GROUP BY "Year Id"
        ORDER BY "Year Id"
    """)
    
    # Calculate year-over-year growth rates
    if trend_df is not None and len(trend_df) > 1:
        trend_df['growth_rate'] = trend_df['total_production'].pct_change() * 100
        trend_df['growth_rate'] = trend_df['growth_rate'].fillna(0)
        
        # Calculate 3-year moving average for smoothing trends
        trend_df['moving_avg'] = trend_df['total_production'].rolling(window=3, min_periods=1).mean()
        
        trend_data = {
            'years': trend_df['year'].tolist(),
            'production': trend_df['total_production'].tolist(),
            'growth_rates': trend_df['growth_rate'].round(2).tolist(),
            'moving_avg': trend_df['moving_avg'].tolist()
        }
    else:
        trend_data = {'years': [], 'production': [], 'growth_rates': [], 'moving_avg': []}
    
    # Get regional breakdown
    region_df = load_data("""
        SELECT er."European Region" as region, SUM(apd.Value) as total_production
        FROM Agricultural_Production_Data apd
        JOIN Area a ON apd.AreaID = a.AreaID
        JOIN european_region_ er ON a." Region  id" = er." Region  id"
        WHERE er."European Region" IS NOT NULL
        GROUP BY er."European Region"
        ORDER BY total_production DESC
    """)
    
    if region_df is not None:
        region_data = {
            'regions': region_df['region'].tolist(),
            'production': region_df['total_production'].tolist()
        }
    else:
        region_data = {'regions': [], 'production': []}
    
    # Get top-performing items
    item_df = load_data("""
        SELECT it.Item, ic.Category, SUM(apd.Value) as total_production
        FROM Agricultural_Production_Data apd
        JOIN item it ON apd."Item Code (CPC)" = it."Item Code (CPC)"
        JOIN Item_Category ic ON it."Category ID" = ic."Category ID"
        GROUP BY it.Item, ic.Category
        ORDER BY total_production DESC
        LIMIT 10
    """)
    
    if item_df is not None:
        item_data = {
            'items': item_df['Item'].tolist(),
            'categories': item_df['Category'].tolist(),
            'production': item_df['total_production'].tolist()
        }
    else:
        item_data = {'items': [], 'categories': [], 'production': []}
    
    # Get key performance indicators
    kpi_data = {}
    
    # 1. Total production
    total_prod_df = load_data("SELECT SUM(Value) as total FROM Agricultural_Production_Data")
    if total_prod_df is not None:
        kpi_data['total_production'] = round(float(total_prod_df.iloc[0]['total']), 2)
    
    # 2. Average annual growth rate
    if trend_df is not None and len(trend_df) > 1:
        kpi_data['avg_growth_rate'] = round(trend_df['growth_rate'].mean(), 2)
    else:
        kpi_data['avg_growth_rate'] = 0
    
    # 3. Production concentration (% in top 5 areas)
    top_areas_prod_df = load_data("""
        SELECT SUM(Value) as top_prod
        FROM (
            SELECT AreaID, SUM(Value) as Value
            FROM Agricultural_Production_Data
            GROUP BY AreaID
            ORDER BY Value DESC
            LIMIT 5
        )
    """)
    
    if total_prod_df is not None and top_areas_prod_df is not None:
        total_prod = float(total_prod_df.iloc[0]['total'])
        top_prod = float(top_areas_prod_df.iloc[0]['top_prod'])
        if total_prod > 0:
            kpi_data['top5_concentration'] = round((top_prod / total_prod) * 100, 2)
        else:
            kpi_data['top5_concentration'] = 0
    else:
        kpi_data['top5_concentration'] = 0
    
    # 4. Diversity index (number of different items produced)
    diversity_df = load_data("""
        SELECT COUNT(DISTINCT "Item Code (CPC)") as diversity
        FROM Agricultural_Production_Data
    """)
    
    if diversity_df is not None:
        kpi_data['diversity_index'] = int(diversity_df.iloc[0]['diversity'])
    
    # Get category distribution
    category_df = load_data("""
        SELECT ic.Category, SUM(apd.Value) as total_production
        FROM Agricultural_Production_Data apd
        JOIN item it ON apd."Item Code (CPC)" = it."Item Code (CPC)"
        JOIN Item_Category ic ON it."Category ID" = ic."Category ID"
        GROUP BY ic.Category
        ORDER BY total_production DESC
    """)
    
    if category_df is not None:
        category_data = {
            'categories': category_df['Category'].tolist(),
            'production': category_df['total_production'].tolist()
        }
    else:
        category_data = {'categories': [], 'production': []}
    
    return render_template('strategic.html', 
                           year_range=year_range,
                           trend_data=trend_data,
                           region_data=region_data,
                           item_data=item_data,
                           kpi_data=kpi_data,
                           category_data=category_data)

@app.route('/api/dashboard_data')
def dashboard_data():
    result = {}
    
    # Get record count
    record_count_df = load_data("SELECT COUNT(*) as count FROM Agricultural_Production_Data")
    if record_count_df is not None:
        result['record_count'] = int(record_count_df.iloc[0]['count'])
    
    # Get total value
    total_value_df = load_data("SELECT SUM(Value) as total FROM Agricultural_Production_Data")
    if total_value_df is not None:
        result['total_value'] = round(float(total_value_df.iloc[0]['total']), 2)
    
    # Get yearly data
    yearly_data_df = load_data("""
        SELECT "Year Id" as Year, SUM(Value) as Production 
        FROM Agricultural_Production_Data 
        GROUP BY "Year Id" 
        ORDER BY "Year Id"
    """)
    
    if yearly_data_df is not None:
        result['years'] = yearly_data_df['Year'].tolist()
        result['production_values'] = yearly_data_df['Production'].tolist()
    
    # Get top areas by production
    top_areas_df = load_data("""
        SELECT apd.AreaID, a.Area as AreaName, SUM(apd.Value) as Total 
        FROM Agricultural_Production_Data apd
        JOIN Area a ON apd.AreaID = a.AreaID
        GROUP BY apd.AreaID, a.Area
        ORDER BY Total DESC 
        LIMIT 5
    """)
    
    if top_areas_df is not None:
        result['top_areas'] = {
            'labels': top_areas_df['AreaName'].tolist(),
            'values': top_areas_df['Total'].tolist()
        }
    
    # Get indicator distribution
    indicator_df = load_data("""
        SELECT i.Indicator, SUM(apd.Value) as Total
        FROM Agricultural_Production_Data apd
        JOIN Indicator i ON apd."Indicator Code" = i."Indicator Code"
        GROUP BY i.Indicator
        ORDER BY Total DESC
    """)
    
    if indicator_df is not None:
        result['indicators'] = {
            'labels': indicator_df['Indicator'].tolist(),
            'values': indicator_df['Total'].tolist()
        }
    
    return jsonify(result)

@app.route('/api/strategic_data')
def strategic_data():
    """API endpoint for strategic dashboard data."""
    
    # Get production trend by year with 5-year forecast
    trend_df = load_data("""
        SELECT "Year Id" as year, SUM(Value) as total_production
        FROM Agricultural_Production_Data
        GROUP BY "Year Id"
        ORDER BY "Year Id"
    """)
    
    result = {}
    
    if trend_df is not None and len(trend_df) > 1:
        # Calculate growth rates
        trend_df['growth_rate'] = trend_df['total_production'].pct_change() * 100
        trend_df['growth_rate'] = trend_df['growth_rate'].fillna(0)
        
        # Calculate moving average
        trend_df['moving_avg'] = trend_df['total_production'].rolling(window=3, min_periods=1).mean()
        
        # Simple forecast for next 5 years
        last_year = trend_df['year'].max()
        last_value = trend_df.loc[trend_df['year'] == last_year, 'total_production'].values[0]
        avg_growth = trend_df['growth_rate'].tail(5).mean() / 100  # Last 5 years average growth rate
        
        forecast_years = list(range(last_year + 1, last_year + 6))
        forecast_values = []
        current_value = last_value
        
        for _ in range(5):
            current_value = current_value * (1 + avg_growth)
            forecast_values.append(round(current_value, 2))
        
        result['trend'] = {
            'years': trend_df['year'].tolist(),
            'production': trend_df['total_production'].tolist(),
            'growth_rates': trend_df['growth_rate'].round(2).tolist(),
            'moving_avg': trend_df['moving_avg'].tolist(),
            'forecast_years': forecast_years,
            'forecast_values': forecast_values
        }
    
    # Get production by region with year-over-year comparison
    region_yearly_df = load_data("""
        SELECT er."European Region" as region, apd."Year Id" as year, SUM(apd.Value) as total_production
        FROM Agricultural_Production_Data apd
        JOIN Area a ON apd.AreaID = a.AreaID
        JOIN european_region_ er ON a." Region  id" = er." Region  id"
        WHERE er."European Region" IS NOT NULL
        GROUP BY er."European Region", apd."Year Id"
        ORDER BY er."European Region", apd."Year Id"
    """)
    
    if region_yearly_df is not None:
        # Pivot the data to get regions as columns and years as rows
        pivot_df = region_yearly_df.pivot(index='year', columns='region', values='total_production')
        
        result['region_yearly'] = {
            'years': pivot_df.index.tolist(),
            'regions': pivot_df.columns.tolist(),
            'data': pivot_df.values.tolist()
        }
    
    return jsonify(result)

@app.route('/api/query')
def execute_query():
    """Execute a custom SQL query."""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "No query provided"})
    
    # Basic security check - only allow SELECT queries
    if not query.strip().upper().startswith('SELECT'):
        return jsonify({"error": "Only SELECT queries are allowed"})
    
    try:
        df = load_data(query)
        if df is not None:
            return jsonify(df.to_dict('records'))
        return jsonify({"error": "Failed to execute query"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/items')
def get_items():
    items_df = load_data("""
        SELECT i.*, ic.Category
        FROM item i
        JOIN Item_Category ic ON i."Category ID" = ic."Category ID"
    """)
    
    if items_df is not None:
        return jsonify(items_df.to_dict('records'))
    return jsonify([])

@app.route('/api/areas')
def get_areas():
    areas_df = load_data("""
        SELECT a.*, er.* 
        FROM Area a
        LEFT JOIN european_region_ er ON a." Region  id" = er." Region  id"
    """)
    
    if areas_df is not None:
        return jsonify(areas_df.to_dict('records'))
    return jsonify([])

@app.route('/api/data_by_area/<int:area_id>')
def get_data_by_area(area_id):
    data_df = load_data(f"""
        SELECT apd.*, i.Indicator, it."Item", y.Year as YearDate
        FROM Agricultural_Production_Data apd
        JOIN Indicator i ON apd."Indicator Code" = i."Indicator Code"
        JOIN item it ON apd."Item Code (CPC)" = it."Item Code (CPC)"
        JOIN Year y ON apd."Year Id" = y."Year_ID"
        WHERE apd.AreaID = {area_id}
        ORDER BY apd."Year Id"
    """)
    
    if data_df is not None:
        return jsonify(data_df.to_dict('records'))
    return jsonify([])

@app.route('/api/tables')
def get_tables():
    """Get information about all tables in the database."""
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Could not connect to database"})
            
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        result = {}
        for table in tables:
            # Get column information
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns = [{"name": col[1], "type": col[2]} for col in cursor.fetchall()]
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
            row_count = cursor.fetchone()[0]
            
            result[table] = {
                "columns": columns,
                "row_count": row_count
            }
            
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
