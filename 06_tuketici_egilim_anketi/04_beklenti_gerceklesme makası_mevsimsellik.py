import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats

# ── Veri hazırlık ─────────────────────────────────────────────────────────────
df = pd.read_excel("Veri.xlsx")

kisaltma = {
    "Tarih": "tarih",
    "Tüketici Güven Endeksi": "TGE",
    "Hanenin maddi durumu (12 ay öncesine göre mevcut dönemde)": "hane_mevcut",
    "Hanenin maddi durum beklentisi (gelecek 12 aylık dönemde)": "hane_beklenti",
    "Genel ekonomik durum (12 ay öncesine göre mevcut dönemde)": "ekonomi_mevcut",
    "Genel ekonomik durum beklentisi (gelecek 12 aylık dönemde)": "ekonomi_beklenti",
    "İşsizlerin sayısı beklentisi (gelecek 12 aylık dönemde)": "issizlik_beklenti",
    "Yarı_dayanıklı tüketim mallarına yönelik harcama yapma düşüncesi (geçen 3 aylık döneme göre gelecek 3 aylık dönemde)": "yari_dayanikli",
    "Mevcut dönemin dayanıklı tüketim malı satın almak için uygunluğu": "dayanikli_uygunluk",
    "Dayanıklı tüketim mallarına yönelik harcama yapma düşüncesi (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)": "dayanikli_beklenti",
    "Mevcut dönemin tasarruf etmek için uygunluğu": "tasarruf_uygunluk",
    "Hanenin içinde bulunduğu mali durumu": "hane_mali",
    "Tasarruf etme ihtimali (gelecek 12 aylık dönemde)": "tasarruf_ihtimal",
    "Tüketimin finansmanı amacıyla borç kullanma ihtimali (gelecek 3 aylık dönemde)": "borc_ihtimal",
    "Tüketici fiyatlarının değişimine ilişkin düşünce (geçen 12 aylık dönemde)": "fiyat_dusunce",
    "Tüketici fiyatlarının değişimine ilişkin beklenti (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)": "fiyat_beklenti",
    "Ücretlerin değişimine ilişkin beklenti (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)": "ucret_beklenti",
    "Otomobil satın alma ihtimali (gelecek 12 aylık dönemde)": "oto_ihtimal",
    "Konut tamiratına para harcama ihtimali (gelecek 12 aylık dönemde)": "konut_tamirat",
    "Konut satın alma veya inşa ettirme ihtimali (gelecek 12 aylık dönemde)": "konut_satin",
}
df.rename(columns=kisaltma, inplace=True)
df["tarih"] = pd.to_datetime(df["tarih"], format="%m/%Y")
df = df.sort_values("tarih").reset_index(drop=True)
df["ay"] = df["tarih"].dt.month
df["yil"] = df["tarih"].dt.year

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

ay_etiket = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"]

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 9 — Beklenti-Gerçekleşme Makası (Hane & Ekonomi)
# 12 ay öteleme: t dönemindeki beklenti, t+12'deki gerçekleşmeyle karşılaştırılır
# ════════════════════════════════════════════════════════════════════════════════

# Hane: beklenti(t) vs mevcut(t+12)
df["hane_gerceklesme"] = df["hane_mevcut"].shift(-12)
df["hane_makas"]       = df["hane_beklenti"] - df["hane_gerceklesme"]

# Ekonomi: beklenti(t) vs mevcut(t+12)
df["ekonomi_gerceklesme"] = df["ekonomi_mevcut"].shift(-12)
df["ekonomi_makas"]       = df["ekonomi_beklenti"] - df["ekonomi_gerceklesme"]

fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

# -- Hane
ax = axes[0]
valid = df["hane_makas"].notna()
pos = df["hane_makas"].clip(lower=0)
neg = df["hane_makas"].clip(upper=0)
ax.fill_between(df["tarih"][valid], pos[valid], 0, alpha=0.5, color="#d62728", label="Aşırı iyimserlik (beklenti > gerçekleşme)")
ax.fill_between(df["tarih"][valid], neg[valid], 0, alpha=0.5, color="#1f77b4", label="Aşırı karamserlik (beklenti < gerçekleşme)")
ax.axhline(0, color="black", lw=0.8)
ax.plot(df["tarih"][valid], df["hane_makas"][valid].rolling(6).mean(),
        color="black", lw=1.5, ls="--", label="6 aylık hareketli ort.")
ax.set_title("Hane Mali Durumu: Beklenti – Gerçekleşme Makası (12 ay öteleme)", fontsize=11, fontweight="bold")
ax.set_ylabel("Makas (puan)")
ax.legend(fontsize=8)

