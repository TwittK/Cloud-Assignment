import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calculate_salary_projections():
    """Calculate salary projections using linear trend extrapolation"""
    # Load the dataset
    data = pd.read_csv('../cleaned.csv')

    # Get unique degree-university combinations
    degree_university_combos = data.groupby(['degree', 'university']).size().reset_index()[['degree', 'university']]

    # Parameters for projection
    N_YEARS = 5  # Use last 5 years for linear trend
    FORECAST_YEAR = 2024  # Next year to forecast

    results = []

    for _, row in degree_university_combos.iterrows():
        degree = row['degree']
        university = row['university']
        
        # Filter data for this specific degree and university
        subset = data[(data['degree'] == degree) & (data['university'] == university)].copy()
        subset = subset.sort_values('year')
        
        # Get the last N years of data
        last_n_years = subset.tail(N_YEARS)
        
        if len(last_n_years) < 2:
            # Not enough data for projection
            continue
        
        # Prepare data for linear regression
        X = last_n_years[['year']].values
        y = last_n_years['gross_monthly_median'].values
        
        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make prediction for 2024
        predicted_2024 = model.predict([[FORECAST_YEAR]])[0]
        
        # Get the last actual value (2023)
        last_year = last_n_years['year'].max()
        last_actual_value = last_n_years[last_n_years['year'] == last_year]['gross_monthly_median'].values[0]
        
        # Calculate change
        change_amount = predicted_2024 - last_actual_value
        change_percentage = (change_amount / last_actual_value) * 100
        
        # Get the slope (trend)
        slope = model.coef_[0]
        
        # Store results
        results.append({
            'degree': degree,
            'university': university,
            'method': f'Linear Trend (last {len(last_n_years)} years: {last_n_years["year"].min()}-{last_year})',
            'last_year': int(last_year),
            'last_actual_median': round(last_actual_value, 2),
            'forecast_year': FORECAST_YEAR,
            'predicted_median_2024': round(predicted_2024, 2),
            'change_amount': round(change_amount, 2),
            'change_percentage': round(change_percentage, 2),
            'trend_slope': round(slope, 2),
            'years_used': len(last_n_years),
            'data_range': f'{last_n_years["year"].min()}-{last_year}'
        })

    # Create DataFrame
    results_df = pd.DataFrame(results)

    # Sort by predicted median (descending)
    results_df = results_df.sort_values('predicted_median_2024', ascending=False)
    
    return results_df

if __name__ == '__main__':
    # When run as a script, save to CSV
    results_df = calculate_salary_projections()
    results_df.to_csv('../function5_data.csv', index=False)

    print(f"Projection analysis completed for {len(results_df)} degree-university combinations!")
    print(f"\nTop 5 projected salaries for 2024:")
    print(results_df[['degree', 'university', 'predicted_median_2024', 'change_percentage']].head(10).to_string(index=False))
