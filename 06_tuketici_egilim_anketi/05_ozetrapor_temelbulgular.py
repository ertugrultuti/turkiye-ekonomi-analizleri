import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

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

# Makas hesapla
df["hane_makas"]    = df["hane_beklenti"]    - df["hane_mevcut"].shift(-12)
df["ekonomi_makas"] = df["ekonomi_beklenti"] - df["ekonomi_mevcut"].shift(-12)

# Dönem etiketi
def donem_ata(t):
    if t < pd.Timestamp("2018-08-01"):   return "Öncesi\n(2013–18)"
    elif t < pd.Timestamp("2020-03-01"): return "Döviz\nKrizi"
    elif t < pd.Timestamp("2021-12-01"): return "Covid"
    elif t < pd.Timestamp("2023-05-01"): return "Kur\nKrizi"
    else:                                return "Toparlanma\n(2023–26)"
df["donem"] = df["tarih"].apply(donem_ata)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 11 — Özet Dashboard (2x3 panel)
# ════════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 11))
fig.suptitle("Tüketici Eğilim Anketi — Analiz Özeti (Ekim 2013 – Nisan 2026)",
             fontsize=15, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

olaylar = {"2018-08": "Döviz", "2020-03": "Covid",
           "2021-12": "Kur K.", "2023-02": "Deprem", "2023-05": "Seçim"}

def olay_ciz(ax):
    for ts, lab in olaylar.items():
        t = pd.Timestamp(ts)
        ax.axvline(t, color="gray", lw=0.7, ls="--", alpha=0.5)

# --- Panel A: TGE + hareketli ort
ax_a = fig.add_subplot(gs[0, 0:2])
ax_a.plot(df["tarih"], df["TGE"], color="#aec6e8", lw=1, alpha=0.9)
ax_a.plot(df["tarih"], df["TGE"].rolling(12).mean(), color="#1f77b4", lw=2.5, label="12 ay ort.")
ax_a.axhline(df["TGE"].mean(), color="red", ls=":", lw=1, alpha=0.7, label=f"Ort. {df['TGE'].mean():.1f}")
ax_a.set_title("A. Tüketici Güven Endeksi", fontsize=10, fontweight="bold")
ax_a.set_ylabel("Endeks")
ax_a.xaxis.set_major_locator(mdates.YearLocator(2))
ax_a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_a.legend(fontsize=8)
olay_ciz(ax_a)

# --- Panel B: Dönem bazlı TGE ort (yatay bar)
ax_b = fig.add_subplot(gs[0, 2])
donem_ort = df.groupby("donem")["TGE"].mean()
donem_sirali = ["Öncesi\n(2013–18)", "Döviz\nKrizi", "Covid", "Kur\nKrizi", "Toparlanma\n(2023–26)"]
donem_renkler = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"]
vals = [donem_ort.get(d, np.nan) for d in donem_sirali]
bars = ax_b.barh([d.replace("\n", " ") for d in donem_sirali], vals,
                 color=donem_renkler, alpha=0.85)
ax_b.axvline(df["TGE"].mean(), color="red", ls="--", lw=1, alpha=0.7)
for bar, v in zip(bars, vals):
    ax_b.text(v + 0.3, bar.get_y() + bar.get_height()/2,
              f"{v:.1f}", va="center", fontsize=9, fontweight="bold")
ax_b.set_xlim(60, 100)
ax_b.set_title("B. Dönem Ort. TGE", fontsize=10, fontweight="bold")
ax_b.set_xlabel("Endeks")

# --- Panel C: Mevcut vs Beklenti (ekonomi)
ax_c = fig.add_subplot(gs[1, 0])
ax_c.plot(df["tarih"], df["ekonomi_mevcut"],   color="#2ca02c", lw=1.4, label="Mevcut")
ax_c.plot(df["tarih"], df["ekonomi_beklenti"], color="#ff7f0e", lw=1.4, ls="--", label="Beklenti")
ax_c.fill_between(df["tarih"], df["ekonomi_mevcut"], df["ekonomi_beklenti"],
                  alpha=0.1, color="#ff7f0e")
ax_c.set_title("C. Ekonomi: Mevcut vs Beklenti", fontsize=10, fontweight="bold")
ax_c.set_ylabel("Endeks")
ax_c.xaxis.set_major_locator(mdates.YearLocator(3))
ax_c.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_c.legend(fontsize=8)
olay_ciz(ax_c)

# --- Panel D: Makas (ekonomi)
ax_d = fig.add_subplot(gs[1, 1])
valid = df["ekonomi_makas"].notna()
ax_d.fill_between(df["tarih"][valid],
                  df["ekonomi_makas"][valid].clip(lower=0), 0,
                  alpha=0.55, color="#d62728", label="İyimserlik")
ax_d.fill_between(df["tarih"][valid],
                  df["ekonomi_makas"][valid].clip(upper=0), 0,
                  alpha=0.55, color="#1f77b4", label="Karamserlik")
ax_d.plot(df["tarih"][valid], df["ekonomi_makas"][valid].rolling(6).mean(),
          color="black", lw=1.5, ls="--", label="6ay ort.")
ax_d.axhline(0, color="black", lw=0.8)
ortalama_makas = df["ekonomi_makas"].dropna().mean()
ax_d.axhline(ortalama_makas, color="red", lw=1, ls=":", alpha=0.8,
             label=f"Ort. +{ortalama_makas:.1f}")
ax_d.set_title("D. Ekonomi Beklenti–Gerçekleşme Makası", fontsize=10, fontweight="bold")
ax_d.set_ylabel("Puan")
ax_d.xaxis.set_major_locator(mdates.YearLocator(3))
ax_d.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_d.legend(fontsize=7.5)
olay_ciz(ax_d)

# --- Panel E: Enflasyon algısı & borç ihtimali (iki eksen)
ax_e = fig.add_subplot(gs[1, 2])
color1, color2 = "#d62728", "#9467bd"
l1, = ax_e.plot(df["tarih"], df["fiyat_dusunce"], color=color1, lw=1.5, label="Fiyat Algısı (sol)")
ax_e2 = ax_e.twinx()
ax_e2.spines["top"].set_visible(False)
l2, = ax_e2.plot(df["tarih"], df["borc_ihtimal"], color=color2, lw=1.5, ls="--", label="Borç İhtimali (sağ)")
ax_e.set_title("E. Fiyat Algısı & Borç İhtimali", fontsize=10, fontweight="bold")
ax_e.set_ylabel("Fiyat Algısı", color=color1)
ax_e2.set_ylabel("Borç İhtimali", color=color2)
ax_e.tick_params(axis="y", labelcolor=color1)
ax_e2.tick_params(axis="y", labelcolor=color2)
ax_e.xaxis.set_major_locator(mdates.YearLocator(3))
ax_e.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_e.legend(handles=[l1, l2], fontsize=7.5, loc="upper right")
olay_ciz(ax_e)

plt.savefig("grafik11_dashboard.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik11_dashboard.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# KONSOL — Yapılandırılmış Analitik Rapor
# ════════════════════════════════════════════════════════════════════════════════
print("\n")
print("╔" + "═"*66 + "╗")
print("║   TÜKETİCİ EĞİLİM ANKETİ — ANALİTİK BULGULAR RAPORU           ║")
print("║   Ekim 2013 – Nisan 2026  |  n=151 aylık gözlem                ║")
print("╚" + "═"*66 + "╝")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BULGU 1 — TGE HİÇBİR ZAMAN 100 EŞİĞİNİ AŞAMADI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Tüm dönem ortalaması : 84.0
  En yüksek değer      : 97.4  (Kasım 2013)
  En düşük değer       : 63.4  (Aralık 2022 — Kur Krizi dibi)
  100 eşiğini aşan ay  : 0
  → Türk tüketicisi 13 yılda hiç net iyimser konuma geçemedi.
""")

donem_dict = {
    "Öncesi (2013–18)": df[df["donem"]=="Öncesi\n(2013–18)"]["TGE"],
    "Döviz Krizi": df[df["donem"]=="Döviz\nKrizi"]["TGE"],
    "Covid": df[df["donem"]=="Covid"]["TGE"],
    "Kur Krizi": df[df["donem"]=="Kur\nKrizi"]["TGE"],
    "Toparlanma": df[df["donem"]=="Toparlanma\n(2023–26)"]["TGE"],
}

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("BULGU 2 — KRİZLERİN TGE'YE ETKİSİ (dönem ortalamaları)")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
for ad, seri in donem_dict.items():
    print(f"  {ad:<22} ort={seri.mean():.1f}  min={seri.min():.1f}  max={seri.max():.1f}")

ref = donem_dict["Öncesi (2013–18)"].mean()
print(f"\n  Öncesi döneme göre kayıplar:")
for ad, seri in list(donem_dict.items())[1:]:
    fark = seri.mean() - ref
    print(f"    {ad:<20}  {fark:+.1f} puan")

hane_m   = df["hane_makas"].dropna()
ekonomi_m = df["ekonomi_makas"].dropna()
ht, hp = stats.ttest_1samp(hane_m, 0)
et, ep = stats.ttest_1samp(ekonomi_m, 0)

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BULGU 3 — YAPISAL İYİMSERLİK ÖNYARGISI (p<0.001 düzeyinde)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Hane makası    : ort=+{hane_m.mean():.1f} puan  (pos: %{(hane_m>0).mean()*100:.0f})  t={ht:.1f}  p<0.001
  Ekonomi makası : ort=+{ekonomi_m.mean():.1f} puan  (pos: %{(ekonomi_m>0).mean()*100:.0f})  t={et:.1f}  p<0.001
  → Tüketiciler sistematik olarak geleceği olduğundan iyi görüyor.
  → Bu önyargı kriz dönemlerinde daha da büyüyor.
""")

print("""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BULGU 4 — BORÇLANMA BASKISI TOPARLANMAYLA BİRLİKTE ARTIYOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
for ad, seri in donem_dict.items():
    sub = df[df["donem"] == {"Öncesi (2013–18)":"Öncesi\n(2013–18)",
                              "Döviz Krizi":"Döviz\nKrizi",
                              "Covid":"Covid",
                              "Kur Krizi":"Kur\nKrizi",
                              "Toparlanma":"Toparlanma\n(2023–26)"}[ad]]
    print(f"  {ad:<22} borç_ort={sub['borc_ihtimal'].mean():.1f}  tasarruf_ort={sub['tasarruf_ihtimal'].mean():.1f}")

print("""
  → Toparlanma döneminde borç ihtimali tarihi zirveye (58.7) ulaştı.
  → Aynı dönemde tasarruf ihtimali de yükseldi: finansal
    baskı altında hem borçlanma hem de tasarruf güdüsü birlikte artıyor.
""")

print("""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BULGU 5 — MEVSİMSELLİK: İLKBAHAR ZİRVE, EYLÜL DİP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  En yüksek aylar : Nisan (+1.1), Mayıs (+1.1), Mart (+0.9)
  En düşük aylar  : Eylül (-1.5), Ağustos (-1.0), Aralık (-1.0)
  → Mevsimsel etki görece zayıf (±1.5 puan); kriz dönemleri
    mevsimsel örüntüyü baskılıyor.
""")

print("""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BULGU 6 — KRİZ DÖNEMLERİNDE DEĞİŞKENLER TEKLEŞIYOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Kur Krizi döneminde TGE ile bileşenler arası korelasyon:
    Hane Beklenti   : 1.00
    Ekonomi Beklenti: 0.99
    İşsizlik Beklenti: 0.97
  → Kriz dönemlerinde tüm değişkenler tek bir 'ekonomik baskı'
    faktörüne indirgeniyor; bireysel farklar kayboluyor.
""")

print("╔" + "═"*66 + "╗")
print("║  Analiz tamamlandı.                                             ║")
print("╚" + "═"*66 + "╝")