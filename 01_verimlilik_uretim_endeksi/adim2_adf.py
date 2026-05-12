import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings("ignore")

# --- Veri ---
df = pd.read_excel("Veri.xlsx")
df.columns = ["Tarih", "Toplam", "Madencilik", "Imalat"]

def parse_quarter(s):
    yil, ceyrek = s.split("-")
    ay = {"1Ç": 1, "2Ç": 4, "3Ç": 7, "4Ç": 10}[ceyrek]
    return pd.Timestamp(int(yil), ay, 1)

df["Tarih"] = df["Tarih"].apply(parse_quarter)
df = df.set_index("Tarih")

seriler = {
    "Toplam Sanayi": df["Toplam"],
    "Madencilik":    df["Madencilik"],
    "İmalat":        df["Imalat"],
}
colors = {"Toplam Sanayi": "#2563EB", "Madencilik": "#16A34A", "İmalat": "#DC2626"}

# --- 1. STL Ayrıştırma ---
for isim, seri in seriler.items():
    stl = STL(seri, period=4, robust=True)
    res = stl.fit()

    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    renk = colors[isim]

    axes[0].plot(seri.index, seri.values, color=renk, linewidth=1.8)
    axes[0].set_title("Gözlemlenen", fontsize=11)

    axes[1].plot(seri.index, res.trend, color=renk, linewidth=1.8)
    axes[1].set_title("Trend", fontsize=11)

    axes[2].plot(seri.index, res.seasonal, color=renk, linewidth=1.8)
    axes[2].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[2].set_title("Mevsimsellik", fontsize=11)

    axes[3].plot(seri.index, res.resid, color="gray", linewidth=1.2)
    axes[3].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[3].set_title("Artık (Residual)", fontsize=11)

    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(f"STL Ayrıştırma — {isim}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fname = f"03_stl_{isim.replace(' ', '_')}.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"STL grafiği kaydedildi: {fname}")

# --- 2. Durağanlık Testleri ---
def adf_test(seri, isim):
    result = adfuller(seri.dropna(), autolag="AIC")
    return {
        "Seri": isim,
        "ADF İstatistiği": round(result[0], 4),
        "p-değeri": round(result[1], 4),
        "%1 Kritik": round(result[4]["1%"], 4),
        "%5 Kritik": round(result[4]["5%"], 4),
        "Karar": "Durağan ✓" if result[1] < 0.05 else "Durağan Değil ✗"
    }

def kpss_test(seri, isim):
    result = kpss(seri.dropna(), regression="ct", nlags="auto")
    return {
        "Seri": isim,
        "KPSS İstatistiği": round(result[0], 4),
        "p-değeri": round(result[1], 4),
        "%5 Kritik": round(result[3]["5%"], 4),
        "Karar": "Durağan ✓" if result[1] > 0.05 else "Durağan Değil ✗"
    }

print("\n" + "="*60)
print("DURAĞANLIK TESTLERİ — DÜZEY")
print("="*60)

adf_sonuc, kpss_sonuc = [], []
for isim, seri in seriler.items():
    adf_sonuc.append(adf_test(seri, isim))
    kpss_sonuc.append(kpss_test(seri, isim))

print("\n--- ADF Testi (H0: Birim kök var = Durağan değil) ---")
print(pd.DataFrame(adf_sonuc).to_string(index=False))

print("\n--- KPSS Testi (H0: Durağan) ---")
print(pd.DataFrame(kpss_sonuc).to_string(index=False))

# Birinci fark
print("\n" + "="*60)
print("DURAĞANLIK TESTLERİ — BİRİNCİ FARK")
print("="*60)

adf_fark, kpss_fark = [], []
for isim, seri in seriler.items():
    fark = seri.diff().dropna()
    adf_fark.append(adf_test(fark, isim))
    kpss_fark.append(kpss_test(fark, isim))

print("\n--- ADF Testi ---")
print(pd.DataFrame(adf_fark).to_string(index=False))
print("\n--- KPSS Testi ---")
print(pd.DataFrame(kpss_fark).to_string(index=False))

# --- 3. ACF / PACF ---
fig, axes = plt.subplots(3, 2, figsize=(14, 12))

for i, (isim, seri) in enumerate(seriler.items()):
    plot_acf(seri, lags=20, ax=axes[i][0], title=f"ACF — {isim}", color=colors[isim])
    plot_pacf(seri, lags=20, ax=axes[i][1], title=f"PACF — {isim}", color=colors[isim])
    for ax in axes[i]:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("04_acf_pacf.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nACF/PACF grafiği kaydedildi.")