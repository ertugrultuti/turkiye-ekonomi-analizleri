import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

df["ay"]        = df.index.month
df["yil"]       = df.index.year
df["aylik_pct"] = df["endeks"].pct_change() * 100

ay_isimleri = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"]

# 1. Aylık ortalama % değişim
ay_ort = df.groupby("ay")["aylik_pct"].agg(["mean","median","std"]).round(3)
ay_ort.index = ay_isimleri
print("=== AYLARA GÖRE ORTALAMA % DEĞİŞİM ===")
print(ay_ort.to_string())

# 2. En yüksek / düşük ay
print(f"\nEn güçlü ay (ortalama): {ay_isimleri[ay_ort['mean'].idxmax()-1 if isinstance(ay_ort['mean'].idxmax(), int) else list(ay_ort.index).index(ay_ort['mean'].idxmax())]} — %{ay_ort['mean'].max():.3f}")
print(f"En zayıf  ay (ortalama): {ay_isimleri[ay_ort['mean'].idxmin()-1 if isinstance(ay_ort['mean'].idxmin(), int) else list(ay_ort.index).index(ay_ort['mean'].idxmin())]} — %{ay_ort['mean'].min():.3f}")

# Grafik
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# Sol üst: Aylık ortalama % değişim (bar)
ax = axes[0, 0]
renkler = ["#d73027" if v >= 0 else "#4575b4" for v in ay_ort["mean"]]
bars = ax.bar(ay_ort.index, ay_ort["mean"], color=renkler, alpha=0.85, edgecolor="white")
ax.errorbar(ay_ort.index, ay_ort["mean"], yerr=ay_ort["std"],
            fmt="none", color="black", capsize=4, linewidth=1.2)
ax.axhline(0, color="black", linewidth=0.8)
ax.axhline(ay_ort["mean"].mean(), color="gray", linestyle="--", linewidth=1, alpha=0.7, label=f"Genel ort: %{ay_ort['mean'].mean():.2f}")
ax.set_title("Aylara Göre Ortalama % Değişim (±1 std)", fontweight="bold")
ax.set_ylabel("%")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)
for bar, val in zip(bars, ay_ort["mean"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=7.5)

# Sağ üst: Medyan % değişim
ax = axes[0, 1]
renkler2 = ["#d73027" if v >= 0 else "#4575b4" for v in ay_ort["median"]]
ax.bar(ay_ort.index, ay_ort["median"], color=renkler2, alpha=0.85, edgecolor="white")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Aylara Göre Medyan % Değişim", fontweight="bold")
ax.set_ylabel("%")
ax.grid(axis="y", linestyle="--", alpha=0.4)

# Sol alt: Yıl × Ay ısı haritası (% değişim)
pivot = df.pivot_table(values="aylik_pct", index="yil", columns="ay", aggfunc="mean")
pivot.columns = ay_isimleri
ax = axes[1, 0]
im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn_r")
ax.set_xticks(range(12))
ax.set_xticklabels(ay_isimleri, fontsize=9)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, fontsize=9)
ax.set_title("Yıl × Ay Isı Haritası (Aylık % Değişim)", fontweight="bold")
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="%")
for i in range(len(pivot.index)):
    for j in range(12):
        val = pivot.values[i, j]
        if not np.isnan(val):
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=6.5,
                    color="black" if abs(val) < 8 else "white")

# Sağ alt: Box plot aylara göre
ax = axes[1, 1]
data_by_month = [df[df["ay"] == m]["aylik_pct"].dropna().values for m in range(1, 13)]
bp = ax.boxplot(data_by_month, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
for patch in bp["boxes"]:
    patch.set_facecolor("#aec7e8")
ax.set_xticklabels(ay_isimleri, fontsize=9)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Aylık % Değişim Dağılımı (Box Plot)", fontweight="bold")
ax.set_ylabel("%")
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.suptitle("Tarımsal Girdi Fiyat Endeksi — Mevsimsellik Analizi", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim5_mevsimsellik.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim5_mevsimsellik.png")