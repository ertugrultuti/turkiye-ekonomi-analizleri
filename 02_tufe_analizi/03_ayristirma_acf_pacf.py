import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# ── VERİYİ YÜKLE ─────────────────────────────────────────────────
df = pd.read_excel("Veri.xlsx")
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m')
df = df.set_index('Tarih')
df = df.asfreq('MS')

# ── LOG DÖNÜŞÜMÜ + FARK ALMA ──────────────────────────────────────
df['log_tufe']      = np.log(df['TUFE_Endeks'])
df['log_fark']      = df['log_tufe'].diff(1)       # 1. fark → trendi giderir
df['log_mevs_fark'] = df['log_fark'].diff(12)      # 12. fark → mevsimselliği giderir

# Durağanlaştırılmış seri
print("=== FARK SONRASI EKSİK DEĞER ===")
print(df[['log_fark', 'log_mevs_fark']].isnull().sum())

# ── MEVSİMSEL AYRIŞIM (log seride) ───────────────────────────────
decomp = seasonal_decompose(df['log_tufe'], model='additive', period=12)

fig, axes = plt.subplots(4, 1, figsize=(13, 10))
decomp.observed.plot(ax=axes[0], color='steelblue');  axes[0].set_ylabel('Gözlem')
decomp.trend.plot(ax=axes[1], color='darkorange');    axes[1].set_ylabel('Trend')
decomp.seasonal.plot(ax=axes[2], color='darkgreen');  axes[2].set_ylabel('Mevsimsel')
decomp.resid.plot(ax=axes[3], color='crimson');       axes[3].set_ylabel('Artık')

for ax in axes:
    ax.xaxis.set_major_locator(mdates.YearLocator(3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(alpha=0.3)

axes[0].set_title('Mevsimsel Ayrıştırma (Log TÜFE)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('mevsimsel_ayristirma.png', dpi=150, bbox_inches='tight')
plt.show()

# ── ACF / PACF — 3 SERİ ──────────────────────────────────────────
fig, axes = plt.subplots(3, 2, figsize=(14, 12))

seriler = [
    (df['log_tufe'],         'Log TÜFE (ham)'),
    (df['log_fark'],         'Log TÜFE — 1. Fark'),
    (df['log_mevs_fark'],    'Log TÜFE — 1. + 12. Fark'),
]

for i, (seri, baslik) in enumerate(seriler):
    temiz = seri.dropna()
    plot_acf(temiz,  lags=40, ax=axes[i][0], title=f'ACF  | {baslik}',  color='steelblue')
    plot_pacf(temiz, lags=40, ax=axes[i][1], title=f'PACF | {baslik}', color='crimson',
              method='ywm')
    axes[i][0].grid(alpha=0.3)
    axes[i][1].grid(alpha=0.3)

plt.suptitle('ACF / PACF Analizi', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('acf_pacf.png', dpi=150, bbox_inches='tight')
plt.show()

# ── MEVSİMSEL PATTERN ÖZET ───────────────────────────────────────
df['ay'] = df.index.month
aylik_ort = df.groupby('ay')['log_fark'].mean() * 100

print("\n=== AYLIK ORTALAMA LOG-FARK (%) ===")
aylar = ['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara']
for ay, deger in zip(aylar, aylik_ort):
    bar = '█' * int(abs(deger) * 10)
    print(f"  {ay}: {deger:+.3f}%  {bar}")