import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

fig, axes = plt.subplots(2, 1, figsize=(13, 8))
ax1 = axes[0]
ax1.plot(df.index, df["endeks"], color="#2c7bb6", linewidth=1.8, label="Endeks")
ax1.set_title("Tarımsal Girdi Fiyat Endeksi (2020=100)", fontsize=13, fontweight="bold")
ax1.set_ylabel("Endeks Değeri")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax1.axhline(100, color="gray", linestyle="--", linewidth=0.9, alpha=0.7, label="Baz (100)")
ax1.legend()
ax1.grid(axis="y", linestyle="--", alpha=0.4)

ax1.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-01"), alpha=0.12, color="orange", label="Baz Yılı 2020")

df["yillik_pct"] = df["endeks"].pct_change(12) * 100

ax2 = axes[1]
colors = ["#d73027" if v >= 0 else "#4575b4" for v in df["yillik_pct"].dropna()]
ax2.bar(df["yillik_pct"].dropna().index, df["yillik_pct"].dropna(), color=colors, width=20, alpha=0.85)
ax2.axhline(0, color="black", linewidth=0.8)
ax2.set_title("Yıllık Değişim (%)", fontsize=12, fontweight="bold")
ax2.set_ylabel("%")
ax2.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("adim2_gorsellestirme.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim2_gorsellestirme.png")