from pathlib import Path
import pandas as pd
from utils import save_to_history
print("=" * 60)
print("TRADEFINDER V3 - BACKTEST")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

HISTORY = BASE / "History"

folders = sorted(
    [x for x in HISTORY.iterdir() if x.is_dir()]
)

print("Available History")

for f in folders:
    print(f.name)

if len(folders) < 2:
    print("\nNeed at least 2 trading days for backtest.")
    exit()

# =====================================================
# SELECT BACKTEST PAIR
# =====================================================

import sys

# =====================================================
# SELECT BACKTEST PAIR
# =====================================================

if len(sys.argv) > 1:
    PAIR_INDEX = int(sys.argv[1])
else:
    PAIR_INDEX = 0

if PAIR_INDEX >= len(folders) - 1:
    print("Invalid Pair Index")
    exit()

scanner_folder = folders[PAIR_INDEX]
next_day_folder = folders[PAIR_INDEX + 1]

print(f"\nTotal History Folders : {len(folders)}")

print(f"\nBacktest Pair : {PAIR_INDEX + 1}")

print("\nScanner Folder :")
print(scanner_folder.name)

print("\nNext Day Folder :")
print(next_day_folder.name)

scanner_file = scanner_folder / "BULLISH_SCANNER.xlsx"
bearish_file = scanner_folder / "BEARISH_SCANNER.xlsx"
master_file = next_day_folder / "MASTER.xlsx"

print("\nLoading Scanner...")
print(scanner_file)

print("\nLoading Bearish Scanner...")
print(bearish_file)

print("\nLoading MASTER...")
print(master_file)

scanner = pd.read_excel(scanner_file)
bearish = pd.read_excel(bearish_file)
master = pd.read_excel(master_file)

print("\nScanner Rows :", len(scanner))
print("Bearish Rows :", len(bearish))
print("MASTER Rows  :", len(master))

print("\nScanner Rows :", len(scanner))
print("Bearish Rows :", len(bearish))
print("MASTER Rows  :", len(master))

print("\nMASTER Columns")
print(master.columns.tolist())
# =====================================================
# Keep only required MASTER columns
# =====================================================

master = master[[
    "SYMBOL",
    "%CHNG",
    "OPEN",
    "HIGH",
    "LOW",
    "LTP"
]]

master = master.rename(
    columns={
        "%CHNG": "% CHANGE"
    }
)

print("\nMASTER Ready")
print(master.head())
# =====================================================
# REMOVE INDEX ROWS
# =====================================================

before = len(master)

master = master.dropna(subset=["% CHANGE"])

after = len(master)

print(f"\nMASTER Clean Rows : {after}")
print(f"Removed Rows      : {before-after}")
# =====================================================
# MERGE SCANNER WITH MASTER
# =====================================================

print("\nMerging Scanner with MASTER...")

backtest = scanner.merge(
    master,
    on="SYMBOL",
    how="left"
)
# =====================================================
# MERGE BEARISH WITH MASTER
# =====================================================

bear_backtest = bearish.merge(
    master,
    on="SYMBOL",
    how="left"
)

print("\nBearish Merge Completed")
print("Rows :", len(bear_backtest))

print("\nBearish Sample")
print(
    bear_backtest[
        [
            "SYMBOL",
            "R Factor",
            "% CHANGE"
        ]
    ].head(10)
)
print("Merge Completed")
print("Rows :", len(backtest))

print("\nMerged Sample")
print(
    backtest[
        [
            "SYMBOL",
            "R Factor",
            "% CHANGE"
        ]
    ].head(10)
)
# =====================================================
# BACKTEST RULE
# =====================================================

BULLISH_TARGET = 3.0

backtest["Result"] = "MISS"

backtest.loc[
    backtest["% CHANGE"] >= BULLISH_TARGET,
    "Result"
] = "HIT"
# =====================================================
# BULLISH ACCURACY
# =====================================================

total_signals = len(backtest)

total_hits = (backtest["Result"] == "HIT").sum()

total_miss = (backtest["Result"] == "MISS").sum()

accuracy = round(
    (total_hits / total_signals) * 100,
    2
)

print("\n" + "=" * 50)
print("BULLISH BACKTEST SUMMARY")
print("=" * 50)

print(f"Total Signals : {total_signals}")
print(f"Hits          : {total_hits}")
print(f"Miss          : {total_miss}")
print(f"Accuracy      : {accuracy}%")
# =====================================================
# BEARISH BACKTEST
# =====================================================

BEARISH_TARGET = -3.0

bear_backtest["Result"] = "MISS"

bear_backtest.loc[
    bear_backtest["% CHANGE"] <= BEARISH_TARGET,
    "Result"
] = "HIT"

bear_total = len(bear_backtest)

bear_hits = (bear_backtest["Result"] == "HIT").sum()

bear_miss = (bear_backtest["Result"] == "MISS").sum()

bear_accuracy = round(
    (bear_hits / bear_total) * 100,
    2
)

print("\n" + "=" * 50)
print("BEARISH BACKTEST SUMMARY")
print("=" * 50)

print(f"Total Signals : {bear_total}")
print(f"Hits          : {bear_hits}")
print(f"Miss          : {bear_miss}")
print(f"Accuracy      : {bear_accuracy}%")
# =====================================================
# OVERALL SUMMARY
# =====================================================

overall_signals = total_signals + bear_total
overall_hits = total_hits + bear_hits
overall_miss = total_miss + bear_miss

overall_accuracy = round(
    (overall_hits / overall_signals) * 100,
    2
)

print("\n" + "=" * 50)
print("TRADEFINDER V1 SUMMARY")
print("=" * 50)

print(f"Bullish Accuracy : {accuracy}%")
print(f"Bearish Accuracy : {bear_accuracy}%")
print("-" * 50)
print(f"Overall Signals  : {overall_signals}")
print(f"Overall Hits     : {overall_hits}")
print(f"Overall Miss     : {overall_miss}")
print(f"Overall Accuracy : {overall_accuracy}%")
print("=" * 50)
# =====================================================
# CREATE BACKTEST REPORT
# =====================================================

bull_report = backtest.copy()
bull_report["Signal"] = "Bullish"

bear_report = bear_backtest.copy()
bear_report["Signal"] = "Bearish"

report = pd.concat(
    [bull_report, bear_report],
    ignore_index=True
)

report = report[
    [
        "Signal",
        "Rank",
        "SYMBOL",
        "R Factor",
        "% CHANGE",
        "Result"
    ]
]

OUTPUT_FILE = BASE / "Output" / "BACKTEST.xlsx"

report.to_excel(
    OUTPUT_FILE,
    index=False
)

print("\nBACKTEST Report Saved")
print(OUTPUT_FILE)
save_to_history(
    OUTPUT_FILE,
    "BACKTEST.xlsx"
)
