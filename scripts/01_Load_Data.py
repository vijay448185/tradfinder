from pathlib import Path
import pandas as pd

print("=" * 60)
print("TRADEFINDER V2 - LOAD DATA")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

DAILY = BASE / "Input" / "Daily"
OI = BASE / "Input" / "OI"
MW = BASE / "Input" / "MW"
OUTPUT = BASE / "Output"

OUTPUT.mkdir(exist_ok=True)

print("Searching Files...")

daily_file = list(DAILY.glob("*.csv"))[0]
oi_file = list(OI.glob("*.csv"))[0]
mw_file = list(MW.glob("*.csv"))[0]

print("Daily :", daily_file.name)
print("OI    :", oi_file.name)
print("MW    :", mw_file.name)
# ==========================================================
# LOAD FILES
# ==========================================================

print("\nLoading Daily File...")
daily = pd.read_csv(daily_file, low_memory=False)

print("Loading OI File...")
oi = pd.read_csv(oi_file, low_memory=False)

print("Loading MW File...")
mw = pd.read_csv(mw_file, low_memory=False)

# ==========================================================
# CLEAN COLUMN NAMES
# ==========================================================

daily.columns = daily.columns.str.strip()
oi.columns = oi.columns.str.strip()
mw.columns = mw.columns.str.strip()

print("\nDaily Columns")
print(daily.columns.tolist())

print("\nOI Columns")
print(oi.columns.tolist())

print("\nMW Columns")
print(mw.columns.tolist())
# ==========================================================
# PREPARE DATA
# ==========================================================

# OI Symbol
oi.rename(columns={
    "Symbol": "SYMBOL"
}, inplace=True)

# Daily Contract
daily.rename(columns={
    "CONTRACT_D": "CONTRACT"
}, inplace=True)

# MW Symbol
mw.rename(columns={
    "SYMBOL": "SYMBOL"
}, inplace=True)

# Clean Symbols
oi["SYMBOL"] = (
    oi["SYMBOL"]
    .astype(str)
    .str.upper()
    .str.strip()
)

mw["SYMBOL"] = (
    mw["SYMBOL"]
    .astype(str)
    .str.upper()
    .str.strip()
)

print("\nOI Records :", len(oi))
print("Daily Records :", len(daily))
print("MW Records :", len(mw))

print("\nOI Sample Symbols")
print(oi["SYMBOL"].head(10).tolist())
# ==========================================================
# EXTRACT SYMBOL FROM FUTURES CONTRACT
# ==========================================================

import re

def extract_symbol(contract):
    contract = str(contract).upper().strip()

    # Remove Prefix
    contract = contract.replace("FUTSTK", "")
    contract = contract.replace("FUTIDX", "")

    # Remove Expiry (e.g. 30-JUN-2026)
    contract = re.sub(r"\d{2}-[A-Z]{3}-\d{4}$", "", contract)

    return contract.strip()

daily["SYMBOL"] = daily["CONTRACT"].apply(extract_symbol)
# ==========================================================
# KEEP ONLY CURRENT MONTH FUTURE
# ==========================================================

daily["EXPIRY"] = daily["CONTRACT"].str.extract(r'(\d{2}-[A-Z]{3}-\d{4})')

print("\nAvailable Expiries:")
print(daily["EXPIRY"].value_counts())

# Keep nearest expiry only
daily["EXPIRY_DATE"] = pd.to_datetime(
    daily["EXPIRY"],
    format="%d-%b-%Y"
)

nearest_expiry = daily["EXPIRY_DATE"].min()

daily = daily[
    daily["EXPIRY_DATE"] == nearest_expiry
]

print("\nUsing Expiry :", nearest_expiry.date())
print("Rows After Expiry Filter :", len(daily))

print("\nUsing Expiry :", nearest_expiry)



print("Rows After Expiry Filter :", len(daily))

print("\nDaily Sample Symbols")
print(daily["SYMBOL"].head(10).tolist())

# ==========================================================
# KEEP REQUIRED COLUMNS
# ==========================================================

daily = daily[
    [
        "SYMBOL",
        "OPEN_PRICE",
        "HIGH_PRICE",
        "LOW_PRICE",
        "CLOSE_PRIC",
        "SETTLEMENT",
        "NET_CHANGE",
        "OI_NO_CON",
        "TRADED_QUA",
        "TRD_NO_CON",
        "TRADED_VAL",
    ]
]

# ==========================================================
# MERGE
# ==========================================================

master = oi.merge(
    mw,
    on="SYMBOL",
    how="left"
)

master = master.merge(
    daily,
    on="SYMBOL",
    how="left"
)

# ==========================================================
# SAVE
# ==========================================================

output_file = OUTPUT / "MASTER.xlsx"

master.to_excel(output_file, index=False)

print("\n" + "=" * 60)
print("MASTER CREATED SUCCESSFULLY")
print(master.shape)
print(output_file)
print("=" * 60)