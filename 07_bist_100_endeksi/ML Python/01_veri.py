import pandas as pd
import numpy as np

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")

df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df = df.dropna()
df = df.reset_index(drop=True)

X = df[["fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]]
y = df["bist_ret"]

print(df.shape)
print(X.describe())