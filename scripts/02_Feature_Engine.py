from pathlib import Path
import pandas as pd
from utils import save_to_history

print("=" * 60)
print("TRADEFINDER V2 - FEATURE ENGINE")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

MASTER_FILE = BASE / "Output" / "MASTER.xlsx"

OUTPUT_FILE = BASE / "Output" / "FEATURES.xlsx"

print("Loading MASTER...")

df = pd.read_excel(MASTER_FILE)

print("Rows :", len(df))
print("Columns :", len(df.columns))
# ==========================================================
# REQUIRED COLUMNS
# ==========================================================

required_columns = [
    "LTP",
    "PREV. CLOSE",
    "Open Interest",
    "%chng in OI",
    "VOLUME (shares)",
    "TRADED_QUA",
    "SETTLEMENT",
    "Underlying value"
]
# Remove commas from numeric columns
for col in ["LTP", "PREV. CLOSE", "OPEN", "HIGH", "LOW"]:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
        )
for col in required_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

print("\nChecking Required Columns...")

for col in required_columns:
    if col in df.columns:
        print(f"✓ {col}")
    else:
        print(f"✗ Missing : {col}")
        # ==========================================================
# FEATURE CALCULATIONS
# ==========================================================

print("\nCreating Features...")

# 1. Price Change %
df["Price Change %"] = (
    (df["LTP"] - df["PREV. CLOSE"])
    / df["PREV. CLOSE"]
) * 100

# 2. OI Change %
df["OI Change %"] = df["%chng in OI"]

# 3. Futures Premium %
df["Futures Premium %"] = (
    (df["SETTLEMENT"] - df["LTP"])
    / df["LTP"]
) * 100

# 4. Volume Ratio

if "VOLUME (shares)" in df.columns:
    volume_col = "VOLUME (shares)"
else:
    volume_col = "TRADED_QUA"

median_volume = df[volume_col].median()

df["Volume Ratio"] = (
    df[volume_col] / median_volume
)

print("Features Created Successfully")
# ==========================================================
# DATA QUALITY REPORT
# ==========================================================

print("\n" + "=" * 60)
print("DATA QUALITY REPORT")
print("=" * 60)

mw_match = df["LTP"].notna().sum()
future_match = df["SETTLEMENT"].notna().sum()

complete_match = df[
    df["LTP"].notna() &
    df["SETTLEMENT"].notna()
].shape[0]

print(f"Total OI Records      : {len(df)}")
print(f"Matched in MW         : {mw_match}")
print(f"Matched in Futures    : {future_match}")
print(f"Complete Records      : {complete_match}")
# ==========================================================
# MISSING DATA
# ==========================================================

print("\nMissing in MW")
print("-" * 40)

missing_mw = df[df["LTP"].isna()]

if len(missing_mw):
    print(missing_mw["SYMBOL"].to_list())
else:
    print("None")

print("\nMissing in Futures")
print("-" * 40)

missing_future = df[df["SETTLEMENT"].isna()]

if len(missing_future):
    print(missing_future["SYMBOL"].to_list())
else:
    print("None")
    # ==========================================================
# REMOVE INDEX SYMBOLS
# ==========================================================

df = df[
    ~df["SYMBOL"].isin([
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "MIDCPNIFTY",
        "NIFTYNXT50"
    ])
]

print(f"\nStocks after removing indices : {len(df)}")
# ==========================================================
# SAVE FEATURES
# ==========================================================

feature_columns = [
    "SYMBOL",
    "Price Change %",
    "OI Change %",
    "Futures Premium %",
    "Volume Ratio"
]

features = df[feature_columns]

features.to_excel(OUTPUT_FILE, index=False)

print("\nFEATURES CREATED")
print(features.head(20))
save_to_history(
    OUTPUT_FILE,
    "FEATURES.xlsx"
)
