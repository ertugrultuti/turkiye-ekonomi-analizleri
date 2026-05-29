import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# --- Veri yükle ---
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
df.index.freq = "MS"

df["log"] = np.log(df["endeks"])
df["aylik_pct"] = df["endeks"].pct_change() * 100

# --- Yöntem 1: IQR (aylık % değişim üzerinde) ---
Q1 = df["aylik_pct"].quantile(0.25)
Q3 = df["aylik_pct"].quantile(0.75)
IQR = Q3 - Q1
iqr_alt = Q1 - 1.5 * IQR
iqr_ust = Q3 + 1.5 * IQR
df["iqr_anomali"] = (df["aylik_pct"] < iqr_alt) | (df["aylik_pct"] > iqr_ust)

# --- Yöntem 2: Z-score (aylık % değişim) ---
df["zscore"] = stats.zscore(df["aylik_pct"].fillna(0))
df["z_anomali"] = df["zscore"].abs() > 2.5

# --- Yöntem 3: STL artıkları ---
stl = STL(df["log"], period=12, robust=True)
stl_fit = stl.fit()
resid = pd.Series(stl_fit.resid, index=df.index)
resid_std = resid.std()
df["stl_resid"] = resid
df["stl_anomali"] = resid.abs() > 2.5 * resid_std

# --- Birleşik anomali skoru (kaç yöntemde anomali?) ---
df["anomali_skor"] = df["iqr_anomali"].astype(int) + \
                     df["z_anomali"].astype(int) + \
                     df["stl_anomali"].astype(int)

# --- Yazdır ---
print("=== IQR SINIRLAR ===")
print(f"  Alt sınır: {iqr_alt:.3f}%  |  Üst sınır: {iqr_ust:.3f}%")

print("\n=== ANOMALİ TESPİTİ — TÜM YÖNTEMLERİN ÖZETI ===")
anomaliler = df[df["anomali_skor"] >= 2][
    ["endeks", "aylik_pct", "zscore", "stl_resid", "anomali_skor"]
].copy()
anomaliler.columns = ["Endeks", "Aylık %", "Z-score", "STL Artık", "Skor"]
print(anomaliler.round(3).to_string())

print(f"\nToplam anomali (≥2 yöntem): {len(anomaliler)}")

# --- Grafik ---
fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=True)

# Üst: Ham seri + anomaliler
ax = axes[0]
ax.plot(df.index, df["endeks"], color="#2c7bb6", linewidth=1.5, label="Endeks", zorder=2)
for skor, renk, etiket in [(1, "#fdae61", "1 yöntem"), (2, "#f46d43", "2 yöntem"), (3, "#a50026", "3 yöntem")]:
    mask = df["anomali_skor"] == skor
    if mask.any():
        ax.scatter(df.index[mask], df["endeks"][mask], s=80, color=renk,
                   zorder=5, label=etiket, edgecolors="black", linewidths=0.5)
ax.set_title("Ham Endeks + Anomali Noktaları", fontweight="bold")
ax.set_ylabel("Endeks")
ax.legend(loc="upper left", fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# Orta: Aylık % değişim + IQR sınırları
ax = axes[1]
renkler = ["#a50026" if v else "#4575b4" for v in df["iqr_anomali"]]
ax.bar(df.index, df["aylik_pct"].fillna(0), color=renkler, width=20, alpha=0.8)
ax.axhline(iqr_ust, color="#d73027", linestyle="--", linewidth=1.2, label=f"IQR üst ({iqr_ust:.2f}%)")
ax.axhline(iqr_alt, color="#1a9641", linestyle="--", linewidth=1.2, label=f"IQR alt ({iqr_alt:.2f}%)")
ax.set_title("Aylık % Değişim — IQR Anomali Sınırları", fontweight="bold")
ax.set_ylabel("%")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# Alt: STL artıkları + ±2.5σ bantları
ax = axes[2]
renkler2 = ["#d73027" if v else "#4575b4" for v in df["stl_anomali"]]
ax.bar(df.index, df["stl_resid"], color=renkler2, width=20, alpha=0.8)
ax.axhline(2.5 * resid_std, color="#d73027", linestyle="--", linewidth=1.2, label="+2.5σ")
ax.axhline(-2.5 * resid_std, color="#d73027", linestyle="--", linewidth=1.2, label="-2.5σ")
ax.fill_between(df.index, -2.5*resid_std, 2.5*resid_std, alpha=0.08, color="gray")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("STL Artık Bileşeni — ±2.5σ Anomali Bantları", fontweight="bold")
ax.set_ylabel("Artık (log)")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.suptitle("Tarımsal Girdi Fiyat Endeksi — Anomali Tespiti", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim9_anomali.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim9_anomali.png")