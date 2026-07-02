from pathlib import Path
import shutil
import re
import subprocess
import sys
print("=" * 60)
print("TRADEFINDER V2 - BUILD HISTORY")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------
# SOURCE
# ----------------------------------------------------------

SOURCE_DAILY = BASE / "Data" / "Daily"
SOURCE_OI = BASE / "Data" / "OI"
SOURCE_MW = BASE / "Data" / "MW"

# ----------------------------------------------------------
# INPUT
# ----------------------------------------------------------

INPUT_DAILY = BASE / "Input" / "Daily"
INPUT_OI = BASE / "Input" / "OI"
INPUT_MW = BASE / "Input" / "MW"


def clear_folder(folder):
    for f in folder.glob("*"):
        if f.is_file():
            f.unlink()


def extract_date(filename):

    name = filename.upper()

    m = re.search(r"(\d{2})(\d{2})(\d{4})", name)

    if m:
        d, mth, y = m.groups()
        return f"{y}-{mth}-{d}"

    m = re.search(r"(\d{2})-([A-Z]{3})-(\d{4})", name)

    if m:

        d, mon, y = m.groups()

        months = {
            "JAN": "01",
            "FEB": "02",
            "MAR": "03",
            "APR": "04",
            "MAY": "05",
            "JUN": "06",
            "JUL": "07",
            "AUG": "08",
            "SEP": "09",
            "OCT": "10",
            "NOV": "11",
            "DEC": "12",
        }

        return f"{y}-{months[mon]}-{d}"

    return None


print("\nChecking folders...")

for folder in [
    SOURCE_DAILY,
    SOURCE_OI,
    SOURCE_MW,
    INPUT_DAILY,
    INPUT_OI,
    INPUT_MW,
]:
    if not folder.exists():
        print("Missing :", folder)
        exit()

print("All folders found.")

daily_files = sorted(SOURCE_DAILY.glob("*"))
oi_files = sorted(SOURCE_OI.glob("*"))
mw_files = sorted(SOURCE_MW.glob("*"))

print("\nDaily :", len(daily_files))
print("OI    :", len(oi_files))
print("MW    :", len(mw_files))

daily_map = {}
oi_map = {}
mw_map = {}

for f in daily_files:
    dt = extract_date(f.name)
    if dt:
        daily_map[dt] = f

for f in oi_files:
    dt = extract_date(f.name)
    if dt:
        oi_map[dt] = f

for f in mw_files:
    dt = extract_date(f.name)
    if dt:
        mw_map[dt] = f

all_dates = sorted(
    set(daily_map.keys())
    | set(oi_map.keys())
    | set(mw_map.keys())
)

valid = 0

print("\n" + "=" * 60)
print("DATE MATCH REPORT")
print("=" * 60)
count = 0
total = valid
for dt in all_dates:

    d = dt in daily_map
    o = dt in oi_map
    m = dt in mw_map

    if d and o and m:

        valid += 1

        print(
            f"{dt}  D:Y  O:Y  M:Y  OK"
        )

print("\nValid Trading Days :", valid)

# ----------------------------------------------------------
# TEST COPY
# ----------------------------------------------------------

count = 0
total = valid

for dt in all_dates:

    if dt not in daily_map:
        continue

    if dt not in oi_map:
        continue

    if dt not in mw_map:
        continue

    count += 1

    clear_folder(INPUT_DAILY)
    clear_folder(INPUT_OI)
    clear_folder(INPUT_MW)

    shutil.copy2(
        daily_map[dt],
        INPUT_DAILY / daily_map[dt].name,
    )

    shutil.copy2(
        oi_map[dt],
        INPUT_OI / oi_map[dt].name,
    )

    shutil.copy2(
        mw_map[dt],
        INPUT_MW / mw_map[dt].name,
    )

    print("\n" + "=" * 60)
    print(f"Processing {count}/{total}")
    print(f"Date : {dt}")
    print("=" * 60)

    print("Daily :", daily_map[dt].name)
    print("OI    :", oi_map[dt].name)
    print("MW    :", mw_map[dt].name)

    print("\nRunning Pipeline...\n")

    result = subprocess.run(
        [
            sys.executable,
            str(BASE / "scripts" / "00_Run_All.py")
        ]
    )

    if result.returncode != 0:
        print(f"FAILED : {dt}")
        continue

    history_folder = BASE / "History" / dt

    required = [
        "MASTER.xlsx",
        "FEATURES.xlsx",
        "R_FACTOR.xlsx",
        "BULLISH_SCANNER.xlsx",
        "BEARISH_SCANNER.xlsx",
    ]

    missing = []

    for file in required:
        if not (history_folder / file).exists():
            missing.append(file)

    if missing:
        print(f"\n❌ VERIFY FAILED : {dt}")
        print("Missing :", ", ".join(missing))
    else:
        print(f"\n✅ VERIFIED : {dt}")

print("\n" + "=" * 60)
print("BUILD HISTORY COMPLETED")
print("=" * 60)
print(f"Processed : {count}")