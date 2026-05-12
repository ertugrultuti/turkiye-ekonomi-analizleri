import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.stattools import adfuller, kpss

# ── VERİYİ YÜKLE ─────────────────────────────────────────────────
df = pd.read_excel("Veri.xlsx")
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m')
df = df.set_index('Tarih')
df = df.asfreq('MS')
df['Yillik_Enf'] = df['TUFE_Endeks'].pct_change(12) * 100
df['Aylik_Enf']  = df['TUFE_Endeks'].pct_change(1) * 100

# ── ADF VE KPSS TEST FONKSİYONU ──────────────────────────────────
def duraginlik_testi(seri, isim):
    temiz = seri.dropna()
    print(f"\n{'='*50}")
    print(f"  {isim}")
    print(f"{'='*50}")

    # ADF Testi (H0: Birim kök VAR → durağan DEĞİL)
    adf_sonuc = adfuller(temiz, autolag='AIC')
    print(f"\n[ADF Testi]")
    print(f"  İstatistik : {adf_sonuc[0]:.4f}")
    print(f"  p-değeri   : {adf_sonuc[1]:.4f}")
    print(f"  Sonuç      : {'✅ Durağan (H0 red)' if adf_sonuc[1] < 0.05 else '❌ Durağan DEĞİL'}")

    # KPSS Testi (H0: Durağan)
    kpss_sonuc = kpss(temiz, regression='c', nlags='auto')
    print(f"\n[KPSS Testi]")
    print(f"  İstatistik : {kpss_sonuc[0]:.4f}")
    print(f"  p-değeri   : {kpss_sonuc[1]:.4f}")
    print(f"  Sonuç      : {'❌ Durağan DEĞİL (H0 red)' if kpss_sonuc[1] < 0.05 else '✅ Durağan'}")

# ── 4 SERİYİ TEST ET ─────────────────────────────────────────────
duraginlik_testi(df['TUFE_Endeks'],          '1) Ham Endeks')
duraginlik_testi(np.log(df['TUFE_Endeks']), '2) Log Endeks')
duraginlik_testi(df['Aylik_Enf'],            '3) Aylık Enflasyon (%)')
duraginlik_testi(df['Yillik_Enf'],           '4) Yıllık Enflasyon (%)')

# ── GÖRSELLEŞTİR ─────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

seriler = [
    (df['TUFE_Endeks'],          'Ham Endeks',          'steelblue'),
    (np.log(df['TUFE_Endeks']), 'Log Endeks',           'darkorange'),
    (df['Aylik_Enf'],            'Aylık Enflasyon (%)', 'crimson'),
    (df['Yillik_Enf'],           'Yıllık Enflasyon (%)', 'darkgreen'),
]

for ax, (seri, baslik, renk) in zip(axes.flat, seriler):
    ax.plot(seri.index, seri, color=renk, linewidth=1.2)
    ax.set_title(baslik, fontweight='bold')
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(alpha=0.3)

plt.suptitle('Durağanlık Analizi — Farklı Dönüşümler', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('duraginlik_analizi.png', dpi=150, bbox_inches='tight')
plt.show()