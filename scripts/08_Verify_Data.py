from pathlib import Path
import re

print("=" * 60)
print("TRADEFINDER V2 - DATA VERIFICATION")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

DAILY = BASE / "Input" / "Daily"
OI = BASE / "Input" / "OI"
MW = BASE / "Input" / "MW"


def get_dates(folder):

    dates = {}

    for file in folder.iterdir():

        if not file.is_file():
            continue

        m = re.search(r"(\d{2})(\d{2})(\d{4})", file.name)

        if m:
            day, month, year = m.groups()
            dates[f"{year}-{month}-{day}"] = file.name

    return dates


daily = get_dates(DAILY)
oi = get_dates(OI)
mw = get_dates(MW)

all_dates = sorted(
    set(daily.keys()) |
    set(oi.keys()) |
    set(mw.keys())
)

print(f"\nTotal Dates Found : {len(all_dates)}\n")

valid = 0
invalid = 0

print(
    f'{"DATE":12} {"DAILY":7} {"OI":7} {"MW":7} STATUS'
)

print("-" * 60)

for d in all_dates:

    d_ok = d in daily
    o_ok = d in oi
    m_ok = d in mw

    status = "OK"

    if not (d_ok and o_ok and m_ok):
        status = "MISSING"
        invalid += 1
    else:
        valid += 1

    print(
        f"{d:12} "
        f"{'YES' if d_ok else 'NO':7}"
        f"{'YES' if o_ok else 'NO':7}"
        f"{'YES' if m_ok else 'NO':7}"
        f"{status}"
    )

print("\n" + "=" * 60)
print(f"Valid Dates   : {valid}")
print(f"Invalid Dates : {invalid}")
print("=" * 60)