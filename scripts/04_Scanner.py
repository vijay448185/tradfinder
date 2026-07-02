from pathlib import Path
import pandas as pd
from utils import save_to_history

# ==========================================================
# TRADEFINDER SCANNER
# ==========================================================

print("=" * 60)
print("TRADEFINDER V3 - SCANNER")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE / "Output" / "R_FACTOR.xlsx"

df = pd.read_excel(INPUT_FILE)

print("Rows :", len(df))


# ==========================================================
# BULLISH SCANNER
# ==========================================================

bullish = df[df["Build Up"] == "Long Build-up"].copy()
# ==========================================================
# BEARISH SCANNER
# ==========================================================

bearish = df[df["Build Up"] == "Short Build-up"].copy()

bearish = bearish.sort_values(
    "R Factor",
    ascending=False
)
bullish = bullish.sort_values(
    "R Factor",
    ascending=False
)


# ==========================================================
# SIGNAL
# ==========================================================

bullish["Signal"] = "Watch"
bearish["Signal"] = "Watch"

bearish.loc[
    bearish["R Factor"] >= 90,
    "Signal"
] = "★★★★★ Strong Sell"

bearish.loc[
    (bearish["R Factor"] >= 80) &
    (bearish["R Factor"] < 90),
    "Signal"
] = "★★★★ Sell"

bearish.loc[
    (bearish["R Factor"] >= 70) &
    (bearish["R Factor"] < 80),
    "Signal"
] = "★★★ Watch"

bearish.loc[
    bearish["R Factor"] < 70,
    "Signal"
] = "★★ Avoid"
bullish.loc[bullish["R Factor"] >= 90, "Signal"] = "★★★★★ Strong Buy"

bullish.loc[
    (bullish["R Factor"] >= 80) &
    (bullish["R Factor"] < 90),
    "Signal"
] = "★★★★ Buy"

bullish.loc[
    (bullish["R Factor"] >= 70) &
    (bullish["R Factor"] < 80),
    "Signal"
] = "★★★ Watch"

bullish.loc[
    bullish["R Factor"] < 70,
    "Signal"
] = "★★ Avoid"


# ==========================================================
# REASON
# ==========================================================

bullish["Reason"] = ""

bullish.loc[
    bullish["Build Up"] == "Long Build-up",
    "Reason"
] += "Long Build-up | "

bullish.loc[
    bullish["Conviction Score"] >= 10,
    "Reason"
] += "High Conviction | "

bullish.loc[
    bullish["Momentum Score"] >= 10,
    "Reason"
] += "Strong Momentum | "

bullish.loc[
    bullish["OI Score"] >= 20,
    "Reason"
] += "Strong OI | "

bullish["Reason"] = bullish["Reason"].str.rstrip(" | ")
bearish["Reason"] = ""

bearish.loc[
    bearish["Build Up"] == "Short Build-up",
    "Reason"
] += "Short Build-up | "

bearish.loc[
    bearish["Conviction Score"] >= 10,
    "Reason"
] += "High Conviction | "

bearish.loc[
    bearish["Momentum Score"] >= 10,
    "Reason"
] += "Strong Momentum | "

bearish.loc[
    bearish["OI Score"] >= 20,
    "Reason"
] += "Strong OI | "

bearish["Reason"] = ""

bearish.loc[
    bearish["Build Up"] == "Short Build-up",
    "Reason"
] += "Short Build-up | "

bearish.loc[
    bearish["Conviction Score"] >= 10,
    "Reason"
] += "High Conviction | "

bearish.loc[
    bearish["Momentum Score"] >= 10,
    "Reason"
] += "Strong Momentum | "

bearish.loc[
    bearish["OI Score"] >= 20,
    "Reason"
] += "Strong OI | "

bearish["Reason"] = bearish["Reason"].str.rstrip(" | ")
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
    bullish["Signal"] == "★★★ Watch",
    "Action"
] = "Watch"

bullish.loc[
    bullish["Signal"] == "★★ Avoid",
    "Action"
] = "Ignore"


# ==========================================================
# OUTPUT
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
# ==========================================================
# BEARISH OUTPUT
# ==========================================================

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

print("\nTOP 10 BEARISH\n")

bearish = bearish.head(10)

print(bearish.head(10))

OUTPUT_BEARISH = BASE / "Output" / "BEARISH_SCANNER.xlsx"
bearish.to_excel(
    OUTPUT_BEARISH,
    index=False
)

print("\nSaved :", OUTPUT_BEARISH)

save_to_history(
    OUTPUT_BEARISH,
    "BEARISH_SCANNER.xlsx"
)
print()
bullish = bullish.head(10)
print(bullish.head(10))

OUTPUT = BASE / "Output" / "BULLISH_SCANNER.xlsx"

bullish.to_excel(
    OUTPUT,
    index=False
)
print("\nSaved :", OUTPUT)

save_to_history(OUTPUT, "BULLISH_SCANNER.xlsx")


