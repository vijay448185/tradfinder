import pandas as pd

print("="*60)
print("TRADEFINDER - INDICATORS")
print("="*60)

df = pd.read_excel("Output/MASTER.xlsx")
df["LTP"] = pd.to_numeric(df["LTP"], errors="coerce")
df["PREV. CLOSE"] = pd.to_numeric(df["PREV. CLOSE"], errors="coerce")
df["MWPL"] = pd.to_numeric(df["MWPL"], errors="coerce")
df["NCL FutEq OI"] = pd.to_numeric(df["NCL FutEq OI"], errors="coerce")
df["%chng in OI"] = pd.to_numeric(df["%chng in OI"], errors="coerce")
# ------------------------
# MW Used %
# ------------------------
df["MW Used %"] = (
    df["NCL FutEq OI"] / df["MWPL"]
) * 100

# ------------------------
# Price Change %
# ------------------------
df["Price Change %"] = (
    (df["LTP"] - df["PREV. CLOSE"])
    / df["PREV. CLOSE"]
) * 100

# ------------------------
# OI Change %
# ------------------------
df["OI Change %"] = df["%chng in OI"]

# ------------------------
# Build Up
# ------------------------

def buildup(row):

    price = row["Price Change %"]
    oi = row["OI Change %"]

    if price > 0 and oi > 0:
        return "Long Build Up"

    elif price < 0 and oi > 0:
        return "Short Build Up"

    elif price > 0 and oi < 0:
        return "Short Covering"

    elif price < 0 and oi < 0:
        return "Long Unwinding"

    else:
        return "Neutral"

df["Build Up"] = df.apply(buildup, axis=1)

df.to_excel("Output/MASTER_INDICATORS.xlsx", index=False)

print("Indicators Created Successfully")
print(df[[
    "SYMBOL",
    "Price Change %",
    "OI Change %",
    "MW Used %",
    "Build Up"
]].head(20))