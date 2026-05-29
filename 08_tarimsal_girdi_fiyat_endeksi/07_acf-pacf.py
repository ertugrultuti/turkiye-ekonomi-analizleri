import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
import warnings
warnings.filterwarnings("ignore")

# --- Veri yükle ---
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

df["log"]       = np.log(df["endeks"])
df["fark2"]     = df["endeks"].diff().diff()
df["log_fark1"] = df["log"].diff()
df["log_fark2"] = df["log"].diff().diff()

lags = 36

fig, axes = plt.subplots(4, 2, figsize=(14, 14))

seriler = [
    ("Ham Endeks",   df["endeks"],    "#2c7bb6"),
    ("Log(Endeks)",  df["log"],       "#1a9641"),
    ("2. Fark",      df["fark2"],     "#d62728"),
    ("Log 2. Fark",  df["log_fark2"], "#7b2d8b"),
]

for i, (isim, seri, renk) in enumerate(seriler):
    s = seri.dropna()
    
    # ACF
    plot_acf(s, lags=lags, ax=axes[i, 0], alpha=0.05,
             color=renk, vlines_kwargs={"colors": renk})
    axes[i, 0].set_title(f"ACF — {isim}", fontweight="bold", fontsize=10)
    axes[i, 0].set_xlabel("Lag (ay)")
    axes[i, 0].grid(axis="y", linestyle="--", alpha=0.3)
    
    # PACF
    plot_pacf(s, lags=lags, ax=axes[i, 1], alpha=0.05, method="ywm",
              color=renk, vlines_kwargs={"colors": renk})
    axes[i, 1].set_title(f"PACF — {isim}", fontweight="bold", fontsize=10)
    axes[i, 1].set_xlabel("Lag (ay)")
    axes[i, 1].grid(axis="y", linestyle="--", alpha=0.3)

plt.suptitle("ACF & PACF Analizi", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim7_acf_pacf.png", dpi=150, bbox_inches="tight")
plt.show()

# --- Sayısal özet: Log 2. Fark için anlamlı laglar ---
s = df["log_fark2"].dropna()
acf_vals  = acf(s,  nlags=24, alpha=0.05)
pacf_vals = pacf(s, nlags=24, alpha=0.05, method="ywm")

print("=== LOG 2. FARK — ACF (anlamlı laglar) ===")
for lag in range(1, 25):
    val = acf_vals[0][lag]
    ci_low, ci_high = acf_vals[1][lag]
    if val < ci_low or val > ci_high:
        print(f"  Lag {lag:2d}: {val:+.4f}  [CI: {ci_low:.4f}, {ci_high:.4f}]  *** ANLAMLı")

print("\n=== LOG 2. FARK — PACF (anlamlı laglar) ===")
for lag in range(1, 25):
    val = pacf_vals[0][lag]
    ci_low, ci_high = pacf_vals[1][lag]
    if val < ci_low or val > ci_high:
        print(f"  Lag {lag:2d}: {val:+.4f}  [CI: {ci_low:.4f}, {ci_high:.4f}]  *** ANLAMLı")

print("\nKaydedildi: adim7_acf_pacf.png")