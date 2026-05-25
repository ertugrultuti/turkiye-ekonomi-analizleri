import pandas as pd
import numpy as np
from statsmodels.tsa.vector_ar.var_model import VAR
df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
data = df[["bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]].dropna()
model = VAR(data)
lag_result = model.select_order(maxlags=12)
optimal_lag = lag_result.selected_orders["aic"]
print(f"Optimal lag (AIC): {optimal_lag}")
var_model = model.fit(optimal_lag)
print(var_model.summary())