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

print(f"En iyi alpha: {lasso.alpha_:.6f}")
print(f"R^2: {lasso.score(X_scaled, y):.4f}")
print("\nKatsayılar:")

for name, coef in zip(X.columns, lasso.coef_):
    print(f"{name}: {coef:.6f}")