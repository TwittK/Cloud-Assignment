from flask import Flask, render_template, request, jsonify
import pandas as pd
from function5_projection import calculate_salary_projections

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

@app.route('/')
def index():
    # Default tab, using a specific CSV file
    grouped_data = load_csv('../cleaned.csv')
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab1')

@app.route('/function1')
def function1():
    # If function1 needs different data, load a different CSV
    function1_data = load_csv('../cleaned.csv')
    return render_template('index.html', data=function1_data.to_dict(orient='records'), active_tab='tab1')

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
        years=unique_years  # Passing years to the frontend
    )

@app.route('/function3')
def function3():
    # If function3 needs different data, load a different CSV
    function3_data = load_csv('../cleaned.csv')
    return render_template('index.html', data=function3_data.to_dict(orient='records'), active_tab='tab3')

@app.route('/function4')
def function4():
    # If function4 needs different data, load a different CSV
    function4_data = load_csv('../cleaned.csv')
    return render_template('index.html', data=function4_data.to_dict(orient='records'), active_tab='tab4')

@app.route('/function5')
def function5():
    # Calculate projections on-the-fly
    function5_data = calculate_salary_projections()
    return render_template('index.html', data=function5_data.to_dict(orient='records'), active_tab='tab5')

@app.route('/function6')
def function6():
    df = load_cleaned_data('../cleaned.csv')
    rel, corr = employment_rate_vs_salary(df)
    return render_template(
        'index.html',
        data=rel.to_dict(orient='records'),
        active_tab='tab6',
        correlation=corr,
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
