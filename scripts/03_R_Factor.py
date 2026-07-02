from pathlib import Path
import pandas as pd
from utils import save_to_history
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
# ==========================================================
# CONVICTION SCORE
# ==========================================================

df["Conviction Score"] = 0

# Very Strong Setup
df.loc[
    (df["Price Change %"] >= 2) &
    (df["OI Change %"] >= 15) &
    (df["Volume Ratio"] >= 2),
    "Conviction Score"
] = 10

# Strong Setup
df.loc[
    (df["Price Change %"] >= 1) &
    (df["OI Change %"] >= 10),
    "Conviction Score"
] = df["Conviction Score"].clip(lower=5)

# Weak Setup
df.loc[
    (df["Price Change %"] < 0) &
    (df["OI Change %"] > 10),
    "Conviction Score"
] = -5
# ==========================================================
# BUILD-UP LOGIC
# ==========================================================

df["Build Up"] = "Neutral"

# Long Build-up
df.loc[
    (df["Price Change %"] > 0) &
    (df["OI Change %"] > 0),
    "Build Up"
] = "Long Build-up"

# Short Build-up
df.loc[
    (df["Price Change %"] < 0) &
    (df["OI Change %"] > 0),
    "Build Up"
] = "Short Build-up"

# Short Covering
df.loc[
    (df["Price Change %"] > 0) &
    (df["OI Change %"] < 0),
    "Build Up"
] = "Short Covering"

# Long Unwinding
df.loc[
    (df["Price Change %"] < 0) &
    (df["OI Change %"] < 0),
    "Build Up"
] = "Long Unwinding"

# Bonus according to Build-up
df.loc[df["Build Up"] == "Long Build-up", "Bonus Score"] = 20
df.loc[df["Build Up"] == "Short Covering", "Bonus Score"] = 15
df.loc[df["Build Up"] == "Long Unwinding", "Bonus Score"] = 5
df.loc[df["Build Up"] == "Short Build-up", "Bonus Score"] = 0
# Final R Factor
# ==========================================================
# MOMENTUM SCORE
# ==========================================================

df["Momentum Score"] = 0

# Strong Momentum
df.loc[
    (df["Price Change %"] >= 2) &
    (df["Volume Ratio"] >= 2),
    "Momentum Score"
] = 10

# Medium Momentum
df.loc[
    (df["Price Change %"] >= 1) &
    (df["Volume Ratio"] >= 1.5),
    "Momentum Score"
] = df["Momentum Score"].clip(lower=5)

# Weak Momentum
df.loc[
    (df["Price Change %"] < 0),
    "Momentum Score"
] = -5
df["R Factor"] = (
    df["Price Score"]
    + df["OI Score"]
    + df["Premium Score"]
    + df["Volume Score"]
    + df["Bonus Score"]
    + df["Conviction Score"]
    + df["Momentum Score"]
)


print("R Factor Created")
# ==========================================================
# RANKING
# ==========================================================
print("\nMissing R Factor :", df["R Factor"].isna().sum())

print(df[df["R Factor"].isna()][["SYMBOL"]])

rank = df["R Factor"].rank(
    ascending=False,
    method="dense"
)

print("\nMissing Rank :", rank.isna().sum())

print(
    df.loc[
        rank.isna(),
        ["SYMBOL", "R Factor"]
    ]
)

df["Rank"] = rank

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
    "Build Up",
    "Price Score",
    "OI Score",
    "Premium Score",
    "Volume Score",
    "Bonus Score",
    "Conviction Score",
    "Momentum Score",
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
save_to_history(OUTPUT_FILE, "R_FACTOR.xlsx")