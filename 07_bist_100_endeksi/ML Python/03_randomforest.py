import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")

df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds", "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df = df.dropna()
df = df.reset_index(drop=True)

X = df[["fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]]
y = df["bist_ret"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

lasso = LassoCV(cv=5, random_state=42, max_iter=10000)
lasso.fit(X_scaled, y)

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

rf = RandomForestRegressor(n_estimators=500, random_state=42)
rf.fit(X_scaled, y)

import shap

explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_scaled)

mean_shap = np.abs(shap_values).mean(axis=0)
print("\nSHAP değerleri (ortalama mutlak etki):")
for name, val in sorted(zip(X.columns, mean_shap), key=lambda x: -x[1]):
    print(f"  {name}: {val:.6f}")
