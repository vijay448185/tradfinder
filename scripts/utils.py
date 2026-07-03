from pathlib import Path
from shutil import copy2
import re


def get_trading_date(filename):

    m = re.search(r"(\d{2})(\d{2})(\d{4})", filename)

    if not m:
        raise ValueError(
            f"Trading date not found in filename: {filename}"
        )

    day, month, year = m.groups()

    return f"{year}-{month}-{day}"


def save_to_history(file_path, file_name):

    base = Path(__file__).resolve().parent.parent

    trading_date_file = base / "Output" / "trading_date.txt"

    with open(trading_date_file, "r") as f:
        trading_date = f.read().strip()

    history_folder = base / "History" / trading_date

    history_folder.mkdir(parents=True, exist_ok=True)

    copy2(file_path, history_folder / file_name)

    print("\nHistory Updated")
    print(history_folder)
    # ==========================================================
# COLUMN NORMALIZATION
# ==========================================================

def normalize_columns(df):

    # Remove newlines and extra spaces
    df.columns = (
        df.columns
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    rename_map = {
        "%CHNG": "% CHANGE",
        "% CHANGE": "% CHANGE",
        "VOLUME (shares)": "VOLUME (shares)",
        "VOLUME ( SHARES )": "VOLUME (shares)",
        "VOLUME ( SHARES)": "VOLUME (shares)",
        "VOLUME (shares )": "VOLUME (shares)",
        "VOLUME (shares ) ": "VOLUME (shares)",
        "VOLUME (shares)": "VOLUME (shares)",
        "VOLUME (shares )": "VOLUME (shares)",
        "VOLUME (shares)": "VOLUME (shares)",
    }

    df = df.rename(columns=rename_map)

    return df