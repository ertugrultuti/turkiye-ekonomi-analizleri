import pandas as pd
import numpy as np
df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
data = df[["bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]].dropna()
print(data.shape)
print(data.head())