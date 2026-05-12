import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"] = (df["YP"] / df["Toplam"] * 100)
df["Toplam_haf_deg"] = df["Toplam"].pct_change() * 100

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

fig = plt.figure(figsize=(18, 20))
fig.patch.set_facecolor("#F8F9FA")
gs = GridSpec(3, 2, figure=fig, hspace=0.42, wspace=0.32)

RENK_TOP  = "#1A3C6E"
RENK_TL   = "#2E86AB"
RENK_YP   = "#E84855"
RENK_YPP  = "#F4A261"

# ── 1. Toplam, TL, YP Seyri ──────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
ax1.fill_between(df["Tarih"], df["TL"] / 1000, alpha=0.15, color=RENK_TL)
ax1.fill_between(df["Tarih"], df["YP"] / 1000, alpha=0.15, color=RENK_YP)
ax1.plot(df["Tarih"], df["Toplam"] / 1000, color=RENK_TOP, lw=2.5, label="Toplam")
ax1.plot(df["Tarih"], df["TL"]     / 1000, color=RENK_TL,  lw=2.0, label="TL", linestyle="--")
ax1.plot(df["Tarih"], df["YP"]     / 1000, color=RENK_YP,  lw=2.0, label="YP", linestyle="-.")
ax1.set_title("Finansman Şirketleri Ticari Kredi Büyüklüğü (Milyar TL)", fontsize=14, fontweight="bold", pad=12)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax1.set_ylabel("Milyar TL")
ax1.legend(fontsize=11)
ax1.set_facecolor("#F8F9FA")

# Periyot arka planları
periyotlar = [
    ("2024-06-28", "2024-12-27", "#D4E6F1", "2024 H2"),
    ("2025-01-03", "2025-06-27", "#D5F5E3", "2025 H1"),
    ("2025-07-04", "2025-12-26", "#FDEBD0", "2025 H2"),
    ("2026-01-02", "2026-04-10", "#F9EBEA", "2026 YTD"),
]
for bas, bit, renk, etiket in periyotlar:
    ax1.axvspan(pd.Timestamp(bas), pd.Timestamp(bit), alpha=0.35, color=renk, zorder=0)
    ax1.text(pd.Timestamp(bas) + (pd.Timestamp(bit) - pd.Timestamp(bas)) / 2,
             ax1.get_ylim()[1] if ax1.get_ylim()[1] > 0 else 270,
             etiket, ha="center", va="top", fontsize=9, color="#555555")

# ── 2. YP Payı ───────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(df["Tarih"], df["YP_Payi"], color=RENK_YPP, lw=2.2)
ax2.fill_between(df["Tarih"], df["YP_Payi"], alpha=0.2, color=RENK_YPP)
ax2.axhline(df["YP_Payi"].mean(), color="gray", lw=1.2, linestyle=":", label=f"Ortalama: {df['YP_Payi'].mean():.1f}%")
ax2.set_title("YP Payı (%)", fontsize=12, fontweight="bold")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
ax2.legend(fontsize=10)
ax2.set_facecolor("#F8F9FA")

# ── 3. Haftalık % Değişim ────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
renkler = [RENK_TL if v >= 0 else RENK_YP for v in df["Toplam_haf_deg"].fillna(0)]
ax3.bar(df["Tarih"], df["Toplam_haf_deg"].fillna(0), color=renkler, width=5, alpha=0.85)
ax3.axhline(0, color="black", lw=0.8)
ax3.set_title("Haftalık Değişim — Toplam (%)", fontsize=12, fontweight="bold")
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
ax3.set_facecolor("#F8F9FA")

# ── 4. Büyümeye Katkı (TL vs YP, mutlak) ────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0])
periyot_isimleri = ["2024 H2", "2025 H1", "2025 H2", "2026\nYTD"]
tl_katki  = [31688.6, 25956.6, 71622.7, 2056.8]
yp_katki  = [1690.6,  9197.3,  1607.2,  1529.2]
x = np.arange(len(periyot_isimleri))
w = 0.35
ax4.bar(x - w/2, [t/1000 for t in tl_katki], w, label="TL Katkı", color=RENK_TL, alpha=0.85)
ax4.bar(x + w/2, [y/1000 for y in yp_katki], w, label="YP Katkı", color=RENK_YP, alpha=0.85)
ax4.set_xticks(x)
ax4.set_xticklabels(periyot_isimleri)
ax4.set_title("Büyümeye Katkı — TL vs YP (Milyar TL)", fontsize=12, fontweight="bold")
ax4.set_ylabel("Milyar TL")
ax4.legend(fontsize=10)
ax4.set_facecolor("#F8F9FA")

# ── 5. Periyot Büyüme Oranları ───────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
p_isimleri = ["2024 H2", "2025 H1", "2025 H2", "2026 YTD"]
toplam_buy = [28.5, 23.0, 37.9, 1.3]
tl_buy     = [32.3, 19.6, 44.3, 0.9]
yp_buy     = [8.9,  44.8, 5.1,  4.5]
x = np.arange(len(p_isimleri))
w = 0.25
ax5.bar(x - w, toplam_buy, w, label="Toplam", color=RENK_TOP, alpha=0.85)
ax5.bar(x,     tl_buy,     w, label="TL",     color=RENK_TL,  alpha=0.85)
ax5.bar(x + w, yp_buy,     w, label="YP",     color=RENK_YP,  alpha=0.85)
ax5.set_xticks(x)
ax5.set_xticklabels(p_isimleri)
ax5.set_title("Periyot Büyüme Oranları (%)", fontsize=12, fontweight="bold")
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax5.legend(fontsize=10)
ax5.set_facecolor("#F8F9FA")

fig.suptitle("Finansman Şirketleri — Ticari Kredi Analizi\nHaz 2024 – Nis 2026",
             fontsize=16, fontweight="bold", y=1.01)

plt.savefig("kredi_analizi.png", dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
plt.show()
print("Grafik kaydedildi: kredi_analizi.png")