import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)

# Haftalık frekans ata
df = df.set_index("Tarih")
df.index.freq = pd.tseries.frequencies.to_offset("W-FRI")

for col in ["Toplam", "TL", "YP"]:
    seri = df[col].dropna()
    log_seri = np.log(seri)
    diff_seri = seri.diff().dropna()
    log_diff  = log_seri.diff().dropna()

    adf_raw  = adfuller(seri,      autolag="AIC")
    adf_diff = adfuller(diff_seri, autolag="AIC")
    adf_logd = adfuller(log_diff,  autolag="AIC")

    print(f"\n{'='*55}")
    print(f"  {col}")
    print(f"{'='*55}")
    print(f"  ADF (düzey)      : stat={adf_raw[0]:.4f},  p={adf_raw[1]:.4f}  {'✗ Durağan DEĞİL' if adf_raw[1]>0.05 else '✓ Durağan'}")
    print(f"  ADF (1. fark)    : stat={adf_diff[0]:.4f}, p={adf_diff[1]:.4f}  {'✗ Durağan DEĞİL' if adf_diff[1]>0.05 else '✓ Durağan'}")
    print(f"  ADF (log-fark)   : stat={adf_logd[0]:.4f}, p={adf_logd[1]:.4f}  {'✗ Durağan DEĞİL' if adf_logd[1]>0.05 else '✓ Durağan'}")

    # Otokorelasyon özeti
    from statsmodels.stats.stattools import durbin_watson
    dw = durbin_watson(diff_seri)
    print(f"  Durbin-Watson    : {dw:.4f}  {'(otokorelasyon var)' if dw < 1.5 or dw > 2.5 else '(otokorelasyon yok)'}")

    # Büyüme istatistikleri
    haftalik_buy = log_diff * 100
    print(f"\n  Haftalık log-büyüme özeti:")
    print(f"    Ortalama : {haftalik_buy.mean():.4f}%")
    print(f"    Std      : {haftalik_buy.std():.4f}%")
    print(f"    Min/Max  : {haftalik_buy.min():.4f}% / {haftalik_buy.max():.4f}%")
    print(f"    Son 12 hf ort: {haftalik_buy.iloc[-12:].mean():.4f}%")
    print(f"    Son 26 hf ort: {haftalik_buy.iloc[-26:].mean():.4f}%")