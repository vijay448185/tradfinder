from pathlib import Path
from datetime import datetime
import sys
import pandas as pd

from utils import normalize_columns

print("=" * 60)
print("TRADEFINDER V4 - RESEARCH BACKTEST")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

HISTORY = BASE / "History"
OUTPUT = BASE / "Output"

folders = sorted(
    [
        x
        for x in HISTORY.iterdir()
        if x.is_dir()
    ]
)

print(f"\nHistory Folders : {len(folders)}")

if len(folders) < 2:
    print("\nNeed at least 2 folders.")
    sys.exit()

# ==========================================================
# BUILD VALID PAIRS
# ==========================================================

pairs = []

print("\n" + "=" * 60)
print("VALID RESEARCH PAIRS")
print("=" * 60)

for i in range(len(folders) - 1):

    scanner_folder = folders[i]
    next_day_folder = folders[i + 1]

    d1 = datetime.strptime(
        scanner_folder.name,
        "%Y-%m-%d"
    )

    d2 = datetime.strptime(
        next_day_folder.name,
        "%Y-%m-%d"
    )

    gap = (d2 - d1).days

    if gap > 5:

        print(
            f"SKIP : "
            f"{scanner_folder.name}"
            f" -> "
            f"{next_day_folder.name}"
        )

        continue

    pairs.append(
        (
            scanner_folder,
            next_day_folder
        )
    )

print("\n" + "=" * 60)
print(f"Valid Pairs : {len(pairs)}")
print("=" * 60)

results = []

print("\nStarting Research...\n")

# ==========================================================
# MAIN LOOP
# ==========================================================

