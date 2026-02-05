import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your dataset
df = pd.read_csv("cleaned.csv")

# Ensure numeric types
df["year"] = pd.to_numeric(df["year"], errors="coerce")

metrics = ["employment_rate_overall", "employment_rate_ft_perm", "gross_monthly_median"]
for c in metrics:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# --------- Interactive Selection ----------
def run_analysis():
    print("\n" + "="*60)
    print("GRADUATE EMPLOYMENT TREND ANALYSIS")
    print("="*60 + "\n")
    
    # Show available universities
    universities = sorted(df["university"].unique())
    print("Available Universities:")
    for i, uni in enumerate(universities, 1):
        print(f"  {i}. {uni}")
    
    # Get university
    while True:
        uni_input = input("\nSelect university (number or name): ").strip()
        if uni_input.isdigit() and 1 <= int(uni_input) <= len(universities):
            university = universities[int(uni_input) - 1]
            break
        elif uni_input in universities:
            university = uni_input
            break
        else:
            print("❌ Invalid choice. Try again.")
    
    # Show available schools
    schools = sorted(df[df["university"] == university]["school"].unique())
    print(f"\nAvailable Schools at {university}:")
    for i, sch in enumerate(schools, 1):
        print(f"  {i}. {sch}")
    
    school_input = input("\nSelect school (number/name, or Enter to view all): ").strip()
    school = None
    if school_input:
        if school_input.isdigit() and 1 <= int(school_input) <= len(schools):
            school = schools[int(school_input) - 1]
        elif school_input in schools:
            school = school_input
    
    # Show available degrees
    degree_filter = df["university"] == university
    if school:
        degree_filter = degree_filter & (df["school"] == school)
    degrees = sorted(df[degree_filter]["degree"].unique())
    print(f"\nAvailable Degrees:")
    for i, deg in enumerate(degrees, 1):
        print(f"  {i}. {deg}")
    
    degree_input = input("\nSelect degree (number/name, or Enter to view all): ").strip()
    degree = None
    if degree_input:
        if degree_input.isdigit() and 1 <= int(degree_input) <= len(degrees):
            degree = degrees[int(degree_input) - 1]
        elif degree_input in degrees:
            degree = degree_input
    
    # Rolling window
    roll_input = input("\nRolling window size (default 3): ").strip()
    rolling_window = int(roll_input) if roll_input.isdigit() else 3
    
    print("\n" + "="*60)
    print("RUNNING ANALYSIS...")
    print("="*60 + "\n")
    
    # Filter data
    d = df[df["university"] == university].copy()
    if school:
        d = d[d["school"] == school].copy()
    if degree:
        d = d[d["degree"] == degree].copy()
    
    if d.empty:
        print("❌ No data found for the selected criteria.")
        return
    
    d = d.sort_values("year")
    d = d.groupby("year", as_index=False)[metrics].mean(numeric_only=True).sort_values("year")
    
    # Compute value-added stats
    for c in metrics:
        d[f"{c}_yoy_abs"] = d[c].diff()
        d[f"{c}_yoy_pct"] = d[c].pct_change(fill_method=None) * 100
        d[f"{c}_ma{rolling_window}"] = d[c].rolling(rolling_window, min_periods=1).mean()
    
    # Print summary
    print("--- Trend Data ---")
    print(d[["year"] + metrics +
            [f"{m}_yoy_abs" for m in metrics] +
            [f"{m}_ma{rolling_window}" for m in metrics]].to_string())
    
    # Plot
    titles = {
        "employment_rate_overall": "Employment Rate Overall (%)",
        "employment_rate_ft_perm": "FT Permanent Employment Rate (%)",
        "gross_monthly_median": "Gross Monthly Median Salary"
    }
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    for ax, c in zip(axes, metrics):
        ax.plot(d["year"], d[c], marker="o", label="Actual")
        ax.plot(d["year"], d[f"{c}_ma{rolling_window}"], linestyle="--",
                label=f"{rolling_window}-year moving avg")
        ax.set_title(titles[c])
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    axes[-1].set_xlabel("Year")
    title_parts = [university]
    if school:
        title_parts.append(school)
    if degree:
        title_parts.append(degree)
    plt.suptitle(" | ".join(title_parts), y=1.02)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_analysis()
