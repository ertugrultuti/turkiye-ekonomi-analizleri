import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.tsa.vector_ar.var_model import VAR

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df.columns = ["tarih", "bist100", "fed", "tcmb", "usdtl", "cds",
              "bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
data = df[["bist_ret", "fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]].dropna()

labels = {
    "bist_ret": "BIST 100",
    "fed_ret": "Fed Faizi",
    "tcmb_ret": "TCMB Faizi",
    "usdtl_ret": "USD/TL",
    "cds_ret": "CDS"
}

model = VAR(data)
lag_result = model.select_order(maxlags=12)
var_model = model.fit(lag_result.selected_orders["aic"])
irf = var_model.irf(periods=12)
fevd = var_model.fevd(periods=12)

fig, axes = plt.subplots(5, 1, figsize=(12, 14), sharex=True)
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

for i, (col, ax) in enumerate(zip(data.columns, axes)):
    ax.plot(data.index, data[col], color=colors[i], linewidth=1.2)
    ax.set_ylabel(labels[col], fontsize=10)
    ax.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))

axes[0].set_title("Değişkenlerin Aylık % Değişimleri", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("grafik1_zaman_serisi.png", dpi=150, bbox_inches="tight")
plt.show()
print("grafik1 kaydedildi")

import matplotlib.colors as mcolors

corr = data.rename(columns=labels).corr()
fig, ax = plt.subplots(figsize=(8, 6))
cmap = plt.cm.RdBu_r
im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
ax.set_xticks(range(len(corr)))
ax.set_yticks(range(len(corr)))
ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=10)
ax.set_yticklabels(corr.columns, fontsize=10)

for i in range(len(corr)):
    for j in range(len(corr)):
        val = corr.iloc[i, j]
        color = "white" if abs(val) > 0.5 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                fontsize=10, color=color, fontweight="bold")

ax.set_title("Korelasyon Isı Haritası", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("grafik2_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()
print("grafik2 kaydedildi")

impulses = ["fed_ret", "tcmb_ret", "usdtl_ret", "cds_ret"]
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

irf_obj = var_model.irf(periods=12)
se_array = irf_obj.stderr()  

for i, imp in enumerate(impulses):
    ax = axes[i]
    idx_imp = list(data.columns).index(imp)
    idx_resp = list(data.columns).index("bist_ret")

    irf_vals = irf_obj.irfs[:, idx_resp, idx_imp]
    se = se_array[:, idx_resp, idx_imp]
    periods = range(len(irf_vals))

    ax.plot(periods, irf_vals, color=colors[i+1], linewidth=2)
    ax.fill_between(periods,
                    irf_vals - 1.96 * se,
                    irf_vals + 1.96 * se,
                    alpha=0.2, color=colors[i+1])
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title(f"{labels[imp]} → BIST 100", fontsize=11, fontweight="bold")
    ax.set_xlabel("Ay")
    ax.set_ylabel("Etki")

fig.suptitle("Etki-Tepki Analizi (IRF)", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("grafik3_irf.png", dpi=150, bbox_inches="tight")
plt.show()
print("grafik3 kaydedildi")

fevd_df = pd.DataFrame(
    fevd.decomp[list(data.columns).index("bist_ret")],
    columns=data.columns
).rename(columns=labels)

fevd_ext = fevd_df.drop(columns=["BIST 100"])
x = range(1, 13)

fig, ax = plt.subplots(figsize=(10, 5))
bottom = np.zeros(12)
ext_colors = ["#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

for col, c in zip(fevd_ext.columns, ext_colors):
    ax.bar(x, fevd_ext[col], bottom=bottom, label=col, color=c, alpha=0.85)
    bottom += fevd_ext[col].values

ax.set_xlabel("Dönem (Ay)", fontsize=11)
ax.set_ylabel("Açıklama Payı", fontsize=11)
ax.set_title("Varyans Ayrıştırması — BIST 100 (Dış Değişkenler)", fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
ax.legend(loc="upper right", fontsize=10)
ax.set_xticks(list(x))
plt.tight_layout()
plt.savefig("grafik4_fevd.png", dpi=150, bbox_inches="tight")
plt.show()
print("grafik4 kaydedildi")
