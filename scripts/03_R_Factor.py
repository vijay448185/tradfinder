from pathlib import Path
import pandas as pd

from utils import save_to_history

print("=" * 60)
print("TRADEFINDER V3 - R FACTOR")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

FEATURE_FILE = (
    BASE /
    "Output" /
    "FEATURES.xlsx"
)

OUTPUT_FILE = (
    BASE /
    "Output" /
    "R_FACTOR.xlsx"
)

print("Loading FEATURES...")

df = pd.read_excel(
    FEATURE_FILE
)

print(
    f"Rows : {len(df)}"
)

print(
    f"Columns : {len(df.columns)}"
)

# ==========================================================
# BUILD UP
# ==========================================================

df["Build Up"] = "Neutral"

df.loc[
    (df["Price Change %"] > 0) &
    (df["OI Change %"] > 0),
    "Build Up"
] = "Long Build-up"

df.loc[
    (df["Price Change %"] < 0) &
    (df["OI Change %"] > 0),
    "Build Up"
] = "Short Build-up"

df.loc[
    (df["Price Change %"] > 0) &
    (df["OI Change %"] < 0),
    "Build Up"
] = "Short Covering"

df.loc[
    (df["Price Change %"] < 0) &
    (df["OI Change %"] < 0),
    "Build Up"
] = "Long Unwinding"

# ==========================================================
# SCORE COLUMNS
# ==========================================================

df["Price Score"] = 0.0
df["OI Score"] = 0.0
df["Premium Score"] = 0.0
df["Volume Score"] = 0.0

df["Bonus Score"] = 0
df["Conviction Score"] = 0
df["Momentum Score"] = 0

print("\nCalculating Dynamic Scores...")
# ==========================================================
# DIRECTIONAL SCORES
# ==========================================================

# -------- LONG BUILD-UP --------

long_mask = (
    df["Build Up"] == "Long Build-up"
)

df.loc[
    long_mask,
    "Price Score"
] = (
    df.loc[
        long_mask,
        "Price Change %"
    ]
    .rank(pct=True)
    .fillna(0)
    * 25
)

df.loc[
    long_mask,
    "OI Score"
] = (
    df.loc[
        long_mask,
        "OI Change %"
    ]
    .rank(pct=True)
    .fillna(0)
    * 25
)

df.loc[
    long_mask,
    "Premium Score"
] = (
    df.loc[
        long_mask,
        "Futures Premium %"
    ]
    .rank(pct=True)
    .fillna(0)
    * 20
)

# -------- SHORT BUILD-UP --------

short_mask = (
    df["Build Up"] == "Short Build-up"
)

# Bigger price fall = higher score
df.loc[
    short_mask,
    "Price Score"
] = (
    (-df.loc[
        short_mask,
        "Price Change %"
    ])
    .rank(pct=True)
    .fillna(0)
    * 25
)

# Higher OI increase = higher score
df.loc[
    short_mask,
    "OI Score"
] = (
    df.loc[
        short_mask,
        "OI Change %"
    ]
    .rank(pct=True)
    .fillna(0)
    * 25
)

# Discount / lower premium is stronger for bearish
df.loc[
    short_mask,
    "Premium Score"
] = (
    (-df.loc[
        short_mask,
        "Futures Premium %"
    ])
    .rank(pct=True)
    .fillna(0)
    * 20
)

# -------- VOLUME (COMMON) --------

df["Volume Score"] = (
    df["Volume Ratio"]
    .rank(pct=True)
    .fillna(0)
    * 20
)

# ==========================================================
# BONUS SCORE
# ==========================================================

df.loc[
    long_mask,
    "Bonus Score"
] = 20

df.loc[
    short_mask,
    "Bonus Score"
] = 20

df.loc[
    df["Build Up"] == "Short Covering",
    "Bonus Score"
] = 8

df.loc[
    df["Build Up"] == "Long Unwinding",
    "Bonus Score"
] = 8
# ==========================================================
# CONVICTION
# ==========================================================

# Long Build-up
df.loc[
    long_mask &
    (df["Price Change %"] >= 2) &
    (df["OI Change %"] >= 15) &
    (df["Volume Ratio"] >= 2),
    "Conviction Score"
] = 10

df.loc[
    long_mask &
    (df["Price Change %"] >= 1) &
    (df["OI Change %"] >= 10),
    "Conviction Score"
] = 5

# Short Build-up
df.loc[
    short_mask &
    (df["Price Change %"] <= -2) &
    (df["OI Change %"] >= 15) &
    (df["Volume Ratio"] >= 2),
    "Conviction Score"
] = 10

df.loc[
    short_mask &
    (df["Price Change %"] <= -1) &
    (df["OI Change %"] >= 10),
    "Conviction Score"
] = 5

# ==========================================================
# MOMENTUM
# ==========================================================

# Bullish Momentum
df.loc[
    long_mask &
    (df["Price Change %"] >= 2) &
    (df["Volume Ratio"] >= 2),
    "Momentum Score"
] = 10

df.loc[
    long_mask &
    (df["Price Change %"] >= 1) &
    (df["Volume Ratio"] >= 1.5),
    "Momentum Score"
] = 5

# Bearish Momentum
df.loc[
    short_mask &
    (df["Price Change %"] <= -2) &
    (df["Volume Ratio"] >= 2),
    "Momentum Score"
] = 10

df.loc[
    short_mask &
    (df["Price Change %"] <= -1) &
    (df["Volume Ratio"] >= 1.5),
    "Momentum Score"
] = 5

# ==========================================================
# FINAL R FACTOR
# ==========================================================

df["R Factor"] = (
    df["Price Score"]
    + df["OI Score"]
    + df["Premium Score"]
    + df["Volume Score"]
    + df["Bonus Score"]
    + df["Conviction Score"]
    + df["Momentum Score"]
)

df["Rank"] = (
    df["R Factor"]
    .rank(
        ascending=False,
        method="dense"
    )
)

df = df.sort_values(
    "R Factor",
    ascending=False
)

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
    "R Factor",

]

result = df[
    output_columns
]

result.to_excel(
    OUTPUT_FILE,
    index=False
)

save_to_history(
    OUTPUT_FILE,
    "R_FACTOR.xlsx"
)

print("\nTOP 20")
print(result.head(20))

print("\nSaved :")
print(OUTPUT_FILE)

print("=" * 60)
print("R FACTOR COMPLETED")
print("=" * 60)