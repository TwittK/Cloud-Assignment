from flask import Flask, render_template
import pandas as pd
from function5_projection import calculate_salary_projections

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
    # Default tab, using a specific CSV file
    grouped_data = load_csv('../cleaned.csv')
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab1')

@app.route('/function1')
def function1():
    # If function1 needs different data, load a different CSV
    function1_data = load_csv('../function1_data.csv')
    return render_template('index.html', data=function1_data.to_dict(orient='records'), active_tab='tab1')

@app.route('/function2')
def function2():
    # If function2 needs different data, load a different CSV
    function2_data = load_csv('../grouped_salary_analysis.csv')
    return render_template('index.html', data=function2_data.to_dict(orient='records'), active_tab='tab2')

@app.route('/function3')
def function3():
    # If function3 needs different data, load a different CSV
    function3_data = load_csv('../function3_data.csv')
    return render_template('index.html', data=function3_data.to_dict(orient='records'), active_tab='tab3')

@app.route('/function4')
def function4():
    # If function4 needs different data, load a different CSV
    function4_data = load_csv('../function4_data.csv')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
