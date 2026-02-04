from flask import Flask, render_template
import pandas as pd

app = Flask(__name__, template_folder='C:/Users/Tristan/OneDrive/SIT/3.2/INF2006/Assignment/templates')

@app.route('/')
def index():
    # Load the analysis results
    grouped_data = pd.read_csv('../grouped_salary_analysis.csv')
    
    # Render the HTML template and pass the data
    return render_template('index.html', data=grouped_data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
