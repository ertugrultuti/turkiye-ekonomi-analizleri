import pandas as pd
import numpy as np
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.stattools import grangercausalitytests
df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
data = df[["bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]].dropna()
model = VAR(data)
lag_result = model.select_order(maxlags=12)
optimal_lag = lag_result.selected_orders["aic"]
for col in ["fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]:
    print(f"--- {col} -> bist_ret ---")
    grangercausalitytests(data[["bist_ret", col]], maxlag=optimal_lag, verbose=True)