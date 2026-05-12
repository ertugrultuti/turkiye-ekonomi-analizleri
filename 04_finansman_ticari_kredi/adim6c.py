import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df = df.set_index("Tarih")

tahmin_hafta = 52
son_tarih  = df.index[-1]
gelecek_idx = pd.date_range(son_tarih + pd.Timedelta(weeks=1), periods=tahmin_hafta, freq="W")

orders = {"Toplam": (3,1,3), "TL": (3,1,3), "YP": (1,1,1)}
sonuclar = {}
for col, order in orders.items():
    log_seri = np.log(df[col].dropna())
    model    = ARIMA(log_seri, order=order).fit()
    fc       = model.get_forecast(steps=tahmin_hafta)
    sonuclar[col] = {
        "tahmin" : np.exp(fc.predicted_mean.values),
        "alt"    : np.exp(fc.conf_int(alpha=0.05).iloc[:,0].values),
        "ust"    : np.exp(fc.conf_int(alpha=0.05).iloc[:,1].values),
        "alt80"  : np.exp(fc.conf_int(alpha=0.20).iloc[:,0].values),
        "ust80"  : np.exp(fc.conf_int(alpha=0.20).iloc[:,1].values),
    }

plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,
                     "axes.spines.right":False,"axes.grid":True,
                     "grid.alpha":0.25,"grid.linestyle":"--"})

RENK_TOP="#1A3C6E"; RENK_TL="#2E86AB"; RENK_YP="#E84855"; RENK_YPP="#F4A261"

fig = plt.figure(figsize=(18, 22))
fig.patch.set_facecolor("#F8F9FA")
gs = GridSpec(3, 2, figure=fig, hspace=0.42, wspace=0.30)

# ── 1. Toplam — Tarihsel + Tahmin ──────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df.index, df["Toplam"]/1000, color=RENK_TOP, lw=2.5, label="Gerçekleşen")
ax1.plot(gelecek_idx, sonuclar["Toplam"]["tahmin"]/1000,
         color=RENK_TOP, lw=2.2, linestyle="--", label="Tahmin (ARIMA 3,1,3)")
ax1.fill_between(gelecek_idx,
                 sonuclar["Toplam"]["alt80"]/1000,
                 sonuclar["Toplam"]["ust80"]/1000,
                 alpha=0.25, color=RENK_TOP, label="%80 Güven Aralığı")
ax1.fill_between(gelecek_idx,
                 sonuclar["Toplam"]["alt"]/1000,
                 sonuclar["Toplam"]["ust"]/1000,
                 alpha=0.12, color=RENK_TOP, label="%95 Güven Aralığı")
ax1.axvline(son_tarih, color="gray", lw=1.2, linestyle=":", alpha=0.8)
ax1.text(son_tarih, ax1.get_ylim()[1]*0.97 if ax1.get_ylim()[1]>0 else 550,
         "  Tahmin\n  başlangıcı", fontsize=9, color="gray")
# Hedef noktaları
for hafta, etiket, offset in [(12,"3A",15), (25,"6A",15), (51,"12A",15)]:
    val = sonuclar["Toplam"]["tahmin"][hafta]/1000
    ax1.annotate(f"{etiket}: {val:,.0f} Mia",
                 xy=(gelecek_idx[hafta], val),
                 xytext=(gelecek_idx[hafta], val+offset),
                 arrowprops=dict(arrowstyle="->", color=RENK_TOP, lw=1.2),
                 fontsize=9, color=RENK_TOP, ha="center")
ax1.set_title("Toplam Ticari Kredi — Tarihsel & 1 Yıllık Tahmin (Milyar TL)",
              fontsize=14, fontweight="bold", pad=12)
ax1.set_ylabel("Milyar TL")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
ax1.legend(fontsize=10); ax1.set_facecolor("#F8F9FA")

# ── 2. TL Tahmin ─────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(df.index, df["TL"]/1000, color=RENK_TL, lw=2.2, label="Gerçekleşen")
ax2.plot(gelecek_idx, sonuclar["TL"]["tahmin"]/1000,
         color=RENK_TL, lw=2.0, linestyle="--", label="Tahmin")
ax2.fill_between(gelecek_idx,
                 sonuclar["TL"]["alt"]/1000, sonuclar["TL"]["ust"]/1000,
                 alpha=0.15, color=RENK_TL)
ax2.fill_between(gelecek_idx,
                 sonuclar["TL"]["alt80"]/1000, sonuclar["TL"]["ust80"]/1000,
                 alpha=0.25, color=RENK_TL)
ax2.axvline(son_tarih, color="gray", lw=1.0, linestyle=":")
son_tl  = df["TL"].iloc[-1]/1000
tah_tl  = sonuclar["TL"]["tahmin"][-1]/1000
ax2.set_title(f"TL Krediler — Tahmin\n{son_tl:,.0f} → {tah_tl:,.0f} Mia (%{(tah_tl/son_tl-1)*100:.1f})",
              fontsize=12, fontweight="bold")
ax2.set_ylabel("Milyar TL")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
ax2.legend(fontsize=10); ax2.set_facecolor("#F8F9FA")

# ── 3. YP Tahmin ─────────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(df.index, df["YP"]/1000, color=RENK_YP, lw=2.2, label="Gerçekleşen")
ax3.plot(gelecek_idx, sonuclar["YP"]["tahmin"]/1000,
         color=RENK_YP, lw=2.0, linestyle="--", label="Tahmin")
