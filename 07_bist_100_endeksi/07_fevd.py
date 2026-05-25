import pandas as pd
import numpy as np
from statsmodels.tsa.vector_ar.var_model import VAR
import matplotlib.pyplot as plt
df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
data = df[["bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]].dropna()
model = VAR(data)
lag_result = model.select_order(maxlags=12)
optimal_lag = lag_result.selected_orders["aic"]
var_model = model.fit(optimal_lag)
fevd = var_model.fevd(periods=12)
fevd_df = pd.DataFrame(
    fevd.decomp[var_model.names.index("bist_ret")],
    columns=var_model.names
)
fevd_df.index = range(1, 13)
print(fevd_df.round(4))