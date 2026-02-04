import pandas as pd

# Load the dataset
data = pd.read_csv('../cleaned.csv')  # Make sure the path is correct

# Group by degree, university, and year
grouped_data = data.groupby(['degree', 'university', 'year']).agg({
    'gross_mthly_25_percentile': 'min',  # 25th percentile
    'gross_mthly_75_percentile': 'max',  # 75th percentile
    'gross_monthly_median': 'median'    # Median salary
}).reset_index()

# Calculate IQR (75th percentile - 25th percentile) and IQR ratio (IQR / median)
grouped_data['IQR'] = grouped_data['gross_mthly_75_percentile'] - grouped_data['gross_mthly_25_percentile']
grouped_data['IQR_ratio'] = grouped_data['IQR'] / grouped_data['gross_monthly_median']

# Save the result to a new CSV file
grouped_data.to_csv('../grouped_salary_analysis.csv', index=False)

print("Salary spread analysis completed for each group!")
