from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("TRADEFINDER V2 - RUN ALL")
print("=" * 60)

BASE = Path(__file__).resolve().parent

scripts = [
    "01_Load_Data.py",
    "02_Feature_Engine.py",
    "03_R_Factor.py",
    "04_Scanner.py"
]

for script in scripts:

    print("\n" + "=" * 60)
    print(f"Running : {script}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(BASE / script)]
    )

    if result.returncode != 0:

        print(f"\nERROR : {script} Failed")
        exit()

print("\n" + "=" * 60)
print("ALL SCRIPTS COMPLETED SUCCESSFULLY")
print("=" * 60)