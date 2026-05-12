import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"]        = df["YP"] / df["Toplam"] * 100
df["Toplam_haf_deg"] = df["Toplam"].pct_change() * 100
df["TL_haf_deg"]     = df["TL"].pct_change() * 100
df["YP_haf_deg"]     = df["YP"].pct_change() * 100
df["Ay"]  = df["Tarih"].dt.month
df["Yil"] = df["Tarih"].dt.year

AY_TR  = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
           7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
AYLAR  = [AY_TR[i] for i in range(1,13)]

aylik_ort = df.groupby("Ay")[["Toplam_haf_deg","TL_haf_deg","YP_haf_deg"]].mean()
aylik_yp  = df.groupby("Ay")["YP_Payi"].mean()
pivot     = df.pivot_table(index="Yil", columns="Ay", values="Toplam_haf_deg", aggfunc="mean")

ceyrek_ort = df.groupby(df["Tarih"].dt.quarter)[["Toplam_haf_deg","TL_haf_deg","YP_haf_deg"]].mean()

plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,
                     "axes.spines.right":False,"axes.grid":True,
                     "grid.alpha":0.3,"grid.linestyle":"--"})

RENK_TOP = "#1A3C6E"; RENK_TL = "#2E86AB"; RENK_YP = "#E84855"; RENK_YPP = "#F4A261"

fig = plt.figure(figsize=(18, 20))
fig.patch.set_facecolor("#F8F9FA")
gs = GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.32)

# ── 1. Ay bazında ort. haftalık değişim (grouped bar) ────────────────────────
ax1 = fig.add_subplot(gs[0, :])
x = np.arange(12); w = 0.28
ax1.bar(x - w, aylik_ort["Toplam_haf_deg"], w, label="Toplam", color=RENK_TOP, alpha=0.85)
ax1.bar(x,     aylik_ort["TL_haf_deg"],     w, label="TL",     color=RENK_TL,  alpha=0.85)
ax1.bar(x + w, aylik_ort["YP_haf_deg"],     w, label="YP",     color=RENK_YP,  alpha=0.85)
ax1.set_xticks(x); ax1.set_xticklabels(AYLAR, fontsize=11)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.1f}%"))
ax1.axhline(0, color="black", lw=0.8)
ax1.set_title("Ay Bazında Ortalama Haftalık Değişim (%)", fontsize=13, fontweight="bold", pad=12)
ax1.legend(fontsize=11); ax1.set_facecolor("#F8F9FA")
# Aralık & Kasım vurgu
for ay_idx in [10, 11]:
    ax1.axvspan(ay_idx - 0.5, ay_idx + 0.5, alpha=0.12, color="gold", zorder=0)
ax1.text(10, ax1.get_ylim()[1]*0.92, "Yıl Sonu\nEtkisi", ha="center", fontsize=9, color="#888")

# ── 2. Isı haritası ──────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, :])
cmap = mcolors.LinearSegmentedColormap.from_list("rg", ["#E84855","#FFFFFF","#2E86AB"])
im = ax2.imshow(pivot.values, aspect="auto", cmap=cmap,
                vmin=pivot.values[~np.isnan(pivot.values)].min(),
                vmax=pivot.values[~np.isnan(pivot.values)].max())
ax2.set_xticks(range(12)); ax2.set_xticklabels(AYLAR, fontsize=11)
ax2.set_yticks(range(len(pivot.index))); ax2.set_yticklabels(pivot.index, fontsize=11)
ax2.set_title("Yıl × Ay Isı Haritası — Toplam Haftalık Değişim (%)", fontsize=13, fontweight="bold", pad=12)
ax2.grid(False)
for i in range(len(pivot.index)):
    for j in range(12):
        val = pivot.values[i, j]
        if not np.isnan(val):
            ax2.text(j, i, f"{val:.2f}%", ha="center", va="center",
                     fontsize=10, fontweight="bold",
                     color="white" if abs(val) > 1.5 else "#333")
plt.colorbar(im, ax=ax2, shrink=0.6, label="Ort. Haftalık Değişim (%)")

# ── 3. YP Payı mevsimselliği ─────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2, 0])
renkler_yp = [RENK_YP if v > aylik_yp.mean() else RENK_YPP for v in aylik_yp.values]
bars = ax3.bar(range(12), aylik_yp.values, color=renkler_yp, alpha=0.85, width=0.6)
ax3.set_xticks(range(12)); ax3.set_xticklabels(AYLAR, fontsize=10)
ax3.axhline(aylik_yp.mean(), color="gray", lw=1.5, linestyle=":", label=f"Ort: {aylik_yp.mean():.1f}%")
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.1f}%"))
ax3.set_title("Ay Bazında Ortalama YP Payı (%)", fontsize=12, fontweight="bold")
ax3.legend(fontsize=10); ax3.set_facecolor("#F8F9FA")
for bar, val in zip(bars, aylik_yp.values):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f"{val:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

# ── 4. Çeyrek bazında büyüme ─────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 1])
x = np.arange(4); w = 0.28
ceyrek_etiket = ["Q1\n(Oca-Mar)", "Q2\n(Nis-Haz)", "Q3\n(Tem-Eyl)", "Q4\n(Eki-Ara)"]
ax4.bar(x - w, ceyrek_ort["Toplam_haf_deg"], w, label="Toplam", color=RENK_TOP, alpha=0.85)
ax4.bar(x,     ceyrek_ort["TL_haf_deg"],     w, label="TL",     color=RENK_TL,  alpha=0.85)
ax4.bar(x + w, ceyrek_ort["YP_haf_deg"],     w, label="YP",     color=RENK_YP,  alpha=0.85)
ax4.set_xticks(x); ax4.set_xticklabels(ceyrek_etiket, fontsize=10)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.1f}%"))
ax4.set_title("Çeyrek Bazında Ort. Haftalık Değişim (%)", fontsize=12, fontweight="bold")
ax4.legend(fontsize=10); ax4.set_facecolor("#F8F9FA")

fig.suptitle("Finansman Şirketleri — Mevsimsellik Analizi\nHaz 2024 – Nis 2026",
             fontsize=16, fontweight="bold", y=1.01)

plt.savefig("mevsimsellik.png", dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
plt.show()
print("Grafik kaydedildi: mevsimsellik.png")