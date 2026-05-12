import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Veri yükleme ve hazırlık ---
df = pd.read_excel("Veri.xlsx")
df.columns = ["Tarih", "Toplam", "Madencilik", "Imalat"]

def parse_quarter(s):
    yil, ceyrek = s.split("-")
    ay = {"1Ç": 1, "2Ç": 4, "3Ç": 7, "4Ç": 10}[ceyrek]
    return pd.Timestamp(int(yil), ay, 1)

df["Tarih"] = df["Tarih"].apply(parse_quarter)
df = df.set_index("Tarih")
df.index = pd.PeriodIndex(df.index, freq="Q")

seriler = {
    "Toplam Sanayi": df["Toplam"],
    "Madencilik": df["Madencilik"],
    "İmalat": df["Imalat"],
}

# --- 1. Zaman serisi grafikleri ---
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
colors = ["#2563EB", "#16A34A", "#DC2626"]

for ax, (isim, seri), renk in zip(axes, seriler.items(), colors):
    ax.plot(seri.index.to_timestamp(), seri.values, color=renk, linewidth=2, marker="o", markersize=3)
    ax.set_title(isim, fontsize=13, fontweight="bold")
    ax.set_ylabel("Endeks")
    ax.grid(True, alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

fig.suptitle("Çalışılan Saat Başına Üretim Endeksleri (2009Q1–2025Q4)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("01_zaman_serisi.png", dpi=150, bbox_inches="tight")
plt.show()
print("Graf 1 kaydedildi.")

# --- 2. Tanımlayıcı istatistikler ---
desc = df[["Toplam", "Madencilik", "Imalat"]].describe().round(2)
desc.index = ["Gözlem", "Ortalama", "Std. Sapma", "Min", "25%", "Medyan", "75%", "Max"]
desc.columns = ["Toplam Sanayi", "Madencilik", "İmalat"]
print("\n=== Tanımlayıcı İstatistikler ===")
print(desc.to_string())

# --- 3. Çeyreklik ortalamalar ---
df["Ceyrek"] = df.index.quarter
quarterly_means = df.groupby("Ceyrek")[["Toplam", "Madencilik", "Imalat"]].mean().round(2)
quarterly_means.index = ["Q1 (Ocak-Mart)", "Q2 (Nisan-Haziran)", "Q3 (Temmuz-Eylül)", "Q4 (Ekim-Aralık)"]
print("\n=== Çeyreklik Ortalamalar (Mevsimsellik İpucu) ===")
print(quarterly_means.to_string())

# --- 4. Çeyreklik kutu grafikleri ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, (isim, seri), renk in zip(axes, seriler.items(), colors):
    data_by_q = [seri[seri.index.quarter == q].values for q in [1, 2, 3, 4]]
    bp = ax.boxplot(data_by_q, labels=["Q1", "Q2", "Q3", "Q4"], patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor(renk + "44")
        patch.set_edgecolor(renk)
    ax.set_title(isim, fontsize=12, fontweight="bold")
    ax.set_ylabel("Endeks")
    ax.grid(True, alpha=0.3, axis="y")
    ax.spines[["top", "right"]].set_visible(False)

fig.suptitle("Çeyreklik Dağılım (Mevsimsel Örüntü)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("02_boxplot_mevsimsel.png", dpi=150, bbox_inches="tight")
plt.show()
print("Graf 2 kaydedildi.")