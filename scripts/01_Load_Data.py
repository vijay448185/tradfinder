from pathlib import Path
import pandas as pd
import zipfile

BASE = Path(__file__).resolve().parent.parent

BHAV = BASE / "Input" / "Bhavcopy"
FUT = BASE / "Input" / "Futures"
OI = BASE / "Input" / "OI"
MW = BASE / "Input" / "MW"
OUT = BASE / "Output"
print("Loading Bhavcopy...")

with zipfile.ZipFile(list(BHAV.glob("*.zip"))[0]) as z:
    print(z.namelist())
    exit()print("Loading Bhavcopy...")

with zipfile.ZipFile(list(BHAV.glob("*.zip"))[0]) as z:
    print(z.namelist())
    exit()

with zipfile.ZipFile(list(BHAV.glob("*.zip"))[0]) as z:
    csv = [x for x in z.namelist() if x.endswith(".csv")][0]
    bhav = pd.read_csv(z.open(csv))
print("\nBhavcopy Segments:")
print(bhav["Sgmt"].value_counts())

print("\nFirst 20 Symbols:")
print(bhav["TckrSymb"].head(20).tolist())

exit()
print("Loading Futures...")

with zipfile.ZipFile(list(FUT.glob("*.zip"))[0]) as z:
    csv = [x for x in z.namelist() if x.endswith(".csv")][0]
    fut = pd.read_csv(z.open(csv))

print("Loading OI...")
oi = pd.read_csv(list(OI.glob("*.csv"))[0])

print("Loading MW...")
mw = pd.read_csv(list(MW.glob("*.csv"))[0])

# Clean column names
bhav.columns = bhav.columns.str.strip()
fut.columns = fut.columns.str.strip()
oi.columns = oi.columns.str.strip()
mw.columns = mw.columns.str.strip()

# Rename symbols
bhav.rename(columns={"TckrSymb":"SYMBOL"}, inplace=True)
fut.rename(columns={"NSE Symbol":"SYMBOL"}, inplace=True)
oi.rename(columns={"Symbol":"SYMBOL"}, inplace=True)

# Uppercase
for df in [bhav,fut,oi,mw]:
    df.columns = df.columns.str.strip()

bhav["SYMBOL"]=bhav["SYMBOL"].astype(str).str.upper().str.strip()
fut["SYMBOL"]=fut["SYMBOL"].astype(str).str.upper().str.strip()
oi["SYMBOL"]=oi["SYMBOL"].astype(str).str.upper().str.strip()
mw["SYMBOL"]=mw["SYMBOL"].astype(str).str.upper().str.strip()

# Merge
master = bhav.merge(oi,on="SYMBOL",how="left")
master = master.merge(fut,on="SYMBOL",how="left")
master = master.merge(mw,on="SYMBOL",how="left")

OUT.mkdir(exist_ok=True)

master.to_excel(OUT/"MASTER.xlsx",index=False)

print("="*60)
print("MASTER CREATED")
print(master.shape)
print("="*60)