for n, (
    scanner_folder,
    next_day_folder
) in enumerate(
    pairs,
    start=1
):

    print("=" * 60)
    print(
        f"Processing "
        f"{n}/{len(pairs)}"
    )

    print(
        f"{scanner_folder.name}"
        f" -> "
        f"{next_day_folder.name}"
    )

    print("=" * 60)

    bull_file = (
        scanner_folder /
        "BULLISH_SCANNER.xlsx"
    )

    bear_file = (
        scanner_folder /
        "BEARISH_SCANNER.xlsx"
    )

    rf_file = (
        scanner_folder /
        "R_FACTOR.xlsx"
    )

    master_file = (
        next_day_folder /
        "MASTER.xlsx"
    )

    required_files = [
        bull_file,
        bear_file,
        rf_file,
        master_file
    ]

    missing = [
        f.name
        for f in required_files
        if not f.exists()
    ]

    if missing:

        print(
            "Missing Files :",
            ", ".join(missing)
        )

        continue

    bullish = pd.read_excel(
        bull_file
    )

    bearish = pd.read_excel(
        bear_file
    )

    rf = pd.read_excel(
        rf_file
    )

    master = pd.read_excel(
        master_file
    )

    master = normalize_columns(
        master
    )
        # ==========================================================
    # CHECK REQUIRED COLUMN
    # ==========================================================

    if "% CHANGE" not in master.columns:

        print("\nMASTER Columns :")

        for col in master.columns:
            print(col)

        print("\nMissing Column : % CHANGE")

        continue

    master["% CHANGE"] = (
        master["% CHANGE"]
        .astype(str)
        .str.replace(
            ",",
            "",
            regex=False
        )
    )

    master["% CHANGE"] = pd.to_numeric(
        master["% CHANGE"],
        errors="coerce"
    )

    # ==========================================================
    # FIND NEXT DAY MOVERS
    # ==========================================================

    bull_movers = master[
        master["% CHANGE"] >= 3
    ].copy()

    bear_movers = master[
        master["% CHANGE"] <= -3
    ].copy()

    print(
        f"Bull Movers : {len(bull_movers)}"
    )

    print(
        f"Bear Movers : {len(bear_movers)}"
    )

    # ==========================================================
    # CAPTURED MOVERS
    # ==========================================================

    captured_bull = bull_movers.merge(
        bullish[
            [
                "SYMBOL",
                "Rank",
                "R Factor"
            ]
        ],
        on="SYMBOL",
        how="inner"
    )

    captured_bear = bear_movers.merge(
        bearish[
            [
                "SYMBOL",
                "Rank",
                "R Factor"
            ]
        ],
        on="SYMBOL",
        how="inner"
    )

    print(
        f"Captured Bull : {len(captured_bull)}"
    )

    print(
        f"Captured Bear : {len(captured_bear)}"
    )

    # ==========================================================
    # MISSED MOVERS
    # ==========================================================

    missed_bull = bull_movers[
        ~bull_movers["SYMBOL"].isin(
            bullish["SYMBOL"]
        )
    ].copy()

    missed_bear = bear_movers[
        ~bear_movers["SYMBOL"].isin(
            bearish["SYMBOL"]
        )
    ].copy()

    missed_bull = missed_bull.merge(
        rf,
        on="SYMBOL",
        how="left"
    )

    missed_bear = missed_bear.merge(
        rf,
        on="SYMBOL",
        how="left"
    )

    print(
        f"Missed Bull : {len(missed_bull)}"
    )

    print(
        f"Missed Bear : {len(missed_bear)}"
    )

    bull_capture_pct = 0

    if len(bull_movers):

        bull_capture_pct = round(
            len(captured_bull)
            * 100
            / len(bull_movers),
            2
        )

    bear_capture_pct = 0

    if len(bear_movers):

        bear_capture_pct = round(
            len(captured_bear)
            * 100
            / len(bear_movers),
            2
        )
    print(
        f"Bull Capture % : "
        f"{bull_capture_pct}%"
    )

    print(
        f"Bear Capture % : "
        f"{bear_capture_pct}%"
    )

    # ==========================================================
    # SAVE RESULT
    # ==========================================================

    results.append(
        {
            "Scanner Date": scanner_folder.name,
            "Next Date": next_day_folder.name,

            "Bull Movers": len(bull_movers),
            "Bull Captured": len(captured_bull),
            "Bull Missed": len(missed_bull),
            "Bull Capture %": bull_capture_pct,

            "Bear Movers": len(bear_movers),
            "Bear Captured": len(captured_bear),
            "Bear Missed": len(missed_bear),
            "Bear Capture %": bear_capture_pct,

            "Average Missed Bull RF":
                round(
                    missed_bull["R Factor"].mean(),
                    2
                ) if len(missed_bull) else 0,

            "Average Missed Bear RF":
                round(
                    missed_bear["R Factor"].mean(),
                    2
                ) if len(missed_bear) else 0,
        }
    )

    print("-" * 60)
    print("Completed")
    print("-" * 60)

# ==========================================================
# CREATE REPORT
# ==========================================================

if len(results) == 0:

    print("\nNo Results Generated.")
    sys.exit()

final = pd.DataFrame(
    results
)

OUTPUT.mkdir(
    exist_ok=True
)

output_file = (
    OUTPUT /
    "RESEARCH_SUMMARY.xlsx"
)

final.to_excel(
    output_file,
    index=False
)

print("\n" + "=" * 60)
print("TRADEFINDER V4 - RESEARCH COMPLETED")
print("=" * 60)

print(
    f"History Folders : {len(folders)}"
)

print(
    f"Valid Pairs     : {len(pairs)}"
)

print(
    f"Pairs Tested    : {len(final)}"
)

print(
    f"Average Bull Capture % : "
    f"{round(final['Bull Capture %'].mean(),2)}%"
)

print(
    f"Average Bear Capture % : "
    f"{round(final['Bear Capture %'].mean(),2)}%"
)

print(
    f"Average Missed Bull RF : "
    f"{round(final['Average Missed Bull RF'].mean(),2)}"
)

print(
    f"Average Missed Bear RF : "
    f"{round(final['Average Missed Bear RF'].mean(),2)}"
)

print("\nSaved :")
print(output_file)

print("=" * 60)