import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from itertools import product

df = pd.read_excel('Veri.xlsx', sheet_name='Veri')
sektorler = ['Tarım', 'Sınai', 'Hizmetler']
tahmin_yillari = [2025, 2026, 2027]

# ── ADF testi (durağanlık kontrolü) ──────────────────────────────
print("=" * 60)
print("DURAĞANLIK TESTİ (ADF)")
print("=" * 60)
for s in sektorler:
    adf_result = adfuller(df[s])
    print(f"{s:12s} → ADF İstatistiği: {adf_result[0]:.3f} | p-değeri: {adf_result[1]:.4f} | "
          f"{'DURAĞAN ✓' if adf_result[1] < 0.05 else 'DURAĞAN DEĞİL ✗'}")

# ── Otomatik ARIMA (p,d,q) seçimi — AIC minimizasyonu ────────────
def auto_arima_aic(series):
    best_aic = np.inf
    best_order = (0, 1, 0)
    for p, d, q in product(range(0, 4), range(0, 2), range(0, 4)):
        try:
            model = ARIMA(series, order=(p, d, q)).fit()
            if model.aic < best_aic:
                best_aic = model.aic
                best_order = (p, d, q)
        except:
            continue
    return best_order, best_aic

print("\n" + "=" * 60)
print("OTOMATİK ARIMA PARAMETRE SEÇİMİ (AIC)")
print("=" * 60)

sonuclar = {}
for s in sektorler:
    order, aic = auto_arima_aic(df[s])
    model = ARIMA(df[s], order=order).fit()
    forecast = model.get_forecast(steps=3)
    tahmin = forecast.predicted_mean.values
    ci = forecast.conf_int(alpha=0.20)  # %80 güven aralığı
    sonuclar[s] = {
        'order': order,
        'aic': aic,
        'model': model,
        'tahmin': tahmin,
        'ci_lower': ci.iloc[:, 0].values,
        'ci_upper': ci.iloc[:, 1].values
    }
    print(f"{s:12s} → ARIMA{order} | AIC: {aic:.1f}")

# ── Tahmin tablosu ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TAHMİN SONUÇLARI (Milyon USD) — %80 Güven Aralığı")
print("=" * 60)
print(f"{'Yıl':>6}  {'Sektör':12s}  {'Tahmin':>10}  {'Alt Sınır':>10}  {'Üst Sınır':>10}")
print("-" * 56)
for i, yil in enumerate(tahmin_yillari):
    for s in sektorler:
        r = sonuclar[s]
        print(f"{yil:>6}  {s:12s}  {r['tahmin'][i]:>10,.0f}  "
              f"{r['ci_lower'][i]:>10,.0f}  {r['ci_upper'][i]:>10,.0f}")
    print("-" * 56)

# ── Toplam tahmin ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TOPLAM TAHMİN (3 SEKTÖR TOPLAMI)")
print("=" * 60)
for i, yil in enumerate(tahmin_yillari):
    toplam = sum(sonuclar[s]['tahmin'][i] for s in sektorler)
    alt = sum(sonuclar[s]['ci_lower'][i] for s in sektorler)
    ust = sum(sonuclar[s]['ci_upper'][i] for s in sektorler)
    print(f"{yil}: {toplam:>10,.0f} Mn USD  (Alt: {alt:,.0f} | Üst: {ust:,.0f})")

# ── Görselleştirme ────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(14, 16))
fig.suptitle("ARIMA Tahmin — Türkiye'ye Yapılan Yatırım Stoku\nSektörel (2025–2027)",
             fontsize=15, fontweight='bold', y=0.99)

renkler = {'Tarım': '#2ecc71', 'Sınai': '#3498db', 'Hizmetler': '#e74c3c'}

for ax, s in zip(axes, sektorler):
    r = sonuclar[s]
    renk = renkler[s]

    # Gerçek veri
    ax.plot(df['Tarih'], df[s], color=renk, linewidth=2.2,
            marker='o', markersize=4, label='Gerçek Veri')

    # Tahmin noktaları
    ax.plot(tahmin_yillari, r['tahmin'], color=renk, linewidth=2,
            marker='D', markersize=7, linestyle='--', label='Tahmin')

    # Güven aralığı
    ax.fill_between(tahmin_yillari, r['ci_lower'], r['ci_upper'],
                    color=renk, alpha=0.18, label='%80 Güven Aralığı')

    # Gerçek → tahmin bağlantı çizgisi
    ax.plot([df['Tarih'].iloc[-1], tahmin_yillari[0]],
            [df[s].iloc[-1], r['tahmin'][0]],
            color=renk, linewidth=1.5, linestyle='--', alpha=0.6)

    # Tahmin değerleri etiket
    for yil, val in zip(tahmin_yillari, r['tahmin']):
        ax.annotate(f"{val:,.0f}", xy=(yil, val),
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=8.5, color=renk, fontweight='bold')

    ax.axvline(x=2024.5, color='gray', linestyle=':', alpha=0.6)
    ax.set_title(f"{s} Sektörü — ARIMA{r['order']}", fontsize=11, fontweight='bold')
    ax.set_ylabel('Milyon USD')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
    ax.set_xticks(list(df['Tarih']) + tahmin_yillari)
    ax.set_xticklabels(list(df['Tarih']) + tahmin_yillari, rotation=45, fontsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.35)
    ax.legend(fontsize=9, loc='upper left')

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('arima_tahmin.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nGrafik kaydedildi: arima_tahmin.png")