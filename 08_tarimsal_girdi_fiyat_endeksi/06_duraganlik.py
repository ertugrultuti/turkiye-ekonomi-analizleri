import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss
import warnings
warnings.filterwarnings("ignore")

# --- Veri yükle ---
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

# Log dönüşümü ve fark serileri
df["log"]        = np.log(df["endeks"])
df["fark1"]      = df["endeks"].diff()
df["fark2"]      = df["endeks"].diff().diff()
df["log_fark1"]  = df["log"].diff()
df["log_fark2"]  = df["log"].diff().diff()

# --- Test fonksiyonu ---
def adf_test(seri, isim):
    seri = seri.dropna()
    sonuc = adfuller(seri, autolag="AIC")
    print(f"\n{'='*50}")
    print(f"ADF TESTİ — {isim}")
    print(f"  Test istatistiği : {sonuc[0]:.4f}")
    print(f"  p-değeri         : {sonuc[1]:.4f}")
    print(f"  Kullanılan lag   : {sonuc[2]}")
    print(f"  Gözlem sayısı    : {sonuc[3]}")
    for anahtar, deger in sonuc[4].items():
        print(f"  Kritik değer {anahtar}: {deger:.4f}")
    yorum = "DURAĞAN DEĞİL ✗" if sonuc[1] > 0.05 else "DURAĞAN ✓"
    print(f"  Sonuç            : {yorum}")
    return sonuc[1]

def kpss_test(seri, isim):
    seri = seri.dropna()
    sonuc = kpss(seri, regression="c", nlags="auto")
    print(f"\n{'='*50}")
    print(f"KPSS TESTİ — {isim}")
    print(f"  Test istatistiği : {sonuc[0]:.4f}")
    print(f"  p-değeri         : {sonuc[1]:.4f}")
    for anahtar, deger in sonuc[3].items():
        print(f"  Kritik değer {anahtar}: {deger:.4f}")
    yorum = "DURAĞAN DEĞİL ✗" if sonuc[1] < 0.05 else "DURAĞAN ✓"
    print(f"  Sonuç            : {yorum}")
    return sonuc[1]

# --- Testleri çalıştır ---
seriler = {
    "Ham Endeks"        : df["endeks"],
    "Log(Endeks)"       : df["log"],
    "1. Fark"           : df["fark1"],
    "2. Fark"           : df["fark2"],
    "Log 1. Fark"       : df["log_fark1"],
    "Log 2. Fark"       : df["log_fark2"],
}

print("\n*** ADF TESTLERİ ***")
adf_sonuclar = {isim: adf_test(seri, isim) for isim, seri in seriler.items()}

print("\n\n*** KPSS TESTLERİ ***")
kpss_sonuclar = {isim: kpss_test(seri, isim) for isim, seri in seriler.items()}

# --- Özet tablo ---
print("\n\n=== ÖZET TABLO ===")
print(f"{'Seri':<20} {'ADF p':>10} {'ADF Sonuç':>15} {'KPSS p':>10} {'KPSS Sonuç':>15}")
print("-" * 72)
for isim in seriler:
    adf_p = adf_sonuclar[isim]
    kpss_p = kpss_sonuclar[isim]
    adf_s = "Durağan ✓" if adf_p <= 0.05 else "Dur. Değil ✗"
    kpss_s = "Durağan ✓" if kpss_p >= 0.05 else "Dur. Değil ✗"
    print(f"{isim:<20} {adf_p:>10.4f} {adf_s:>15} {kpss_p:>10.4f} {kpss_s:>15}")

# --- Görselleştirme ---
fig, axes = plt.subplots(3, 2, figsize=(13, 10))
axes = axes.flatten()

for i, (isim, seri) in enumerate(seriler.items()):
    s = seri.dropna()
    axes[i].plot(s.index, s.values, linewidth=1.3, color="#2c7bb6")
    axes[i].set_title(isim, fontweight="bold", fontsize=10)
    adf_p = adf_sonuclar[isim]
    renk = "#2ca02c" if adf_p <= 0.05 else "#d62728"
    axes[i].set_xlabel(f"ADF p={adf_p:.4f}", color=renk, fontsize=9)
    axes[i].grid(axis="y", linestyle="--", alpha=0.4)
    axes[i].axhline(s.mean(), color="gray", linestyle="--", linewidth=0.8, alpha=0.6)

plt.suptitle("Durağanlık Analizi — Seri Dönüşümleri", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim6_duraganlık.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim6_duraganlık.png")