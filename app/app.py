from flask import Flask, render_template
import pandas as pd

app = Flask(__name__, template_folder='C:/Users/Tristan/OneDrive/SIT/3.2/INF2006/Assignment/templates')

# Load the analysis results (global to avoid reloading for each route)
grouped_data = pd.read_csv('../grouped_salary_analysis.csv')

@app.route('/')
def index():
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab1')

@app.route('/function1')
def function1():
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab1')

@app.route('/function2')
def function2():
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab2')

@app.route('/function3')
def function3():
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab3')

@app.route('/function4')
def function4():
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab4')

@app.route('/function5')
def function5():
    return render_template('index.html', data=grouped_data.to_dict(orient='records'), active_tab='tab5')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
