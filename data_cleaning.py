import pandas as pd
import re
import unicodedata

INPUT = "GraduateEmploymentSurveyNTUNUSSITSMUSUSSSUTD.csv"
OUTPUT = "cleaned"

def fix_mojibake(s: str) -> str:
    """
    Fix common mojibake like 'ï¿½' (UTF-8 text that was decoded as latin1/cp1252).
    Only attempts conversion when typical patterns appear.
    """
    if "ï¿" in s or "Ã" in s:
        try:
            return s.encode("latin1").decode("utf-8")
        except Exception:
            return s
    return s

def clean_text(x):
    if pd.isna(x):
        return x
    s = str(x)

    # Fix encoding artifacts if present
    s = fix_mojibake(s)

    # Normalize unicode
    s = unicodedata.normalize("NFKC", s)

    # Remove common footnote markers/artifacts
    s = re.sub(r"[\*\^#]+", "", s)

    # Remove replacement char and zero-width chars
    s = s.replace("\uFFFD", "")  # �
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)

    # Normalize spaces
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()

    return s

# 1) Read original CSV as strings (keep placeholders like N.A. intact)
df = pd.read_csv(INPUT, dtype=str, encoding="utf-8-sig")

# 2) Define metric columns (E to L = index 4 to 11)
metric_cols = df.columns[4:12].tolist()

# 3) Clean TEXT columns (everything except metric columns)
text_cols = [c for c in df.columns if c not in metric_cols]
for c in text_cols:
    df[c] = df[c].apply(clean_text)

# 4) Clean METRIC columns (strip + standardize missing tokens)
for c in metric_cols:
    df[c] = df[c].astype(str).str.strip()

# Make missing values consistent (covers N.A., NA, n.a., blanks, etc.)
df[metric_cols] = df[metric_cols].replace(
    to_replace=r"^(?:N\.?A\.?|NA|na|n\.?a\.?)$|^$",
    value=pd.NA,
    regex=True
)

# NEW: remove % symbols (and commas) before converting to numbers
for c in metric_cols:
    df[c] = (
        df[c]
        .astype(str)
        .str.replace("%", "", regex=False)     # remove %
        .str.replace(",", "", regex=False)     # remove thousands separators if any
        .str.strip()
    )

# Convert metrics to numeric
for c in metric_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Drop rows where ANY metric column is missing/invalid
df = df.dropna(subset=metric_cols, how="any")

# 5) Drop rows where ANY metric column is missing
df = df.dropna(subset=metric_cols, how="any")

# (Optional) Convert metrics to numeric after cleaning
for c in metric_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# If conversion creates NaN (from weird values), enforce again:
df = df.dropna(subset=metric_cols, how="any")

# 6) Quick sanity check: remaining “bad” characters in text columns
bad_mask = df[text_cols].apply(
    lambda col: col.astype(str).str.contains(r"[ï¿Ã\uFFFD\*\^#]", regex=True, na=False)
).any(axis=1)

print("Rows still suspicious:", int(bad_mask.sum()))
if bad_mask.any():
    print(df.loc[bad_mask, text_cols].head(10))

# 7) Save cleaned output
df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
print(f"Saved -> {OUTPUT}")
print("Final rows:", len(df))
