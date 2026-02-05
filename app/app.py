from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from function5_projection import calculate_salary_projections
import os

from relationship_analysis import (
    employment_rate_vs_salary,
    ft_perm_vs_salary,
    load_cleaned_data,
)

app = Flask(__name__, template_folder='../templates')

# Load the full dataset
grouped_data = pd.read_csv('../grouped_salary_analysis.csv')

# Define a function to load different CSV files for each route (if needed)
def load_csv(file_path):
    return pd.read_csv(file_path)

def analyze_trends(university=None, school=None, degree=None, rolling_window=3):
    """Analyze employment and salary trends"""
    df = pd.read_csv('../cleaned.csv')
    
    # Ensure numeric types
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    metrics = ["employment_rate_overall", "employment_rate_ft_perm", "gross_monthly_median"]
    for c in metrics:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    
    # Filter data
    d = df.copy()
    if university:
        d = d[d["university"] == university].copy()
    if school:
        d = d[d["school"] == school].copy()
    if degree:
        d = d[d["degree"] == degree].copy()
    
    if d.empty:
        return None
    
    d = d.sort_values("year")
    d = d.groupby("year", as_index=False)[metrics].mean(numeric_only=True).sort_values("year")
    
    # Compute value-added stats
    for c in metrics:
        d[f"{c}_yoy_abs"] = d[c].diff()
        d[f"{c}_yoy_pct"] = d[c].pct_change(fill_method=None) * 100
        d[f"{c}_ma{rolling_window}"] = d[c].rolling(rolling_window, min_periods=1).mean()
    
    return d

@app.route('/')
def index():
    # Default tab - show overview with CSV preview
    df = load_csv('../cleaned.csv')
    return render_template('index.html', 
                         data=[], 
                         active_tab='overview',
                         universities=[],
                         schools=[],
                         degrees=[],
                         selected_university=None,
                         selected_school=None,
                         selected_degree=None,
                         rolling_window=3)

@app.route('/function1')
def function1():
    # Graduate Employment Trend Analysis
    university = request.args.get('university')
    school = request.args.get('school')
    degree = request.args.get('degree')
    rolling_window = int(request.args.get('rolling_window', 3))
    
    df = load_csv('../cleaned.csv')
    universities = sorted(df['university'].unique())
    schools = []
    degrees = []
    
    if university:
        schools = sorted(df[df['university'] == university]['school'].unique())
        if school:
            degrees = sorted(df[(df['university'] == university) & (df['school'] == school)]['degree'].unique())
        else:
            degrees = sorted(df[df['university'] == university]['degree'].unique())
    
    trend_data = None
    if university:
        trend_data = analyze_trends(university, school, degree, rolling_window)
    
    return render_template('index.html', 
                         data=trend_data.to_dict(orient='records') if trend_data is not None else [],
                         active_tab='tab1',
                         universities=universities,
                         schools=schools,
                         degrees=degrees,
                         selected_university=university,
                         selected_school=school,
                         selected_degree=degree,
                         rolling_window=rolling_window)

@app.route('/function2')
def function2():
    # Load specific CSV for function2
    function2_data = load_csv('../grouped_salary_analysis.csv')

    # Calculate IQR and IQR ratio for this function
    function2_data['IQR'] = function2_data['gross_mthly_75_percentile'] - function2_data['gross_mthly_25_percentile']
    function2_data['IQR_ratio'] = function2_data['IQR'] / function2_data['gross_monthly_median']

    # Get the top 5 entries based on IQR and IQR ratio
    top_iqr = function2_data.nlargest(5, 'IQR')[['degree', 'university', 'year', 'IQR', 'gross_mthly_25_percentile', 'gross_mthly_75_percentile', 'gross_monthly_median']]
    top_iqr_ratio = function2_data.nlargest(5, 'IQR_ratio')[['degree', 'university', 'year', 'IQR_ratio', 'gross_mthly_25_percentile', 'gross_mthly_75_percentile', 'gross_monthly_median']]

    # Extract unique values for degree, university, and year
    unique_degrees = function2_data['degree'].unique()
    unique_universities = function2_data['university'].unique()
    unique_years = function2_data['year'].unique()

    # Render the template with data and active tab as 'tab2'
    return render_template(
        'index.html', 
        data=function2_data.to_dict(orient='records'),
        top_iqr=top_iqr.to_dict(orient='records'),
        top_iqr_ratio=top_iqr_ratio.to_dict(orient='records'),
        active_tab='tab2',
        degrees=unique_degrees,
        universities=unique_universities,
        schools=[],
        selected_university=None,
        selected_school=None,
        selected_degree=None,
        rolling_window=3,
        years=unique_years
    )

@app.route('/function3')
def function3():
    # If function3 needs different data, load a different CSV
    function3_data = load_csv('../cleaned.csv')
    return render_template('index.html', 
                         data=function3_data.to_dict(orient='records'), 
                         active_tab='tab3',
                         universities=[],
                         schools=[],
                         degrees=[])

