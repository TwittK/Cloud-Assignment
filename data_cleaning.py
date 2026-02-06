import pandas as pd

df = pd.read_csv("../cleaned.csv", encoding="utf-8-sig")


import re
import unicodedata

def fix_mojibake(s: str) -> str:
    """
    Attempt to fix common mojibake like 'ï¿½' (UTF-8 read as Latin-1).
    Only applies if it detects the typical pattern.
    """
    if "ï¿" in s or "Ã" in s:
        try:
            return s.encode("latin1").decode("utf-8")
        except Exception:
            return s
    return s

def clean_text(s):
    if pd.isna(s):
        return s
    s = str(s)

    # 1) Fix encoding artifacts if present
    s = fix_mojibake(s)

    # 2) Normalize unicode (standardize weird variants)
    s = unicodedata.normalize("NFKC", s)

    # 3) Remove common footnote markers: *, ^, # at ends or surrounded by spaces
    s = re.sub(r"[\*\^#]+", "", s)

    # 4) Remove odd replacement characters + zero-width chars
    s = s.replace("\uFFFD", "")  # �
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)

    # 5) Replace non-breaking spaces and collapse whitespace
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()

    return s

# Apply to the columns that should be clean text
text_cols = [c for c in df.columns if df[c].dtype == "object"]
for c in text_cols:
    df[c] = df[c].apply(clean_text)

df.to_csv("cleaned_fixed.csv", index=False, encoding="utf-8-sig")
print("Saved -> cleaned_fixed.csv")

# Show rows that still contain suspicious characters after cleaning
bad = df[text_cols].apply(lambda col: col.astype(str).str.contains(r"[ï¿Ã\uFFFD\*\^#]", regex=True, na=False)).any(axis=1)
print("Rows still suspicious:", bad.sum())
print(df.loc[bad, text_cols].head(10))