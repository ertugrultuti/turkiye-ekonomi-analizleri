import pandas as pd
import matplotlib.pyplot as plt

# --- Veriyi baştan yükle ---
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

# --- Değişimleri hesapla ---
df["aylik_abs"]  = df["endeks"].diff()
df["aylik_pct"]  = df["endeks"].pct_change() * 100
df["yillik_abs"] = df["endeks"].diff(12)
df["yillik_pct"] = df["endeks"].pct_change(12) * 100

# --- Özet tablo ---
print("=== AYLIK DEĞİŞİM İSTATİSTİKLERİ ===")
print(df["aylik_pct"].describe().round(3))

print("\n=== YILLIK DEĞİŞİM İSTATİSTİKLERİ ===")
print(df["yillik_pct"].describe().round(3))

print("\n=== EN YÜKSEK AYLIK ARTIŞ (İlk 5) ===")
print(df["aylik_pct"].nlargest(5).round(3))

print("\n=== EN BÜYÜK AYLIK DÜŞÜŞ (İlk 5) ===")
print(df["aylik_pct"].nsmallest(5).round(3))

print("\n=== EN YÜKSEK YILLIK ARTIŞ (İlk 5) ===")
print(df["yillik_pct"].nlargest(5).round(2))

# --- Görselleştirme ---
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

ax = axes[0, 0]
renkler = ["#d73027" if v >= 0 else "#4575b4" for v in df["aylik_abs"].dropna()]
ax.bar(df["aylik_abs"].dropna().index, df["aylik_abs"].dropna(), color=renkler, width=20)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Aylık Mutlak Değişim")
ax.set_ylabel("Puan")
ax.grid(axis="y", linestyle="--", alpha=0.4)

ax = axes[0, 1]
renkler = ["#d73027" if v >= 0 else "#4575b4" for v in df["aylik_pct"].dropna()]
ax.bar(df["aylik_pct"].dropna().index, df["aylik_pct"].dropna(), color=renkler, width=20)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Aylık % Değişim")
ax.set_ylabel("%")
ax.grid(axis="y", linestyle="--", alpha=0.4)

ax = axes[1, 0]
ax.plot(df["yillik_abs"].dropna().index, df["yillik_abs"].dropna(),
        color="#1a9641", linewidth=1.8)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Yıllık Mutlak Değişim")
ax.set_ylabel("Puan")
ax.grid(axis="y", linestyle="--", alpha=0.4)

ax = axes[1, 1]
ax.plot(df["yillik_pct"].dropna().index, df["yillik_pct"].dropna(),
        color="#d73027", linewidth=1.8)
ax.axhline(0, color="black", linewidth=0.8)
ax.fill_between(df["yillik_pct"].dropna().index,
                df["yillik_pct"].dropna(), 0,
                alpha=0.15, color="#d73027")
ax.set_title("Yıllık % Değişim")
ax.set_ylabel("%")
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.suptitle("Tarımsal Girdi Fiyat Endeksi — Değişim Analizi", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim3_degisim.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim3_degisim.png")