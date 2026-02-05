import pandas as pd
import numpy as np

REQUIRED_COLS = {"year", "degree", "gross_monthly_median"}

def _validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

def _clean_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["gross_monthly_median"] = pd.to_numeric(out["gross_monthly_median"], errors="coerce")
    out = out.dropna(subset=["year", "degree", "gross_monthly_median"])
    out["year"] = out["year"].astype(int)
    return out

def rankings(
    csv_path: str,
    year: int,
    n: int = 10,
    mode: str = "top",
    group_by: str = "degree",
    include_most_improved: bool = True,
):
    """
    For a chosen year, compute:
    - Top/Bottom N by gross_monthly_median
    - Rank change from previous year (Δrank)
    - % change in median salary vs previous year

    Ranking rule:
      rank 1 = highest salary (descending).
      Δrank = prev_rank - curr_rank  (positive means improved, moved up)

    group_by:
      - "degree" (default)
      - "degree_university" (if you want separate ranking per university)
    """
    df = pd.read_csv(csv_path)
    _validate_columns(df)
    df = _clean_numeric(df)

    # Decide grouping keys
    if group_by == "degree_university":
        if "university" not in df.columns:
            raise ValueError("group_by='degree_university' requires a 'university' column.")
        keys = ["degree", "university"]
    else:
        keys = ["degree"]

    # Aggregate to one row per group per year (mean is safest if duplicates exist)
    agg = (
        df.groupby(keys + ["year"], as_index=False)["gross_monthly_median"]
          .mean()
          .rename(columns={"gross_monthly_median": "median_salary"})
    )

    curr = agg[agg["year"] == int(year)].copy()
    prev = agg[agg["year"] == int(year) - 1].copy()

    if curr.empty:
        raise ValueError(f"No data found for year={year}")

    # Rank within the selected year
    curr["rank"] = curr["median_salary"].rank(method="min", ascending=False).astype(int)

    # Rank in previous year (if available)
    if not prev.empty:
        prev["prev_rank"] = prev["median_salary"].rank(method="min", ascending=False).astype(int)
    else:
        prev["prev_rank"] = np.nan

    # Join previous year info onto current year
    merged = curr.merge(
        prev[keys + ["median_salary", "prev_rank"]],
        on=keys,
        how="left",
        suffixes=("", "_prev"),
    )

    merged = merged.rename(columns={"median_salary_prev": "prev_median_salary"})

    # Δrank: positive = improved
    merged["delta_rank"] = merged["prev_rank"] - merged["rank"]

    # % salary change vs previous year
    merged["pct_change_salary"] = np.where(
        merged["prev_median_salary"].notna() & (merged["prev_median_salary"] != 0),
        (merged["median_salary"] - merged["prev_median_salary"]) / merged["prev_median_salary"] * 100.0,
        np.nan,
    )

    # Select Top/Bottom order
    mode = (mode or "top").lower().strip()
    n = int(n) if n is not None else 10
    n = max(1, min(n, 50))  # prevent crazy table sizes

    if mode == "bottom":
        selected = merged.sort_values(["median_salary", "rank"], ascending=[True, True]).head(n)
        label = f"Bottom {n}"
    else:
        selected = merged.sort_values(["median_salary", "rank"], ascending=[False, True]).head(n)
        label = f"Top {n}"

    # Most improved (biggest positive Δrank)
    most_improved = pd.DataFrame()
    if include_most_improved and merged["delta_rank"].notna().any():
        most_improved = (
            merged.dropna(subset=["delta_rank"])
                  .sort_values(["delta_rank", "median_salary"], ascending=[False, False])
                  .head(n)
        )

    # Pretty formatting for UI
    def to_records(df0: pd.DataFrame):
        if df0 is None or df0.empty:
            return []
        out = df0.copy()
        out["median_salary"] = out["median_salary"].round(2)
        out["prev_median_salary"] = out["prev_median_salary"].round(2)
        out["pct_change_salary"] = out["pct_change_salary"].round(2)
        # Ensure JSON-serializable NaNs become None in Jinja
        return out.replace({np.nan: None}).to_dict(orient="records")

    # Also return available years for dropdown
    years = sorted(df["year"].unique().tolist())

    return {
        "year": int(year),
        "n": n,
        "mode": mode,
        "label": label,
        "group_by": group_by,
        "years": years,
        "rows": to_records(selected),
        "most_improved": to_records(most_improved),
    }
