from pathlib import Path
import pandas as pd

from utils import save_to_history

print("=" * 60)
print("TRADEFINDER V6 - SCANNER")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE /
    "Output" /
    "R_FACTOR.xlsx"
)

df = pd.read_excel(
    INPUT_FILE
)

print(
    f"Rows : {len(df)}"
)

# ==========================================================
# BULLISH
# ==========================================================

bullish = df[
    df["Build Up"] == "Long Build-up"
].copy()

bullish = bullish.sort_values(
    "R Factor",
    ascending=False
)

# ==========================================================
# BEARISH
# ==========================================================

bearish = df[
    df["Build Up"] == "Short Build-up"
].copy()

bearish = bearish.sort_values(
    "R Factor",
    ascending=False
)

# ==========================================================
# SIGNAL
# ==========================================================

bullish["Signal"] = "★★ Avoid"

bullish.loc[
    bullish["R Factor"] >= 90,
    "Signal"
] = "★★★★★ Strong Buy"

bullish.loc[
    (
        bullish["R Factor"] >= 80
    )
    &
    (
        bullish["R Factor"] < 90
    ),
    "Signal"
] = "★★★★ Buy"

bullish.loc[
    (
        bullish["R Factor"] >= 70
    )
    &
    (
        bullish["R Factor"] < 80
    ),
    "Signal"
] = "★★★ Watch"

bearish["Signal"] = "★★ Avoid"

bearish.loc[
    bearish["R Factor"] >= 90,
    "Signal"
] = "★★★★★ Strong Sell"

bearish.loc[
    (
        bearish["R Factor"] >= 80
    )
    &
    (
        bearish["R Factor"] < 90
    ),
    "Signal"
] = "★★★★ Sell"

bearish.loc[
    (
        bearish["R Factor"] >= 70
    )
    &
    (
        bearish["R Factor"] < 80
    ),
    "Signal"
] = "★★★ Watch"
# ==========================================================
# QUALITY FILTER
# ==========================================================

bullish = bullish[
    bullish["Signal"] != "★★ Avoid"
].copy()

bearish = bearish[
    bearish["Signal"] != "★★ Avoid"
].copy()

print(
    f"\nBullish Selected : {len(bullish)}"
)

print(
    f"Bearish Selected : {len(bearish)}"
)

# ==========================================================
# REASON
# ==========================================================

for df_scan, build_type in [

    (bullish, "Long Build-up"),

    (bearish, "Short Build-up"),

]:

    df_scan["Reason"] = ""

    df_scan.loc[
        df_scan["Build Up"] == build_type,
        "Reason"
    ] += build_type + " | "

    df_scan.loc[
        df_scan["Conviction Score"] >= 10,
        "Reason"
    ] += "High Conviction | "

    df_scan.loc[
        df_scan["Momentum Score"] >= 10,
        "Reason"
    ] += "Strong Momentum | "

    df_scan.loc[
        df_scan["OI Score"] >= 20,
        "Reason"
    ] += "Strong OI | "

    df_scan["Reason"] = (
        df_scan["Reason"]
        .str.rstrip(" | ")
    )

# ==========================================================
# ACTION
# ==========================================================

bullish["Action"] = "Watch"

bullish.loc[
    bullish["Signal"] == "★★★★★ Strong Buy",
    "Action"
] = "Buy on Breakout"

bullish.loc[
    bullish["Signal"] == "★★★★ Buy",
    "Action"
] = "Buy on Dip"

bullish.loc[
    bullish["Signal"] == "★★ Avoid",
    "Action"
] = "Ignore"
# ==========================================================
# OUTPUT COLUMNS
# ==========================================================

bullish = bullish[
    [
        "Rank",
        "SYMBOL",
        "R Factor",
        "Signal",
        "Reason",
        "Action",
        "Build Up",
        "Price Score",
        "OI Score",
        "Conviction Score",
        "Momentum Score",
    ]
]

bearish = bearish[
    [
        "Rank",
        "SYMBOL",
        "R Factor",
        "Signal",
        "Reason",
        "Build Up",
        "Price Score",
        "OI Score",
        "Conviction Score",
        "Momentum Score",
    ]
]

# ==========================================================
# SAVE OUTPUT
# ==========================================================

OUTPUT_BULL = (
    BASE /
    "Output" /
    "BULLISH_SCANNER.xlsx"
)

OUTPUT_BEAR = (
    BASE /
    "Output" /
    "BEARISH_SCANNER.xlsx"
)

bullish.to_excel(
    OUTPUT_BULL,
    index=False
)

bearish.to_excel(
    OUTPUT_BEAR,
    index=False
)

save_to_history(
    OUTPUT_BULL,
    "BULLISH_SCANNER.xlsx"
)

save_to_history(
    OUTPUT_BEAR,
    "BEARISH_SCANNER.xlsx"
)

print("\nTOP BULLISH")
print("-" * 60)
print(
    bullish.head(15)
)

print("\nTOP BEARISH")
print("-" * 60)
print(
    bearish.head(15)
)

print("\nSaved :")
print(OUTPUT_BULL)
print(OUTPUT_BEAR)

print("=" * 60)
print("SCANNER COMPLETED")
print("=" * 60)