# -- Ekonomi
ax = axes[1]
valid2 = df["ekonomi_makas"].notna()
pos2 = df["ekonomi_makas"].clip(lower=0)
neg2 = df["ekonomi_makas"].clip(upper=0)
ax.fill_between(df["tarih"][valid2], pos2[valid2], 0, alpha=0.5, color="#d62728", label="Aşırı iyimserlik")
ax.fill_between(df["tarih"][valid2], neg2[valid2], 0, alpha=0.5, color="#1f77b4", label="Aşırı karamserlik")
ax.axhline(0, color="black", lw=0.8)
ax.plot(df["tarih"][valid2], df["ekonomi_makas"][valid2].rolling(6).mean(),
        color="black", lw=1.5, ls="--", label="6 aylık hareketli ort.")
ax.set_title("Genel Ekonomik Durum: Beklenti – Gerçekleşme Makası (12 ay öteleme)", fontsize=11, fontweight="bold")
ax.set_ylabel("Makas (puan)")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(fontsize=8)

plt.suptitle("Beklenti – Gerçekleşme Makası Analizi", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("grafik9_makas.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik9_makas.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 10 — Mevsimsellik: TGE aylık ortalamalar (tüm yıllar & dönem bazlı)
# ════════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Sol: tüm dönem aylık ort ± std
ay_ort = df.groupby("ay")["TGE"].agg(["mean", "std"]).reset_index()
ax = axes[0]
ax.bar(ay_ort["ay"], ay_ort["mean"], color="#4e79a7", alpha=0.8, zorder=2)
ax.errorbar(ay_ort["ay"], ay_ort["mean"], yerr=ay_ort["std"],
            fmt="none", color="black", capsize=4, lw=1.5, zorder=3)
ax.axhline(df["TGE"].mean(), color="red", ls="--", lw=1.2, label=f"Genel ort. ({df['TGE'].mean():.1f})")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(ay_etiket, fontsize=9)
ax.set_ylabel("TGE Ortalama")
ax.set_title("TGE Aylık Ortalama (Tüm Dönem)", fontsize=11, fontweight="bold")
ax.legend(fontsize=9)
ax.set_ylim(70, 100)

# Sağ: dönem bazlı mevsimsellik (çizgi grafik)
donem_renk2 = {
    "Öncesi (2013–18)": "#4e79a7",
    "Döviz Krizi": "#f28e2b",
    "Covid": "#e15759",
    "Kur Krizi": "#76b7b2",
    "Toparlanma": "#59a14f",
}

def donem_ata2(t):
    if t < pd.Timestamp("2018-08-01"):   return "Öncesi (2013–18)"
    elif t < pd.Timestamp("2020-03-01"): return "Döviz Krizi"
    elif t < pd.Timestamp("2021-12-01"): return "Covid"
    elif t < pd.Timestamp("2023-05-01"): return "Kur Krizi"
    else:                                return "Toparlanma"

df["donem2"] = df["tarih"].apply(donem_ata2)

ax = axes[1]
for d, renk in donem_renk2.items():
    sub = df[df["donem2"] == d].groupby("ay")["TGE"].mean()
    ax.plot(sub.index, sub.values, color=renk, lw=2, marker="o", ms=5, label=d)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(ay_etiket, fontsize=9)
ax.set_ylabel("TGE Ortalama")
ax.set_title("Dönem Bazlı Mevsimsel Profil", fontsize=11, fontweight="bold")
ax.legend(fontsize=8)

plt.suptitle("TGE Mevsimsellik Analizi", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("grafik10_mevsimsellik.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik10_mevsimsellik.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# TABLO — Makas özet istatistikleri + istatistiksel anlamlılık
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("BEKLENTI – GERÇEKLEŞme MAKAS ÖZETİ")
print("=" * 60)

for ad, seri in [("Hane", df["hane_makas"].dropna()),
                 ("Ekonomi", df["ekonomi_makas"].dropna())]:
    t_stat, p_val = stats.ttest_1samp(seri, 0)
    print(f"\n▶ {ad} Makası")
    print(f"  Ortalama : {seri.mean():.2f} puan")
    print(f"  Std      : {seri.std():.2f}")
    print(f"  Min/Max  : {seri.min():.2f} / {seri.max():.2f}")
    print(f"  Pozitif  : {(seri > 0).sum()} ay  ({(seri > 0).mean()*100:.1f}%)")
    print(f"  Negatif  : {(seri < 0).sum()} ay  ({(seri < 0).mean()*100:.1f}%)")
    print(f"  t-test (H₀: ort=0) → t={t_stat:.2f}, p={p_val:.4f}")

# ════════════════════════════════════════════════════════════════════════════════
# TABLO — Aylık mevsimsel sapma (tüm dönem)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TGE MEVSİMSEL SAPMA (aylık ort – genel ort)")
print("=" * 60)
genel_ort = df["TGE"].mean()
for _, row in ay_ort.iterrows():
    sapma = row["mean"] - genel_ort
    isaret = "▲" if sapma > 0 else "▼"
    print(f"  {ay_etiket[int(row['ay'])-1]:3s}  ort={row['mean']:.2f}  sapma={sapma:+.2f} {isaret}")