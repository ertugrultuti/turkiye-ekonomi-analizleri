import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL, seasonal_decompose
import warnings
warnings.filterwarnings("ignore")

# --- Veri yükle ---
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
df.index.freq = "MS"

# --- STL Ayrıştırma (log ölçeğinde) ---
df["log"] = np.log(df["endeks"])

stl = STL(df["log"], period=12, robust=True)
stl_fit = stl.fit()

trend     = np.exp(stl_fit.trend)
seasonal  = stl_fit.seasonal          # log ölçeğinde additive
residual  = stl_fit.resid

# --- Bileşen gücü ---
var_trend    = np.var(stl_fit.trend)
var_seasonal = np.var(stl_fit.seasonal)
var_resid    = np.var(stl_fit.resid)
var_total    = var_trend + var_seasonal + var_resid

print("=== STL BILEŞEN GÜÇLERI (Log Ölçeği) ===")
print(f"  Trend    : %{100*var_trend/var_total:.1f}")
print(f"  Mevsimsel: %{100*var_seasonal/var_total:.1f}")
print(f"  Artık    : %{100*var_resid/var_total:.1f}")

# Mevsimsel endeks (orijinal ölçekte yaklaşık etki)
seasonal_df = pd.DataFrame({
    "ay": df.index.month,
    "seasonal_log": stl_fit.seasonal
})
ay_isimleri = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
               7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
ay_ort = seasonal_df.groupby("ay")["seasonal_log"].mean()

print("\n=== AYLIK MEVSİMSEL ENDEKSLERİ (log fark, ortalama) ===")
for ay, val in ay_ort.items():
    print(f"  {ay_isimleri[ay]:3s}: {val:+.4f}  (~%{100*(np.exp(val)-1):+.2f} etki)")

# --- Grafik 1: STL bileşenleri ---
fig, axes = plt.subplots(4, 1, figsize=(13, 12), sharex=True)

axes[0].plot(df.index, df["endeks"], color="#2c7bb6", linewidth=1.5)
axes[0].set_ylabel("Endeks")
axes[0].set_title("Ham Seri", fontweight="bold")
axes[0].grid(axis="y", linestyle="--", alpha=0.4)

axes[1].plot(df.index, trend, color="#d62728", linewidth=2)
axes[1].set_ylabel("Trend")
axes[1].set_title("Trend Bileşeni (STL, log→orijinal ölçek)", fontweight="bold")
axes[1].grid(axis="y", linestyle="--", alpha=0.4)

axes[2].bar(df.index, seasonal, color="#ff7f0e", width=20, alpha=0.8)
axes[2].axhline(0, color="black", linewidth=0.8)
axes[2].set_ylabel("Mevsimsel (log)")
axes[2].set_title("Mevsimsel Bileşen", fontweight="bold")
axes[2].grid(axis="y", linestyle="--", alpha=0.4)

renkler = ["#d73027" if v > 0 else "#4575b4" for v in residual]
axes[3].bar(df.index, residual, color=renkler, width=20, alpha=0.85)
axes[3].axhline(0, color="black", linewidth=0.8)
axes[3].set_ylabel("Artık (log)")
axes[3].set_title("Artık Bileşen", fontweight="bold")
axes[3].grid(axis="y", linestyle="--", alpha=0.4)

plt.suptitle("STL Ayrıştırma — Tarımsal Girdi Fiyat Endeksi", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim8_stl.png", dpi=150, bbox_inches="tight")
plt.show()

# --- Grafik 2: Mevsimsel endeks çubuk grafik ---
fig2, ax = plt.subplots(figsize=(10, 4))
renkler2 = ["#d73027" if v > 0 else "#4575b4" for v in ay_ort.values]
bars = ax.bar([ay_isimleri[i] for i in ay_ort.index], ay_ort.values,
              color=renkler2, alpha=0.85, edgecolor="white")
ax.axhline(0, color="black", linewidth=0.9)
ax.set_title("STL Ortalama Mevsimsel Endeks (log ölçeği)", fontweight="bold")
ax.set_ylabel("Log Mevsimsel Etki")
ax.grid(axis="y", linestyle="--", alpha=0.4)
for bar, val in zip(bars, ay_ort.values):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.0003 if val >= 0 else bar.get_height() - 0.0008,
            f"%{100*(np.exp(val)-1):+.1f}", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("adim8_stl_mevsim.png", dpi=150, bbox_inches="tight")
plt.show()

print("Kaydedildi: adim8_stl.png, adim8_stl_mevsim.png")