@app.route('/function4')
def function4():
    # If function4 needs different data, load a different CSV
    function4_data = load_csv('../cleaned.csv')
    return render_template('index.html', 
                         data=function4_data.to_dict(orient='records'), 
                         active_tab='tab4',
                         universities=[],
                         schools=[],
                         degrees=[])

@app.route('/function5')
def function5():
    # Calculate projections on-the-fly
    function5_data = calculate_salary_projections()
    return render_template('index.html', 
                         data=function5_data.to_dict(orient='records'), 
                         active_tab='tab5',
                         universities=[],
                         schools=[],
                         degrees=[],
                         selected_university=None,
                         selected_school=None,
                         selected_degree=None,
                         rolling_window=3)

@app.route('/function6')
def function6():
    df = load_cleaned_data('../cleaned.csv')
    rel, corr = employment_rate_vs_salary(df)
    return render_template(
        'index.html',
        data=rel.to_dict(orient='records'),
        active_tab='tab6',
        correlation=corr,
        universities=[],
        schools=[],
        degrees=[],
        selected_university=None,
        selected_school=None,
        selected_degree=None,
        rolling_window=3,
    )

@app.route('/function7')
def function7():
    df = load_cleaned_data('../cleaned.csv')
    rel, corr = ft_perm_vs_salary(df)
    return render_template(
        'index.html',
        data=rel.to_dict(orient='records'),
        active_tab='tab7',
        correlation=corr,
        universities=[],
        schools=[],
        degrees=[],
        selected_university=None,
        selected_school=None,
        selected_degree=None,
        rolling_window=3,
    )

@app.route('/get_filtered_data', methods=['GET'])
def get_filtered_data():
    degree = request.args.get('degree')
    university = request.args.get('university')
    year = request.args.get('year')

    print(f"Filtering data for Degree: {degree}, University: {university}, Year: {year}")  # Debugging output

    # Filter the data based on the selected degree, university, and year
    filtered_data = grouped_data[(grouped_data['degree'] == degree) & 
                                  (grouped_data['university'] == university) & 
                                  (grouped_data['year'] == int(year))]

    # Debugging print to check if data is found
    print(f"Filtered data: {filtered_data}")  

    # If no data is found, return a 404 response
    if filtered_data.empty:
        return jsonify({'error': 'No data found for the selected filters'}), 404

    # Convert the values to native Python types (int and float)
    result = {
        'gross_mthly_25_percentile': int(filtered_data['gross_mthly_25_percentile'].values[0]),
        'gross_monthly_median': int(filtered_data['gross_monthly_median'].values[0]),
        'gross_mthly_75_percentile': int(filtered_data['gross_mthly_75_percentile'].values[0]),
        'IQR': int(filtered_data['IQR'].values[0]),
        'IQR_ratio': float(filtered_data['IQR_ratio'].values[0])  # IQR ratio might be a float
    }

    return jsonify(result)

# New route to fetch degrees based on the selected university
@app.route('/get_degrees', methods=['GET'])
def get_degrees():
    university = request.args.get('university')

    # Filter the data based on the selected university and get available degrees
    degrees = grouped_data[grouped_data['university'] == university]['degree'].unique()

    return jsonify({'degrees': degrees.tolist()})

@app.route('/get_years', methods=['GET'])
def get_years():
    university = request.args.get('university')
    degree = request.args.get('degree')

    # Filter the data based on the selected university and degree, then return the unique years
    years = grouped_data[(grouped_data['university'] == university) & 
                         (grouped_data['degree'] == degree)]['year'].unique()

    return jsonify({'years': years.tolist()})

@app.route('/api/get_schools', methods=['GET'])
def api_get_schools():
    """Get schools for a given university"""
    university = request.args.get('university')
    if not university:
        return jsonify({'schools': []})
    
    df = load_csv('../cleaned.csv')
    schools = sorted(df[df['university'] == university]['school'].unique().tolist())
    return jsonify({'schools': schools})

@app.route('/api/get_degrees', methods=['GET'])
def api_get_degrees():
    """Get degrees for a given university and optional school"""
    university = request.args.get('university')
    school = request.args.get('school')
    
    if not university:
        return jsonify({'degrees': []})
    
    df = load_csv('../cleaned.csv')
    filtered = df[df['university'] == university]
    
    if school:
        filtered = filtered[filtered['school'] == school]
    
    degrees = sorted(filtered['degree'].unique().tolist())
    return jsonify({'degrees': degrees})

@app.route('/data/<filename>')
def serve_csv(filename):
    """Serve CSV files from the parent directory"""
    try:
        # Get the absolute path to the parent directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, filename)
        
        if os.path.exists(file_path) and filename.endswith('.csv'):
            return send_file(file_path, mimetype='text/csv', as_attachment=False, download_name=filename)
        else:
            return jsonify({'error': f'File not found: {filename}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
