import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

df["HO_3"]  = df["endeks"].rolling(3).mean()
df["HO_6"]  = df["endeks"].rolling(6).mean()
df["HO_12"] = df["endeks"].rolling(12).mean()
df["HO_24"] = df["endeks"].rolling(24).mean()

print("=== SON 12 AYIN HAREKETLİ ORTALAMA DEĞERLERİ ===")
print(df[["endeks", "HO_3", "HO_6", "HO_12", "HO_24"]].tail(12).round(2).to_string())

fig, axes = plt.subplots(2, 1, figsize=(13, 9))

ax1 = axes[0]
ax1.plot(df.index, df["endeks"], color="#aec7e8", linewidth=1.2, alpha=0.9, label="Endeks")
ax1.plot(df.index, df["HO_3"],  color="#1f77b4", linewidth=1.5, linestyle="--", label="3 Aylık HO")
ax1.plot(df.index, df["HO_6"],  color="#ff7f0e", linewidth=1.8, label="6 Aylık HO")
ax1.plot(df.index, df["HO_12"], color="#2ca02c", linewidth=2.0, label="12 Aylık HO")
ax1.plot(df.index, df["HO_24"], color="#d62728", linewidth=2.2, label="24 Aylık HO")
ax1.set_title("Tarımsal Girdi Fiyat Endeksi — Hareketli Ortalamalar", fontsize=12, fontweight="bold")
ax1.set_ylabel("Endeks Değeri")
ax1.legend(loc="upper left")
ax1.grid(axis="y", linestyle="--", alpha=0.4)

df["sapma_12"] = df["endeks"] - df["HO_12"]

ax2 = axes[1]
renkler = ["#d73027" if v >= 0 else "#4575b4" for v in df["sapma_12"].dropna()]
ax2.bar(df["sapma_12"].dropna().index, df["sapma_12"].dropna(),
        color=renkler, width=20, alpha=0.8)
ax2.axhline(0, color="black", linewidth=0.9)
ax2.set_title("12 Aylık Hareketli Ortalamadan Sapma (Endeks − HO_12)", fontsize=12, fontweight="bold")
ax2.set_ylabel("Sapma (Puan)")
ax2.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("adim4_hareketli_ortalama.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim4_hareketli_ortalama.png")