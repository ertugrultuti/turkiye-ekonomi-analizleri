import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from scipy import stats

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"]        = df["YP"] / df["Toplam"] * 100
df["Toplam_haf_deg"] = df["Toplam"].pct_change() * 100
df["TL_haf_deg"]     = df["TL"].pct_change() * 100
df["YP_haf_deg"]     = df["YP"].pct_change() * 100
df["rolling_corr"]   = df["TL_haf_deg"].rolling(12).corr(df["YP_haf_deg"])
df["ayrisma"]        = np.sign(df["TL_haf_deg"]) != np.sign(df["YP_haf_deg"])
df["t"]              = np.arange(len(df))

temiz = df.dropna(subset=["TL_haf_deg","YP_haf_deg"])
slope, intercept, r, p, _ = stats.linregress(temiz["TL_haf_deg"], temiz["YP_haf_deg"])
sl_yp, ic_yp, r_yp, p_yp, _ = stats.linregress(
    df.dropna(subset=["YP_Payi"])["t"], df.dropna(subset=["YP_Payi"])["YP_Payi"])

plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,
                     "axes.spines.right":False,"axes.grid":True,
                     "grid.alpha":0.3,"grid.linestyle":"--"})

RENK_TOP="#1A3C6E"; RENK_TL="#2E86AB"; RENK_YP="#E84855"
RENK_YPP="#F4A261"; RENK_GRI="#888888"

fig = plt.figure(figsize=(18, 22))
fig.patch.set_facecolor("#F8F9FA")
gs = GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.32)

# ── 1. TL vs YP scatter + regresyon ─────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ayri   = temiz[temiz["ayrisma"] == True]
beraber = temiz[temiz["ayrisma"] == False]
ax1.scatter(beraber["TL_haf_deg"], beraber["YP_haf_deg"],
            color=RENK_TL, alpha=0.6, s=50, label="Aynı yön", zorder=3)
ax1.scatter(ayri["TL_haf_deg"], ayri["YP_haf_deg"],
            color=RENK_YP, alpha=0.7, s=60, marker="X", label="Ayrışma", zorder=4)
x_line = np.linspace(temiz["TL_haf_deg"].min(), temiz["TL_haf_deg"].max(), 100)
ax1.plot(x_line, slope * x_line + intercept, color=RENK_GRI, lw=1.5,
         linestyle="--", label=f"Regresyon (R²={r**2:.3f})")
ax1.axhline(0, color="black", lw=0.7); ax1.axvline(0, color="black", lw=0.7)
ax1.set_xlabel("TL Haftalık Değişim (%)"); ax1.set_ylabel("YP Haftalık Değişim (%)")
ax1.set_title("TL vs YP Haftalık Değişim\nSaçılım Grafiği", fontsize=12, fontweight="bold")
ax1.legend(fontsize=9); ax1.set_facecolor("#F8F9FA")
# Quadrant etiketleri
ax1.text( 3,  12, "İkisi de\n↑", ha="center", fontsize=8, color="#2E7D32", alpha=0.7)
ax1.text(-2,  12, "TL↓ YP↑\nAyrışma", ha="center", fontsize=8, color=RENK_YP, alpha=0.7)
ax1.text( 3,  -5, "TL↑ YP↓\nAyrışma", ha="center", fontsize=8, color=RENK_YP, alpha=0.7)
ax1.text(-2,  -5, "İkisi de\n↓", ha="center", fontsize=8, color="#B71C1C", alpha=0.7)

# ── 2. Korelasyon matrisi ısı haritası ───────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
etiketler = ["Toplam\nDeğ.", "TL\nDeğ.", "YP\nDeğ.", "YP\nPayı"]
corr_vals = np.array([
    [1.000, 0.976, 0.367, -0.065],
    [0.976, 1.000, 0.159, -0.084],
    [0.367, 0.159, 1.000,  0.071],
    [-0.065,-0.084, 0.071, 1.000],
])
import matplotlib.colors as mcolors
cmap2 = mcolors.LinearSegmentedColormap.from_list("rb",["#E84855","#FFFFFF","#2E86AB"])
im2 = ax2.imshow(corr_vals, cmap=cmap2, vmin=-1, vmax=1, aspect="auto")
ax2.set_xticks(range(4)); ax2.set_xticklabels(etiketler, fontsize=10)
ax2.set_yticks(range(4)); ax2.set_yticklabels(etiketler, fontsize=10)
ax2.set_title("Korelasyon Matrisi", fontsize=12, fontweight="bold")
ax2.grid(False)
for i in range(4):
    for j in range(4):
        renk = "white" if abs(corr_vals[i,j]) > 0.6 else "#333"
        ax2.text(j, i, f"{corr_vals[i,j]:.3f}", ha="center", va="center",
                 fontsize=11, fontweight="bold", color=renk)
