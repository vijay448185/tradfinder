from pathlib import Path

print("=" * 60)
print("TRADEFINDER V2 - MULTI BACKTEST")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

HISTORY = BASE / "History"

folders = sorted(
    [x for x in HISTORY.iterdir() if x.is_dir()]
)

print(f"\nHistory Folders : {len(folders)}")

if len(folders) < 2:
    print("Need at least 2 folders.")
    exit()

from datetime import datetime

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

    # Skip abnormal gaps
    if gap > 5:
        print(
            f"SKIP : "
            f"{scanner_folder.name} -> "
            f"{next_day_folder.name}"
        )
        continue

    pairs.append(
        (
            scanner_folder,
            next_day_folder
        )
    )

    print(
        f"{len(pairs):02d}. "
        f"{scanner_folder.name}"
        f" -> "
        f"{next_day_folder.name}"
    )

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"History Folders : {len(folders)}")
print(f"Backtest Pairs : {len(pairs)}")

print("\nFirst Pair")
print(pairs[0][0].name, "->", pairs[0][1].name)

print("\nLast Pair")
print(pairs[-1][0].name, "->", pairs[-1][1].name)