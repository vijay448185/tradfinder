from pathlib import Path
from datetime import datetime
import subprocess
import sys
import pandas as pd

print("=" * 60)
print("TRADEFINDER V3 - MULTI BACKTEST")
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

pairs = []

print("\n" + "=" * 60)
print("VALID BACKTEST PAIRS")
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
            i,
            scanner_folder,
            next_day_folder
        )
    )

print("\n" + "=" * 60)
print(f"Valid Pairs : {len(pairs)}")
print("=" * 60)
results = []

print("\nStarting Backtests...")

for n, (pair_index, scanner_folder, next_day_folder) in enumerate(
    pairs,
    start=1
):

    print("\n" + "=" * 60)
    print(f"Processing {n}/{len(pairs)}")
    print(
        f"{scanner_folder.name} -> "
        f"{next_day_folder.name}"
    )
    print("=" * 60)

    result = subprocess.run(
    [
        sys.executable,
        str(BASE / "scripts" / "05_Backtest.py"),
        scanner_folder.name,
        next_day_folder.name
    ]
)

    if result.returncode != 0:

        print(f"FAILED : {pair_index}")
        print(
            f"{scanner_folder.name} -> "
            f"{next_day_folder.name}"
        )

        continue

    summary_file = (
        OUTPUT /
        "BACKTEST_SUMMARY.xlsx"
    )

    if not summary_file.exists():

        print(
            f"Summary Missing : "
            f"{scanner_folder.name}"
        )

        continue

    summary = pd.read_excel(
        summary_file
    )

    results.append(summary)

    print(summary[["Scanner Date", "Next Date"]])

print(f"SUCCESS : {pair_index}")
print(f"Rows Added : {len(results)}")

if len(results) == 0:

    print("\nNo Results Generated.")
    sys.exit()

final = pd.concat(
    results,
    ignore_index=True
)

output_file = (
    OUTPUT /
    "MULTI_BACKTEST.xlsx"
)

final.to_excel(
    output_file,
    index=False
)

print("\n" + "=" * 60)
print("MULTI BACKTEST COMPLETED")
print("=" * 60)

print(
    f"History Folders : "
    f"{len(folders)}"
)

print(
    f"Valid Pairs     : "
    f"{len(pairs)}"
)

print(
    f"Pairs Tested    : "
    f"{len(final)}"
)

print(
    f"Average Bull Accuracy : "
    f"{round(final['Bull Accuracy'].mean(), 2)}%"
)

print(
    f"Average Bear Accuracy : "
    f"{round(final['Bear Accuracy'].mean(), 2)}%"
)

print(
    f"Average Overall Accuracy : "
    f"{round(final['Overall Accuracy'].mean(), 2)}%"
)

print("\nSaved :")
print(output_file)