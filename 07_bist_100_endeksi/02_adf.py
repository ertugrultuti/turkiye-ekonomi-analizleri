import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
data = df[["bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]].dropna()
for col in data.columns:
    result = adfuller(data[col])
    print(f"{col}: ADF = {result[0]:.4f}, p-value = {result[1]:.4f}")