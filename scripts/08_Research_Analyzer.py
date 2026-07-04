from pathlib import Path
import pandas as pd

print("=" * 60)
print("TRADEFINDER V1 - RESEARCH ANALYZER")
print("=" * 60)

BASE = Path(__file__).resolve().parent.parent

OUTPUT = BASE / "Output"

captured_bull = pd.read_excel(
    OUTPUT / "CAPTURED_BULLISH.xlsx"
)

missed_bull = pd.read_excel(
    OUTPUT / "MISSED_BULLISH.xlsx"
)

captured_bear = pd.read_excel(
    OUTPUT / "CAPTURED_BEARISH.xlsx"
)

missed_bear = pd.read_excel(
    OUTPUT / "MISSED_BEARISH.xlsx"
)

print(
    "Captured Bull :",
    len(captured_bull)
)

print(
    "Missed Bull :",
    len(missed_bull)
)

print(
    "Captured Bear :",
    len(captured_bear)
)

print(
    "Missed Bear :",
    len(missed_bear)
)

# ==========================================================
# REQUIRED COLUMNS
# ==========================================================

factors = [

    "R Factor",
    "Price Score",
    "OI Score",
    "Conviction Score",
    "Momentum Score",

]

analysis_rows = []
# ==========================================================
# BULLISH ANALYSIS
# ==========================================================

for factor in factors:

    captured_avg = round(
        captured_bull[factor].mean(),
        2
    )

    missed_avg = round(
        missed_bull[factor].mean(),
        2
    )

    analysis_rows.append(
        {
            "Side": "Bullish",
            "Factor": factor,
            "Captured Avg": captured_avg,
            "Missed Avg": missed_avg,
            "Difference": round(
                captured_avg - missed_avg,
                2
            ),
        }
    )

# ==========================================================
# BEARISH ANALYSIS
# ==========================================================

for factor in factors:

    captured_avg = round(
        captured_bear[factor].mean(),
        2
    )

    missed_avg = round(
        missed_bear[factor].mean(),
        2
    )

    analysis_rows.append(
        {
            "Side": "Bearish",
            "Factor": factor,
            "Captured Avg": captured_avg,
            "Missed Avg": missed_avg,
            "Difference": round(
                captured_avg - missed_avg,
                2
            ),
        }
    )

analysis = pd.DataFrame(
    analysis_rows
)

print()
print(analysis)
# ==========================================================
# TOP MISSED MOVERS
# ==========================================================

top_missed_bull = missed_bull.sort_values(
    "% CHANGE",
    ascending=False
)

top_missed_bear = missed_bear.sort_values(
    "% CHANGE",
    ascending=True
)

# ==========================================================
# SAVE REPORT
# ==========================================================

output_file = (
    OUTPUT /
    "RESEARCH_ANALYSIS.xlsx"
)

with pd.ExcelWriter(output_file) as writer:

    analysis.to_excel(
        writer,
        sheet_name="Factor Analysis",
        index=False
    )

    top_missed_bull.to_excel(
        writer,
        sheet_name="Top Missed Bull",
        index=False
    )

    top_missed_bear.to_excel(
        writer,
        sheet_name="Top Missed Bear",
        index=False
    )

    captured_bull.to_excel(
        writer,
        sheet_name="Captured Bull",
        index=False
    )

    captured_bear.to_excel(
        writer,
        sheet_name="Captured Bear",
        index=False
    )

print("\n" + "=" * 60)
print("RESEARCH ANALYSIS COMPLETED")
print("=" * 60)

print("\nSaved :")
print(output_file)

print("=" * 60)