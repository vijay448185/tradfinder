from pathlib import Path
import pandas as pd

# ==========================================================
# TRADEFINDER - INDICATORS
# ==========================================================

BASE = Path(__file__).resolve().parent.parent
MASTER_FILE = BASE / "Output" / "MASTER.xlsx"

print("=" * 60)
print("TRADEFINDER - INDICATORS")
print("=" * 60)

df = pd.read_excel(MASTER_FILE)

# ----------------------------------------------------------
# Convert required columns to numeric
# ----------------------------------------------------------

numeric_cols = [
    "LTP",
    "PREV. CLOSE",
    "MWPL",
    "NCL FutEq OI",
    "%chng in OI"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ----------------------------------------------------------
# MW Used %
# ----------------------------------------------------------

df["MW Used %"] = (df["NCL FutEq OI"] / df["MWPL"]) * 100

# ----------------------------------------------------------
# Price Change %
# ----------------------------------------------------------

df["Price Change %"] = (
    (df["LTP"] - df["PREV. CLOSE"])
    / df["PREV. CLOSE"]
) * 100

# ----------------------------------------------------------
# OI Change %
# ----------------------------------------------------------

df["OI Change %"] = df["%chng in OI"]

# ----------------------------------------------------------
# Build Up
# ----------------------------------------------------------

def build_up(row):

    price = row["Price Change %"]
    oi = row["OI Change %"]

    if pd.isna(price) or pd.isna(oi):
        return "No Data"

    if price > 0 and oi > 0:
        return "Long Build Up"

    if price < 0 and oi > 0:
        return "Short Build Up"

    if price > 0 and oi < 0:
        return "Short Covering"

    if price < 0 and oi < 0:
        return "Long Unwinding"

    return "Neutral"


df["Build Up"] = df.apply(build_up, axis=1)

# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

OUTPUT_FILE = BASE / "Output" / "MASTER_INDICATORS.xlsx"

df.to_excel(OUTPUT_FILE, index=False)

print("=" * 60)
print("Indicators Created Successfully")
print("=" * 60)

print(
    df[
        [
            "SYMBOL",
            "Price Change %",
            "OI Change %",
            "MW Used %",
            "Build Up",
        ]
    ].tail(20)
)