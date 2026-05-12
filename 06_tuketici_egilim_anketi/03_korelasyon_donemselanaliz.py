import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# ── Veri hazırlık (öncekiyle aynı) ───────────────────────────────────────────
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

# ── Dönem etiketleri ──────────────────────────────────────────────────────────
def donem_ata(t):
    if t < pd.Timestamp("2018-08-01"):
        return "1_Öncesi\n(2013–2018)"
    elif t < pd.Timestamp("2020-03-01"):
        return "2_Döviz\nKrizi"
    elif t < pd.Timestamp("2021-12-01"):
        return "3_Covid"
    elif t < pd.Timestamp("2023-05-01"):
        return "4_Kur\nKrizi"
    else:
        return "5_Toparlanma\n(2023–2026)"

df["donem"] = df["tarih"].apply(donem_ata)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 6 — Korelasyon Isı Haritası (tüm değişkenler)
# ════════════════════════════════════════════════════════════════════════════════
cols = [c for c in df.columns if c not in ["tarih", "donem"]]
corr = df[cols].corr()

etiket = {
    "TGE": "TGE",
    "hane_mevcut": "Hane Mevcut",
    "hane_beklenti": "Hane Beklenti",
    "ekonomi_mevcut": "Ekonomi Mevcut",
    "ekonomi_beklenti": "Ekonomi Beklenti",
    "issizlik_beklenti": "İşsizlik Beklenti",
    "yari_dayanikli": "Yarı-Dayanıklı",
    "dayanikli_uygunluk": "Dayanıklı Uygunluk",
    "dayanikli_beklenti": "Dayanıklı Beklenti",
    "tasarruf_uygunluk": "Tasarruf Uygunluk",
    "hane_mali": "Hane Mali",
    "tasarruf_ihtimal": "Tasarruf İhtimal",
    "borc_ihtimal": "Borç İhtimal",
    "fiyat_dusunce": "Fiyat Algı",
    "fiyat_beklenti": "Fiyat Beklenti",
    "ucret_beklenti": "Ücret Beklenti",
    "oto_ihtimal": "Oto İhtimal",
    "konut_tamirat": "Konut Tamirat",
    "konut_satin": "Konut Satın",
}
corr.index = [etiket[c] for c in corr.index]
corr.columns = [etiket[c] for c in corr.columns]

fig, ax = plt.subplots(figsize=(14, 11))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
    center=0, vmin=-1, vmax=1, linewidths=0.4,
    annot_kws={"size": 7.5}, ax=ax,
    cbar_kws={"shrink": 0.7, "label": "Pearson r"}
)
ax.set_title("Değişkenler Arası Korelasyon Matrisi (2013–2026)",
             fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig("grafik6_korelasyon.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik6_korelasyon.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 7 — TGE ile temel bileşenler arası korelasyon (dönem bazlı)
# ════════════════════════════════════════════════════════════════════════════════
ana_degiskenler = [
    "hane_mevcut", "hane_beklenti", "ekonomi_mevcut",
    "ekonomi_beklenti", "issizlik_beklenti", "dayanikli_uygunluk",
    "fiyat_dusunce", "tasarruf_uygunluk", "borc_ihtimal"
]
etiket2 = {
    "hane_mevcut": "Hane Mevcut",
    "hane_beklenti": "Hane Beklenti",
    "ekonomi_mevcut": "Ekonomi Mevcut",
    "ekonomi_beklenti": "Ekonomi Beklenti",
    "issizlik_beklenti": "İşsizlik Beklenti",
    "dayanikli_uygunluk": "Dayanıklı Uygunluk",
    "fiyat_dusunce": "Fiyat Algı",
    "tasarruf_uygunluk": "Tasarruf Uygunluk",
    "borc_ihtimal": "Borç İhtimal",
}

donemler = df["donem"].unique()
donem_sirali = sorted(donemler)

corr_donem = {}
for d in donem_sirali:
    sub = df[df["donem"] == d]
    corr_donem[d] = sub[["TGE"] + ana_degiskenler].corr()["TGE"].drop("TGE")

corr_df = pd.DataFrame(corr_donem).T
corr_df.columns = [etiket2[c] for c in corr_df.columns]
corr_df.index = [i.replace("\n", " ") for i in corr_df.index]

fig, ax = plt.subplots(figsize=(13, 5))
sns.heatmap(
    corr_df, annot=True, fmt=".2f", cmap="RdYlGn",
    center=0, vmin=-1, vmax=1, linewidths=0.5,
    annot_kws={"size": 9}, ax=ax,
    cbar_kws={"shrink": 0.6, "label": "Pearson r (TGE ile)"}
)
ax.set_title("TGE ile Bileşenler Arası Korelasyon — Dönem Bazlı",
             fontsize=13, fontweight="bold", pad=15)
ax.set_xlabel("")
plt.tight_layout()
plt.savefig("grafik7_korelasyon_donem.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik7_korelasyon_donem.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 8 — Dönem bazlı TGE kutu grafiği (box plot)
# ════════════════════════════════════════════════════════════════════════════════
donem_renk = {
    "1_Öncesi\n(2013–2018)": "#4e79a7",
    "2_Döviz\nKrizi": "#f28e2b",
    "3_Covid": "#e15759",
    "4_Kur\nKrizi": "#76b7b2",
    "5_Toparlanma\n(2023–2026)": "#59a14f",
}

fig, ax = plt.subplots(figsize=(11, 5))
donem_verileri = [df[df["donem"] == d]["TGE"].values for d in donem_sirali]
bp = ax.boxplot(donem_verileri, patch_artist=True, notch=False,
                medianprops=dict(color="black", lw=2))

for patch, d in zip(bp["boxes"], donem_sirali):
    patch.set_facecolor(donem_renk[d])
    patch.set_alpha(0.75)

etiket_x = [d.replace("\n", " ") for d in donem_sirali]
ax.set_xticklabels(etiket_x, fontsize=10)
ax.set_ylabel("TGE Değeri")
ax.set_title("Dönem Bazlı TGE Dağılımı", fontsize=13, fontweight="bold")
ax.axhline(df["TGE"].mean(), color="gray", ls="--", lw=1, alpha=0.7,
           label=f"Genel ort. ({df['TGE'].mean():.1f})")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig("grafik8_donem_boxplot.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik8_donem_boxplot.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# TABLO — Dönem bazlı özet istatistikler (konsola)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("DÖNEM BAZLI ÖZET İSTATİSTİKLER")
print("=" * 70)

ozet_cols = ["TGE", "hane_mevcut", "ekonomi_mevcut",
             "fiyat_dusunce", "tasarruf_uygunluk", "borc_ihtimal"]

for d in donem_sirali:
    sub = df[df["donem"] == d]
    print(f"\n▶ {d.replace(chr(10), ' ')}  (n={len(sub)})")
    print(sub[ozet_cols].describe().loc[["mean", "std", "min", "max"]].round(2).to_string())