plt.colorbar(im2, ax=ax2, shrink=0.8)
ax2.set_facecolor("#F8F9FA")

# ── 3. Hareketli korelasyon (TL–YP, 12 haftalık) ────────────────────────────
ax3 = fig.add_subplot(gs[1, :])
rc = df.dropna(subset=["rolling_corr"])
renkler_rc = [RENK_TL if v >= 0 else RENK_YP for v in rc["rolling_corr"]]
ax3.bar(rc["Tarih"], rc["rolling_corr"], color=renkler_rc, width=6, alpha=0.75)
ax3.axhline(0, color="black", lw=0.8)
ax3.axhline(0.5,  color=RENK_TL, lw=1.2, linestyle=":", alpha=0.7, label="±0.5 eşiği")
ax3.axhline(-0.5, color=RENK_YP, lw=1.2, linestyle=":", alpha=0.7)
ax3.fill_between(rc["Tarih"], rc["rolling_corr"], 0,
                 where=rc["rolling_corr"] >= 0, alpha=0.12, color=RENK_TL)
ax3.fill_between(rc["Tarih"], rc["rolling_corr"], 0,
                 where=rc["rolling_corr"] < 0,  alpha=0.12, color=RENK_YP)
ax3.set_title("TL – YP Hareketli Korelasyon (12 Haftalık Pencere)", fontsize=13, fontweight="bold")
ax3.set_ylabel("Pearson r"); ax3.legend(fontsize=10)
ax3.set_ylim(-0.6, 1.0); ax3.set_facecolor("#F8F9FA")
# Dönem etiketleri
ax3.text(pd.Timestamp("2024-12-15"), 0.88, "Yılsonu\nuyumu", fontsize=8.5,
         color=RENK_TL, ha="center")
ax3.text(pd.Timestamp("2025-05-01"), -0.08, "Tam\nayrışma", fontsize=8.5,
         color=RENK_YP, ha="center")
ax3.text(pd.Timestamp("2025-11-20"), 0.88, "Yılsonu\nuyumu", fontsize=8.5,
         color=RENK_TL, ha="center")
ax3.text(pd.Timestamp("2025-09-20"), -0.5, "Negatif\nkorelasyon", fontsize=8.5,
         color=RENK_YP, ha="center")

# ── 4. YP Payı trend ─────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0])
df_c = df.dropna(subset=["YP_Payi"])
ax4.plot(df_c["Tarih"], df_c["YP_Payi"], color=RENK_YPP, lw=2, label="YP Payı")
ax4.fill_between(df_c["Tarih"], df_c["YP_Payi"], alpha=0.15, color=RENK_YPP)
trend_line = sl_yp * df_c["t"] + ic_yp
ax4.plot(df_c["Tarih"], trend_line, color=RENK_GRI, lw=2, linestyle="--",
         label=f"Trend (−{abs(sl_yp)*52:.2f} pp/yıl)")
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.1f}%"))
ax4.set_title("YP Payı — Trend Analizi", fontsize=12, fontweight="bold")
ax4.legend(fontsize=10); ax4.set_facecolor("#F8F9FA")

# ── 5. Ayrışma haftaları takvim görünümü ────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
df_plot = df.dropna(subset=["TL_haf_deg","YP_haf_deg"]).copy()
df_plot["fark"] = df_plot["TL_haf_deg"] - df_plot["YP_haf_deg"]
renkler_f = [RENK_TL if v >= 0 else RENK_YP for v in df_plot["fark"]]
ax5.bar(df_plot["Tarih"], df_plot["fark"], color=renkler_f, width=6, alpha=0.8)
ax5.axhline(0, color="black", lw=0.8)
ax5.set_title("TL − YP Haftalık Değişim Farkı (pp)\n(+: TL güçlü  /  −: YP güçlü)",
              fontsize=12, fontweight="bold")
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.1f}pp"))
ax5.set_facecolor("#F8F9FA")
# En belirgin YP ayrışması
ax5.annotate("Nis 2025\nYP sıçraması\n(+15.6%)", xy=(pd.Timestamp("2025-04-18"), -14.6),
             xytext=(pd.Timestamp("2025-01-01"), -12),
             arrowprops=dict(arrowstyle="->", color=RENK_YP), fontsize=9, color=RENK_YP)

fig.suptitle("Finansman Şirketleri — Korelasyon & TL/YP Ayrışma Analizi\nHaz 2024 – Nis 2026",
             fontsize=16, fontweight="bold", y=1.01)

plt.savefig("korelasyon_ayrisma.png", dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
plt.show()
print("Grafik kaydedildi: korelasyon_ayrisma.png")