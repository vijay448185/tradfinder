from pathlib import Path
import pandas as pd
from utils import save_to_history

print("=" * 60)
print("TRADEFINDER V2 - LOAD DATA")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

DAILY = BASE / "Input" / "Daily"
OI = BASE / "Input" / "OI"
MW = BASE / "Input" / "MW"
DELIVERY = BASE / "Input" / "DELIVERY"
OUTPUT = BASE / "Output"

OUTPUT.mkdir(exist_ok=True)

print("Searching Files...")

daily_file = list(DAILY.glob("*.csv"))[0]
oi_file = list(OI.glob("*.csv"))[0]
mw_file = list(MW.glob("*.csv"))[0]
# ==========================================================
# MATCH DELIVERY FILE WITH DAILY DATE
# ==========================================================

daily_date = daily_file.stem[2:10]

delivery_files = list(
    DELIVERY.glob("*.csv")
)

delivery_file = None

for f in delivery_files:

    if daily_date in f.stem:

        delivery_file = f
        break

if delivery_file is None:

    raise FileNotFoundError(
        f"Delivery file not found for {daily_date}"
    )

print("Daily    :", daily_file.name)
print("OI       :", oi_file.name)
print("MW       :", mw_file.name)
print("Delivery :", delivery_file.name)
# ==========================================================
# LOAD FILES
# ==========================================================

print("\nLoading Daily File...")
daily = pd.read_csv(daily_file, low_memory=False)

print("Loading OI File...")
oi = pd.read_csv(oi_file, low_memory=False)

print("Loading MW File...")
mw = pd.read_csv(mw_file, low_memory=False)
print("Loading Delivery File...")

delivery = pd.read_csv(
    delivery_file,
    skiprows=3,
    low_memory=False
)
print("\nDelivery Shape :", delivery.shape)

print("\nRow 200")
print(delivery.iloc[200])

print("\nRow 220")
print(delivery.iloc[220])
print("\nDelivery Raw Columns:")
print(delivery.columns.tolist())

print("\nDelivery Raw Data:")
print(delivery.head(10))
# ==========================================================
# CLEAN COLUMN NAMES
# ==========================================================

daily.columns = daily.columns.str.strip()
oi.columns = oi.columns.str.strip()
mw.columns = mw.columns.str.strip()
delivery.columns = delivery.columns.str.strip()
print(delivery.columns.tolist())
print("\nDelivery Columns")
print(delivery.columns.tolist())

print("\nDaily Columns")
print(daily.columns.tolist())

print("\nOI Columns")
print(oi.columns.tolist())

print("\nMW Columns")
print(mw.columns.tolist())



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
# ==========================================================
# DELIVERY CLEAN
# ==========================================================

print(
    delivery[
        "Name of Security"
    ].head(20)
)
delivery.rename(
    columns={
        "Sr No": "SYMBOL",
        "% of Deliverable Quantity to Traded Quantity": "Delivery %"
    },
    inplace=True
)

delivery = delivery[
    delivery["Name of Security"] == "EQ"
].copy()

delivery["SYMBOL"] = (
    delivery["SYMBOL"]
    .astype(str)
    .str.upper()
    .str.strip()
)

delivery = delivery[
    [
        "SYMBOL",
        "Delivery %"
    ]
]

print("\nDelivery Records :", len(delivery))

print("\nDelivery Sample Symbols")
print(
    delivery["SYMBOL"]
    .head(10)
    .tolist()
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
master = master.merge(
    delivery,
    on="SYMBOL",
    how="left"
)

# ==========================================================
# SAVE
# ==========================================================
print("\nDelivery Merged")

print(
    master[
        [
            "SYMBOL",
            "Delivery %"
        ]
    ].head(15)
)
output_file = OUTPUT / "MASTER.xlsx"
# ==========================================================
# AUTO HISTORY
# ==========================================================

master.to_excel(output_file, index=False)

print("\n" + "=" * 60)
print("MASTER CREATED SUCCESSFULLY")
print(master.shape)
print(output_file)
print("=" * 60)
trading_date = daily_file.name[2:10]

trading_date = (
    trading_date[4:8] + "-" +
    trading_date[2:4] + "-" +
    trading_date[0:2]
)

with open(OUTPUT / "trading_date.txt", "w") as f:
    f.write(trading_date)

save_to_history(
    output_file,
    "MASTER.xlsx"
)