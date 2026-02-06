import pandas as pd
from pathlib import Path

NUMERIC_COLS = [
    "employment_rate_overall",
    "employment_rate_ft_perm",
    "basic_monthly_mean",
    "basic_monthly_median",
    "gross_monthly_mean",
    "gross_monthly_median",
    "gross_mthly_25_percentile",
    "gross_mthly_75_percentile",
]


def load_cleaned_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _relationship_frame(df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    base_cols = ["year", "university", "school", "degree", x_col, y_col]
    cols = [c for c in base_cols if c in df.columns]
    rel = df[cols].dropna(subset=[x_col, y_col]).copy()
    return rel


def _correlation_value(df: pd.DataFrame, x_col: str, y_col: str) -> float:
    sub = df[[x_col, y_col]].dropna()
    if len(sub) < 2:
        return float("nan")
    return float(sub[x_col].corr(sub[y_col]))


def employment_rate_vs_salary(
    df: pd.DataFrame,
    salary_col: str = "gross_monthly_median",
) -> tuple[pd.DataFrame, float]:
    rel = _relationship_frame(df, "employment_rate_overall", salary_col)
    corr = _correlation_value(df, "employment_rate_overall", salary_col)
    return rel, corr


def ft_perm_vs_salary(
    df: pd.DataFrame,
    salary_col: str = "gross_monthly_median",
) -> tuple[pd.DataFrame, float]:
    rel = _relationship_frame(df, "employment_rate_ft_perm", salary_col)
    corr = _correlation_value(df, "employment_rate_ft_perm", salary_col)
    return rel, corr


def save_relationship_outputs(
    csv_path: str = "../cleaned_fixed.csv",
    output_dir: str = "..",
    salary_col: str = "gross_monthly_median",
) -> pd.DataFrame:
    df = load_cleaned_data(csv_path)
    output_path = Path(output_dir)

    rel1, corr1 = employment_rate_vs_salary(df, salary_col=salary_col)
    rel2, corr2 = ft_perm_vs_salary(df, salary_col=salary_col)

    rel1.to_csv(output_path / "employment_rate_vs_salary.csv", index=False)
    rel2.to_csv(output_path / "ft_perm_vs_salary.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "relationship": "employment_rate_overall_vs_salary",
                "x_col": "employment_rate_overall",
                "y_col": salary_col,
                "pearson_r": corr1,
                "n": rel1.shape[0],
            },
            {
                "relationship": "employment_rate_ft_perm_vs_salary",
                "x_col": "employment_rate_ft_perm",
                "y_col": salary_col,
                "pearson_r": corr2,
                "n": rel2.shape[0],
            },
        ]
    )
    summary.to_csv(output_path / "relationship_summary.csv", index=False)
    return summary


if __name__ == "__main__":
    summary_df = save_relationship_outputs()
    print(summary_df.to_string(index=False))
