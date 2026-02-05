import pandas as pd
import numpy as np

def analyze_trends(file_path, university=None, school=None, degree=None, rolling_window=3):
    """
    Analyze employment and salary trends for a given university/school/degree.
    
    Args:
        file_path: Path to the cleaned CSV file
        university: University name (required)
        school: School name (optional)
        degree: Degree name (optional)
        rolling_window: Window size for moving average (default: 3)
    
    Returns:
        DataFrame with trend analysis or None if no data found
    """
    # Load dataset
    df = pd.read_csv(file_path)
    
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