ax3.fill_between(gelecek_idx,
                 sonuclar["YP"]["alt"]/1000, sonuclar["YP"]["ust"]/1000,
                 alpha=0.15, color=RENK_YP)
ax3.fill_between(gelecek_idx,
                 sonuclar["YP"]["alt80"]/1000, sonuclar["YP"]["ust80"]/1000,
                 alpha=0.25, color=RENK_YP)
ax3.axvline(son_tarih, color="gray", lw=1.0, linestyle=":")
son_yp  = df["YP"].iloc[-1]/1000
tah_yp  = sonuclar["YP"]["tahmin"][-1]/1000
ax3.set_title(f"YP Krediler — Tahmin\n{son_yp:,.0f} → {tah_yp:,.0f} Mia (%{(tah_yp/son_yp-1)*100:.1f})",
              fontsize=12, fontweight="bold")
ax3.set_ylabel("Milyar TL")
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
ax3.legend(fontsize=10); ax3.set_facecolor("#F8F9FA")

# ── 4. YP Payı tahmini ───────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0])
yp_payi_gercek = (df["YP"] / df["Toplam"] * 100)
yp_payi_tahmin = (sonuclar["YP"]["tahmin"] / sonuclar["Toplam"]["tahmin"] * 100)
ax4.plot(df.index, yp_payi_gercek, color=RENK_YPP, lw=2.2, label="Gerçekleşen")
ax4.plot(gelecek_idx, yp_payi_tahmin, color=RENK_YPP, lw=2.0,
         linestyle="--", label="Tahmin")
ax4.axvline(son_tarih, color="gray", lw=1.0, linestyle=":")
ax4.axhline(yp_payi_tahmin[-1], color=RENK_YPP, lw=0.8, linestyle=":", alpha=0.6)
ax4.set_title(f"YP Payı Tahmini\n{yp_payi_gercek.iloc[-1]:.1f}% → {yp_payi_tahmin[-1]:.1f}%",
              fontsize=12, fontweight="bold")
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.1f}%"))
ax4.legend(fontsize=10); ax4.set_facecolor("#F8F9FA")

# ── 5. Özet tablo ─────────────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
ax5.axis("off")
tablo_data = [
    ["", "Mevcut\n(Nis 26)", "3 Ay\n(Tem 26)", "6 Ay\n(Eki 26)", "12 Ay\n(Nis 27)"],
    ["Toplam (Mia TL)",
     f"{df['Toplam'].iloc[-1]/1000:,.0f}",
     f"{sonuclar['Toplam']['tahmin'][12]/1000:,.0f}",
     f"{sonuclar['Toplam']['tahmin'][25]/1000:,.0f}",
     f"{sonuclar['Toplam']['tahmin'][51]/1000:,.0f}"],
    ["TL (Mia TL)",
     f"{df['TL'].iloc[-1]/1000:,.0f}",
     f"{sonuclar['TL']['tahmin'][12]/1000:,.0f}",
     f"{sonuclar['TL']['tahmin'][25]/1000:,.0f}",
     f"{sonuclar['TL']['tahmin'][51]/1000:,.0f}"],
    ["YP (Mia TL)",
     f"{df['YP'].iloc[-1]/1000:,.0f}",
     f"{sonuclar['YP']['tahmin'][12]/1000:,.0f}",
     f"{sonuclar['YP']['tahmin'][25]/1000:,.0f}",
     f"{sonuclar['YP']['tahmin'][51]/1000:,.0f}"],
    ["YP Payı (%)",
     f"{yp_payi_gercek.iloc[-1]:.1f}%",
     f"{yp_payi_tahmin[12]:.1f}%",
     f"{yp_payi_tahmin[25]:.1f}%",
     f"{yp_payi_tahmin[51]:.1f}%"],
    ["Toplam Büyüme", "—",
     f"%{(sonuclar['Toplam']['tahmin'][12]/df['Toplam'].iloc[-1]-1)*100:.1f}",
     f"%{(sonuclar['Toplam']['tahmin'][25]/df['Toplam'].iloc[-1]-1)*100:.1f}",
     f"%{(sonuclar['Toplam']['tahmin'][51]/df['Toplam'].iloc[-1]-1)*100:.1f}"],
]
tablo = ax5.table(cellText=tablo_data[1:], colLabels=tablo_data[0],
                  cellLoc="center", loc="center", bbox=[0, 0, 1, 1])
tablo.auto_set_font_size(False)
tablo.set_fontsize(10)
for (r, c), cell in tablo.get_celld().items():
    if r == 0:
        cell.set_facecolor("#1A3C6E"); cell.set_text_props(color="white", fontweight="bold")
    elif r % 2 == 0:
        cell.set_facecolor("#EAF2FB")
    cell.set_edgecolor("#CCCCCC")
ax5.set_title("Tahmin Özet Tablosu", fontsize=12, fontweight="bold", pad=15)

fig.suptitle("Finansman Şirketleri — 1 Yıllık ARIMA Tahmin\nNis 2026 → Nis 2027",
             fontsize=16, fontweight="bold", y=1.01)

plt.savefig("tahmin.png", dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
plt.show()
print("Grafik kaydedildi: tahmin.png")