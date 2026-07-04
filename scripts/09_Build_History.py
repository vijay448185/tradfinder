from pathlib import Path
import shutil
import re
import subprocess
import sys

print("=" * 60)
print("TRADEFINDER V5 - BUILD HISTORY")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

SOURCE_DAILY = BASE / "Data" / "Daily"
SOURCE_OI = BASE / "Data" / "OI"
SOURCE_MW = BASE / "Data" / "MW"

INPUT_DAILY = BASE / "Input" / "Daily"
INPUT_OI = BASE / "Input" / "OI"
INPUT_MW = BASE / "Input" / "MW"

HISTORY = BASE / "History"


# ==========================================================
# SINGLE DATE SUPPORT
# ==========================================================

single_date = None

if len(sys.argv) >= 2:

    single_date = sys.argv[1]

    print(
        f"\nSingle Date Mode : "
        f"{single_date}"
    )


# ==========================================================
# FUNCTIONS
# ==========================================================

def clear_folder(folder):

    for f in folder.glob("*"):

        if f.is_file():

            f.unlink()


def extract_date(filename):

    filename = filename.upper()

    m = re.search(
        r"(\d{2})(\d{2})(\d{4})",
        filename
    )

    if m:

        d, mth, y = m.groups()

        return f"{y}-{mth}-{d}"

    m = re.search(
        r"(\d{2})-([A-Z]{3})-(\d{4})",
        filename
    )

    if not m:

        return None

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


print("\nChecking Folders...")

required = [

    SOURCE_DAILY,
    SOURCE_OI,
    SOURCE_MW,

    INPUT_DAILY,
    INPUT_OI,
    INPUT_MW,

]

for folder in required:

    if not folder.exists():

        print(
            "Missing :",
            folder
        )

        sys.exit()

print("Folders OK")

daily_map = {}
oi_map = {}
mw_map = {}

for f in SOURCE_DAILY.glob("*"):

    dt = extract_date(f.name)

    if dt:

        daily_map[dt] = f

for f in SOURCE_OI.glob("*"):

    dt = extract_date(f.name)

    if dt:

        oi_map[dt] = f

for f in SOURCE_MW.glob("*"):

    dt = extract_date(f.name)

    if dt:

        mw_map[dt] = f


all_dates = sorted(

    set(daily_map)
    |
    set(oi_map)
    |
    set(mw_map)

)

valid_dates = []

for dt in all_dates:

    if (
        dt in daily_map
        and
        dt in oi_map
        and
        dt in mw_map
    ):

        if single_date:

            if dt != single_date:

                continue

        valid_dates.append(dt)

print()

print(
    f"Trading Days : "
    f"{len(valid_dates)}"
)

count = 0
for dt in valid_dates:

    count += 1

    print("\n" + "=" * 60)
    print(
        f"Processing "
        f"{count}/{len(valid_dates)}"
    )
    print(f"Date : {dt}")
    print("=" * 60)

    clear_folder(INPUT_DAILY)
    clear_folder(INPUT_OI)
    clear_folder(INPUT_MW)

    shutil.copy2(
        daily_map[dt],
        INPUT_DAILY /
        daily_map[dt].name
    )

    shutil.copy2(
        oi_map[dt],
        INPUT_OI /
        oi_map[dt].name
    )

    shutil.copy2(
        mw_map[dt],
        INPUT_MW /
        mw_map[dt].name
    )

    print("\nRunning 00_Run_All.py\n")

    result = subprocess.run(
        [
            sys.executable,
            str(
                BASE /
                "scripts" /
                "00_Run_All.py"
            )
        ]
    )

    print(
        f"\nExit Code : "
        f"{result.returncode}"
    )

    history_folder = (
        HISTORY /
        dt
    )

    print("\nHistory Verification")
    print("-" * 60)

    required_files = [

        "MASTER.xlsx",
        "FEATURES.xlsx",
        "R_FACTOR.xlsx",
        "BULLISH_SCANNER.xlsx",
        "BEARISH_SCANNER.xlsx",

    ]

    missing = []

    for file in required_files:

        file_path = (
            history_folder /
            file
        )

        if file_path.exists():

            print(f"✓ {file}")

        else:

            print(f"✗ {file}")

            missing.append(file)

    if missing:

        print("\nFAILED")

        print(
            "Missing Files :"
        )

        for x in missing:

            print("-", x)

    else:

        print("\nVERIFIED")
        print("\n" + "=" * 60)
print("BUILD HISTORY COMPLETED")
print("=" * 60)

print(
    f"Processed : "
    f"{count}"
)

print(
    f"Verified  : "
    f"{len(valid_dates)}"
)

if single_date:

    print(
        f"\nSingle Date Completed : "
        f"{single_date}"
    )

print("\nFinished.")
print("=" * 60)