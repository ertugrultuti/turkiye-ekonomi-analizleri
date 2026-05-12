import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from itertools import product
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

# --- Veri ---
df = pd.read_excel("Veri.xlsx")
df.columns = ["Tarih", "Toplam", "Madencilik", "Imalat"]

def parse_quarter(s):
    yil, ceyrek = s.split("-")
    ay = {"1Ç": 1, "2Ç": 4, "3Ç": 7, "4Ç": 10}[ceyrek]
    return pd.Timestamp(int(yil), ay, 1)

df["Tarih"] = df["Tarih"].apply(parse_quarter)
df = df.set_index("Tarih")
df.index = pd.DatetimeIndex(df.index, freq="QS")

seriler = {
    "Toplam Sanayi": df["Toplam"],
    "Madencilik":    df["Madencilik"],
    "İmalat":        df["Imalat"],
}

# COVID dummy (2020 Q2)
covid_dummy = (df.index == "2020-04-01").astype(float)

# --- Grid Search ---
p_vals = range(0, 3)
d_vals = [1]
q_vals = range(0, 3)
P_vals = range(0, 2)
D_vals = [1]
Q_vals = range(0, 2)
s = 4

print("=" * 65)
print("SARIMA GRID SEARCH (d=1, D=1, s=4) — COVID dummy dahil")
print("=" * 65)

best_models = {}

for isim, seri in seriler.items():
    print(f"\n--- {isim} ---")
    results = []

    for p, d, q, P, D, Q in product(p_vals, d_vals, q_vals, P_vals, D_vals, Q_vals):
        try:
            model = SARIMAX(
                seri,
                order=(p, d, q),
                seasonal_order=(P, D, Q, s),
                exog=covid_dummy,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            fit = model.fit(disp=False)
            lb = acorr_ljungbox(fit.resid, lags=[8], return_df=True)
            lb_p = lb["lb_pvalue"].values[0]
            results.append({
                "order": (p, d, q),
                "seasonal": (P, D, Q, s),
                "AIC": round(fit.aic, 2),
                "BIC": round(fit.bic, 2),
                "LB_p": round(lb_p, 4),
            })
        except:
            continue

    res_df = pd.DataFrame(results).sort_values("AIC").reset_index(drop=True)
    print(res_df.head(10).to_string(index=False))

    # En iyi model: AIC en düşük + Ljung-Box p > 0.05
    gecerli = res_df[res_df["LB_p"] > 0.05]
    if len(gecerli) > 0:
        best = gecerli.iloc[0]
    else:
        best = res_df.iloc[0]
    
    best_models[isim] = {
        "order": best["order"],
        "seasonal": best["seasonal"],
        "AIC": best["AIC"],
        "BIC": best["BIC"],
        "LB_p": best["LB_p"],
    }
    print(f"\n>>> Seçilen model: SARIMA{best['order']}x{best['seasonal']}  "
          f"AIC={best['AIC']}  BIC={best['BIC']}  LB_p={best['LB_p']}")

print("\n" + "=" * 65)
print("ÖZET — Seçilen Modeller")
print("=" * 65)
for isim, m in best_models.items():
    print(f"{isim:20s}  SARIMA{m['order']}x{m['seasonal']}  "
          f"AIC={m['AIC']}  BIC={m['BIC']}  LB_p={m['LB_p']}")