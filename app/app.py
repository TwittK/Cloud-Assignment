from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from function5_projection import calculate_salary_projections
from analytics import analyze_trends
from salary_analysis import (
    calculate_iqr_analysis,
    get_filtered_salary_data,
    get_degrees_for_university,
    get_years_for_university_degree
)
from data_helpers import (
    get_schools_for_university,
    get_degrees_for_university_school
)
import os

from relationship_analysis import (
    employment_rate_vs_salary,
    ft_perm_vs_salary,
    load_cleaned_data,
)

app = Flask(__name__, template_folder='../templates')

# Define a function to load different CSV files for each route (if needed)
def load_csv(file_path):
    return pd.read_csv(file_path)

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
        trend_data = analyze_trends('../cleaned.csv', university, school, degree, rolling_window)
    
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
    # Use salary_analysis module for IQR analysis
    function2_data, top_iqr, top_iqr_ratio = calculate_iqr_analysis('../grouped_salary_analysis.csv')

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

    # Use salary_analysis module for filtering
    result = get_filtered_salary_data('../grouped_salary_analysis.csv', degree, university, year)

    if result is None:
        return jsonify({'error': 'No data found for the selected filters'}), 404

    return jsonify(result)

@app.route('/get_degrees', methods=['GET'])
def get_degrees():
    university = request.args.get('university')

    # Use salary_analysis module for getting degrees
    degrees = get_degrees_for_university('../grouped_salary_analysis.csv', university)

    return jsonify({'degrees': degrees})

@app.route('/get_years', methods=['GET'])
def get_years():
    university = request.args.get('university')
    degree = request.args.get('degree')

    # Use salary_analysis module for getting years
    years = get_years_for_university_degree('../grouped_salary_analysis.csv', university, degree)

    return jsonify({'years': years})

@app.route('/api/get_schools', methods=['GET'])
def api_get_schools():
    """Get schools for a given university"""
    university = request.args.get('university')
    
    # Use data_helpers module for getting schools
    schools = get_schools_for_university('../cleaned.csv', university)
    return jsonify({'schools': schools})

@app.route('/api/get_degrees', methods=['GET'])
def api_get_degrees():
    """Get degrees for a given university and optional school"""
    university = request.args.get('university')
    school = request.args.get('school')
    
    # Use data_helpers module for getting degrees
    degrees = get_degrees_for_university_school('../cleaned.csv', university, school)
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
