import pandas as pd

def calculate_iqr_analysis(file_path):
    """
    Calculate IQR and IQR ratio for salary spread analysis.
    
    Args:
        file_path: Path to the grouped salary analysis CSV file
    
    Returns:
        tuple: (full_data, top_iqr, top_iqr_ratio)
    """
    # Load the dataset
    data = pd.read_csv(file_path)
    
    # Ensure IQR columns exist
    if 'IQR' not in data.columns:
        data['IQR'] = data['gross_mthly_75_percentile'] - data['gross_mthly_25_percentile']
    if 'IQR_ratio' not in data.columns:
        data['IQR_ratio'] = data['IQR'] / data['gross_monthly_median']
    
    # Get the top 5 entries based on IQR and IQR ratio
    top_iqr = data.nlargest(5, 'IQR')[['degree', 'university', 'year', 'IQR', 
                                        'gross_mthly_25_percentile', 'gross_mthly_75_percentile', 
                                        'gross_monthly_median']]
    top_iqr_ratio = data.nlargest(5, 'IQR_ratio')[['degree', 'university', 'year', 'IQR_ratio', 
                                                     'gross_mthly_25_percentile', 'gross_mthly_75_percentile', 
                                                     'gross_monthly_median']]
    
    return data, top_iqr, top_iqr_ratio

def get_filtered_salary_data(file_path, degree, university, year):
    """
    Get filtered salary data for specific degree, university, and year.
    
    Args:
        file_path: Path to the grouped salary analysis CSV file
        degree: Degree name
        university: University name
        year: Year
    
    Returns:
        dict: Filtered salary data or None if not found
    """
    data = pd.read_csv(file_path)
    
    # Ensure IQR columns exist
    if 'IQR' not in data.columns:
        data['IQR'] = data['gross_mthly_75_percentile'] - data['gross_mthly_25_percentile']
    if 'IQR_ratio' not in data.columns:
        data['IQR_ratio'] = data['IQR'] / data['gross_monthly_median']
    
    filtered = data[(data['degree'] == degree) & 
                    (data['university'] == university) & 
                    (data['year'] == int(year))]
    
    if filtered.empty:
        return None
    
    return {
        'gross_mthly_25_percentile': int(filtered['gross_mthly_25_percentile'].values[0]),
        'gross_monthly_median': int(filtered['gross_monthly_median'].values[0]),
        'gross_mthly_75_percentile': int(filtered['gross_mthly_75_percentile'].values[0]),
        'IQR': int(filtered['IQR'].values[0]),
        'IQR_ratio': float(filtered['IQR_ratio'].values[0])
    }

def get_degrees_for_university(file_path, university):
    """Get available degrees for a specific university."""
    data = pd.read_csv(file_path)
    degrees = data[data['university'] == university]['degree'].unique()
    return degrees.tolist()

def get_years_for_university_degree(file_path, university, degree):
    """Get available years for a specific university and degree combination."""
    data = pd.read_csv(file_path)
    years = data[(data['university'] == university) & 
                 (data['degree'] == degree)]['year'].unique()
    return years.tolist()

# Script to generate the grouped salary analysis CSV (run once)
if __name__ == '__main__':
    # Load the dataset
    data = pd.read_csv('../cleaned_fixed.csv')

    # Group by degree, university, and year
    grouped_data = data.groupby(['degree', 'university', 'year']).agg({
        'gross_mthly_25_percentile': 'min',
        'gross_mthly_75_percentile': 'max',
        'gross_monthly_median': 'median'
    }).reset_index()

    # Calculate IQR and IQR ratio
    grouped_data['IQR'] = grouped_data['gross_mthly_75_percentile'] - grouped_data['gross_mthly_25_percentile']
    grouped_data['IQR_ratio'] = grouped_data['IQR'] / grouped_data['gross_monthly_median']

    # Save the result
    grouped_data.to_csv('../grouped_salary_analysis.csv', index=False)
    print("Salary spread analysis completed for each group!")
