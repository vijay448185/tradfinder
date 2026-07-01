from pathlib import Path
import pandas as pd

print("=" * 60)
print("TRADEFINDER V2 - R FACTOR")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

FEATURE_FILE = BASE / "Output" / "FEATURES.xlsx"
OUTPUT_FILE = BASE / "Output" / "R_FACTOR.xlsx"

print("Loading FEATURES...")

df = pd.read_excel(FEATURE_FILE)

print("Rows :", len(df))
print("Columns :", len(df.columns))
# ==========================================================
# CREATE R FACTOR SCORES
# ==========================================================

print("\nCreating R Scores...")

# Price Score (0-25)
df["Price Score"] = (
    df["Price Change %"]
    .rank(pct=True)
    .fillna(0)
    * 25
)

# OI Score (0-25)
df["OI Score"] = (
    df["OI Change %"]
    .rank(pct=True)
    .fillna(0)
    * 25
)

# Premium Score (0-20)
df["Premium Score"] = (
    df["Futures Premium %"]
    .rank(pct=True)
    .fillna(0)
    * 20
)

# Volume Score (0-20)
df["Volume Score"] = (
    df["Volume Ratio"]
    .rank(pct=True)
    .fillna(0)
    * 20
)

# Bonus Score
df["Bonus Score"] = 10

# Final R Factor
df["R Factor"] = (
    df["Price Score"]
    + df["OI Score"]
    + df["Premium Score"]
    + df["Volume Score"]
    + df["Bonus Score"]
)

print("R Factor Created")
# ==========================================================
# RANKING
# ==========================================================

df["Rank"] = (
    df["R Factor"]
    .rank(
        ascending=False,
        method="dense"
    )
    .astype(int)
)

df = df.sort_values(
    "R Factor",
    ascending=False
)

# ==========================================================
# SAVE
# ==========================================================

output_columns = [
    "Rank",
    "SYMBOL",
    "Price Score",
    "OI Score",
    "Premium Score",
    "Volume Score",
    "Bonus Score",
    "R Factor"
]

result = df[output_columns]

result.to_excel(
    OUTPUT_FILE,
    index=False
)

print("\nTOP 20 STOCKS")
print(result.head(20))

print("\nSaved :", OUTPUT_FILE)