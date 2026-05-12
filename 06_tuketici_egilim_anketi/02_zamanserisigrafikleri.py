import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# ── Veri yükleme ve hazırlık ──────────────────────────────────────────────────
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

# ── Önemli olaylar ────────────────────────────────────────────────────────────
olaylar = {
    "2018-08": "Döviz\nKrizi",
    "2020-03": "Covid-19",
    "2021-12": "Kur\nKrizi",
    "2023-02": "Deprem",
    "2023-05": "Seçim",
}

def olay_ciz(ax, renk="gray", alpha=0.6, fontsize=7.5):
    for tarih_str, etiket in olaylar.items():
        t = pd.Timestamp(tarih_str)
        ax.axvline(t, color=renk, lw=0.9, ls="--", alpha=alpha)
        ymin, ymax = ax.get_ylim()
        ax.text(t, ymax - (ymax - ymin) * 0.04, etiket,
                fontsize=fontsize, color=renk, ha="center", va="top",
                bbox=dict(fc="white", ec="none", alpha=0.6, pad=1))

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 1 — Tüketici Güven Endeksi (TGE) Ana Seri + 12-aylık hareketli ort.
# ════════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 4.5))

ax.plot(df["tarih"], df["TGE"], color="#1f77b4", lw=1.5, label="TGE (aylık)")
ax.plot(df["tarih"], df["TGE"].rolling(12).mean(),
        color="#d62728", lw=2, ls="-", label="12 aylık hareketli ort.")
ax.axhline(100, color="black", lw=0.8, ls=":", alpha=0.5, label="100 eşiği")

ax.set_title("Tüketici Güven Endeksi (Ekim 2013 – Nisan 2026)", fontsize=13, fontweight="bold")
ax.set_ylabel("Endeks değeri")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
olay_ciz(ax)
ax.legend(loc="lower left", fontsize=9)
plt.tight_layout()
plt.savefig("grafik1_TGE.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik1_TGE.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 2 — Mevcut Durum vs Beklenti (Hane + Ekonomi)
# ════════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

# Hane
axes[0].plot(df["tarih"], df["hane_mevcut"],    color="#2ca02c", lw=1.5, label="Mevcut durum")
axes[0].plot(df["tarih"], df["hane_beklenti"],  color="#ff7f0e", lw=1.5, ls="--", label="Beklenti")
axes[0].fill_between(df["tarih"],
                      df["hane_mevcut"], df["hane_beklenti"],
                      alpha=0.12, color="#ff7f0e")
axes[0].set_title("Hanenin Mali Durumu — Mevcut vs Beklenti", fontsize=11, fontweight="bold")
axes[0].set_ylabel("Endeks")
axes[0].legend(fontsize=9)
olay_ciz(axes[0])

# Ekonomi
axes[1].plot(df["tarih"], df["ekonomi_mevcut"],   color="#2ca02c", lw=1.5, label="Mevcut durum")
axes[1].plot(df["tarih"], df["ekonomi_beklenti"], color="#ff7f0e", lw=1.5, ls="--", label="Beklenti")
axes[1].fill_between(df["tarih"],
                      df["ekonomi_mevcut"], df["ekonomi_beklenti"],
                      alpha=0.12, color="#ff7f0e")
axes[1].set_title("Genel Ekonomik Durum — Mevcut vs Beklenti", fontsize=11, fontweight="bold")
axes[1].set_ylabel("Endeks")
axes[1].legend(fontsize=9)
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
olay_ciz(axes[1])

plt.suptitle("Mevcut Durum Değerlendirmesi ve Beklenti Karşılaştırması",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("grafik2_mevcut_beklenti.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik2_mevcut_beklenti.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 3 — Enflasyon Algısı ve Ücret Beklentisi
# ════════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 4.5))

ax.plot(df["tarih"], df["fiyat_dusunce"],  color="#d62728", lw=1.5, label="Geçmiş fiyat değişimi algısı")
ax.plot(df["tarih"], df["fiyat_beklenti"], color="#ff7f0e", lw=1.5, ls="--", label="Gelecek fiyat beklentisi")
ax.plot(df["tarih"], df["ucret_beklenti"], color="#1f77b4", lw=1.5, ls="-.", label="Ücret beklentisi")

ax.set_title("Enflasyon Algısı, Fiyat Beklentisi ve Ücret Beklentisi", fontsize=13, fontweight="bold")
ax.set_ylabel("Endeks değeri")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
olay_ciz(ax)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig("grafik3_enflayon_ucret.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik3_enflayon_ucret.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 4 — Harcama Eğilimleri (Dayanıklı, Yarı-dayanıklı, Otomobil, Konut)
# ════════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

# Dayanıklı tüketim
axes[0].plot(df["tarih"], df["dayanikli_uygunluk"], color="#9467bd", lw=1.5, label="Satın almak için uygunluk (mevcut)")
axes[0].plot(df["tarih"], df["dayanikli_beklenti"],  color="#8c564b", lw=1.5, ls="--", label="Harcama düşüncesi (12 ay sonra)")
axes[0].plot(df["tarih"], df["yari_dayanikli"],      color="#e377c2", lw=1.2, ls=":",  label="Yarı-dayanıklı harcama (3 ay sonra)")
axes[0].set_title("Dayanıklı ve Yarı-Dayanıklı Tüketim Eğilimleri", fontsize=11, fontweight="bold")
axes[0].set_ylabel("Endeks")
axes[0].legend(fontsize=9)
olay_ciz(axes[0])

# Konut & otomobil
axes[1].plot(df["tarih"], df["oto_ihtimal"],    color="#17becf", lw=1.5, label="Otomobil satın alma ihtimali")
axes[1].plot(df["tarih"], df["konut_satin"],    color="#bcbd22", lw=1.5, ls="--", label="Konut satın alma ihtimali")
axes[1].plot(df["tarih"], df["konut_tamirat"],  color="#7f7f7f", lw=1.2, ls=":", label="Konut tamirat harcaması")
axes[1].set_title("Otomobil ve Konut Satın Alma Eğilimleri", fontsize=11, fontweight="bold")
axes[1].set_ylabel("Endeks / Oran")
axes[1].legend(fontsize=9)
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
olay_ciz(axes[1])

plt.suptitle("Harcama Eğilimleri", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("grafik4_harcama.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik4_harcama.png kaydedildi.")

# ════════════════════════════════════════════════════════════════════════════════
# GRAFİK 5 — Tasarruf ve Borç Eğilimleri
# ════════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 4.5))

ax.plot(df["tarih"], df["tasarruf_uygunluk"], color="#2ca02c", lw=1.5, label="Tasarruf için uygunluk (mevcut)")
ax.plot(df["tarih"], df["tasarruf_ihtimal"],  color="#98df8a", lw=1.5, ls="--", label="Tasarruf etme ihtimali (12 ay)")
ax.plot(df["tarih"], df["borc_ihtimal"],      color="#d62728", lw=1.5, ls="-.", label="Borç kullanma ihtimali (3 ay)")

ax.set_title("Tasarruf ve Borçlanma Eğilimleri", fontsize=13, fontweight="bold")
ax.set_ylabel("Endeks / Oran")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
olay_ciz(ax)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig("grafik5_tasarruf_borc.png", dpi=150, bbox_inches="tight")
plt.close()
print("grafik5_tasarruf_borc.png kaydedildi.")

print("\nTüm grafikler kaydedildi.")