from pathlib import Path
from datetime import datetime
import sys
import pandas as pd

from utils import normalize_columns

print("=" * 60)
print("TRADEFINDER V6 - RESEARCH BACKTEST")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

HISTORY = BASE / "History"
OUTPUT = BASE / "Output"

OUTPUT.mkdir(
    exist_ok=True
)

folders = sorted(
    [
        f
        for f in HISTORY.iterdir()
        if f.is_dir()
    ]
)

print(
    f"History Folders : "
    f"{len(folders)}"
)

if len(folders) < 2:

    print("Need at least 2 folders.")
    sys.exit()

# ==========================================================
# VALID PAIRS
# ==========================================================

pairs = []

for i in range(len(folders) - 1):

    scanner = folders[i]
    next_day = folders[i + 1]

    d1 = datetime.strptime(
        scanner.name,
        "%Y-%m-%d"
    )

    d2 = datetime.strptime(
        next_day.name,
        "%Y-%m-%d"
    )

    if (d2 - d1).days > 5:
        continue

    required = [

        scanner / "BULLISH_SCANNER.xlsx",
        scanner / "BEARISH_SCANNER.xlsx",
        scanner / "R_FACTOR.xlsx",
        next_day / "MASTER.xlsx",

    ]

    if not all(
        x.exists()
        for x in required
    ):
        continue

    pairs.append(
        (
            scanner,
            next_day
        )
    )

print(
    f"Valid Pairs : "
    f"{len(pairs)}"
)

summary_rows = []

captured_bull_all = []
captured_bear_all = []

missed_bull_all = []
missed_bear_all = []

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

    print("\n" + "=" * 60)
    print(
        f"{n}/{len(pairs)}"
    )

    print(
        scanner_folder.name,
        "->",
        next_day_folder.name
    )

    print("=" * 60)

    bullish = pd.read_excel(
        scanner_folder /
        "BULLISH_SCANNER.xlsx"
    )

    bearish = pd.read_excel(
        scanner_folder /
        "BEARISH_SCANNER.xlsx"
    )

    rf = pd.read_excel(
        scanner_folder /
        "R_FACTOR.xlsx"
    )

    master = pd.read_excel(
        next_day_folder /
        "MASTER.xlsx"
    )

    master = normalize_columns(
        master
    )
        # ==========================================================
    # NEXT DAY MOVERS
    # ==========================================================

    if "% CHANGE" not in master.columns:

        print("Missing Column : % CHANGE")
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

    bull_movers = master[
        master["% CHANGE"] >= 3
    ].copy()

    bear_movers = master[
        master["% CHANGE"] <= -3
    ].copy()

    # ==========================================================
    # CAPTURED
    # ==========================================================

    captured_bull = bull_movers.merge(
        bullish[
            [
                "SYMBOL"
            ]
        ],
        on="SYMBOL",
        how="inner"
    )

    captured_bear = bear_movers.merge(
        bearish[
            [
                "SYMBOL"
            ]
        ],
        on="SYMBOL",
        how="inner"
    )

    # ==========================================================
    # IMPORTANT
    # MERGE COMPLETE R_FACTOR DATA
    # ==========================================================

    captured_bull = captured_bull.merge(
        rf,
        on="SYMBOL",
        how="left"
    )

    captured_bear = captured_bear.merge(
        rf,
        on="SYMBOL",
        how="left"
    )

    # ==========================================================
    # MISSED
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

    # ==========================================================
    # DATE TAG
    # ==========================================================

    for df_temp in [

        captured_bull,
        captured_bear,
        missed_bull,
        missed_bear,

    ]:

        df_temp.insert(
            0,
            "Scanner Date",
            scanner_folder.name
        )

        df_temp.insert(
            1,
            "Next Date",
            next_day_folder.name
        )
        bull_capture = 0

    if len(bull_movers):

        bull_capture = round(
            len(captured_bull)
            * 100
            / len(bull_movers),
            2
        )

    bear_capture = 0

    if len(bear_movers):

        bear_capture = round(
            len(captured_bear)
            * 100
            / len(bear_movers),
            2
        )

    summary_rows.append(
        {
            "Scanner Date": scanner_folder.name,
            "Next Date": next_day_folder.name,

            "Bull Movers": len(bull_movers),
            "Bull Captured": len(captured_bull),
            "Bull Missed": len(missed_bull),
            "Bull Capture %": bull_capture,

            "Bear Movers": len(bear_movers),
            "Bear Captured": len(captured_bear),
            "Bear Missed": len(missed_bear),
            "Bear Capture %": bear_capture,
        }
    )

    captured_bull_all.append(captured_bull)
    captured_bear_all.append(captured_bear)

    missed_bull_all.append(missed_bull)
    missed_bear_all.append(missed_bear)

# ==========================================================
# SAVE REPORTS
# ==========================================================

summary = pd.DataFrame(summary_rows)

summary.to_excel(
    OUTPUT / "RESEARCH_SUMMARY.xlsx",
    index=False
)

pd.concat(
    captured_bull_all,
    ignore_index=True
).to_excel(
    OUTPUT / "CAPTURED_BULLISH.xlsx",
    index=False
)

pd.concat(
    captured_bear_all,
    ignore_index=True
).to_excel(
    OUTPUT / "CAPTURED_BEARISH.xlsx",
    index=False
)

pd.concat(
    missed_bull_all,
    ignore_index=True
).to_excel(
    OUTPUT / "MISSED_BULLISH.xlsx",
    index=False
)

pd.concat(
    missed_bear_all,
    ignore_index=True
).to_excel(
    OUTPUT / "MISSED_BEARISH.xlsx",
    index=False
)

print("\n" + "=" * 60)
print("RESEARCH COMPLETED")
print("=" * 60)

print(
    f"Pairs Tested : {len(summary)}"
)

print("\nSaved :")
print("RESEARCH_SUMMARY.xlsx")
print("CAPTURED_BULLISH.xlsx")
print("CAPTURED_BEARISH.xlsx")
print("MISSED_BULLISH.xlsx")
print("MISSED_BEARISH.xlsx")

print("=" * 60)
