import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf
import warnings
warnings.filterwarnings('ignore')

# ── VERİYİ YÜKLE ─────────────────────────────────────────────────
df = pd.read_excel("Veri.xlsx")
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m')
df = df.set_index('Tarih')
df = df.asfreq('MS')
df['log_tufe'] = np.log(df['TUFE_Endeks'])

train = df['log_tufe'][:-12]
test  = df['log_tufe'][-12:]

# ── MODELİ FİT ET ────────────────────────────────────────────────
model = SARIMAX(train,
                order=(1, 1, 0),
                seasonal_order=(0, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False)
sonuc = model.fit(disp=False)

print(sonuc.summary())

# ── TAHMİN (test dönemi + 6 ay ileri) ────────────────────────────
n_ileri = 12 + 6   # 12 ay test + 6 ay gelecek
tahmin  = sonuc.get_forecast(steps=n_ileri)
tahmin_ort   = tahmin.predicted_mean
tahmin_ci    = tahmin.conf_int(alpha=0.05)

# Log'dan orijinal ölçeğe geri dön
pred_orig    = np.exp(tahmin_ort)
ci_low_orig  = np.exp(tahmin_ci.iloc[:, 0])
ci_high_orig = np.exp(tahmin_ci.iloc[:, 1])
test_orig    = np.exp(test)

# ── HATA METRİKLERİ (sadece test dönemi, ilk 12 adım) ────────────
pred_test = pred_orig.iloc[:12]
mae  = np.mean(np.abs(pred_test - test_orig))
rmse = np.sqrt(np.mean((pred_test - test_orig)**2))
mape = np.mean(np.abs((pred_test - test_orig) / test_orig)) * 100

print(f"\n=== TEST DÖNEMİ HATA METRİKLERİ ===")
print(f"  MAE  : {mae:.4f}")
print(f"  RMSE : {rmse:.4f}")
print(f"  MAPE : {mape:.2f}%")

# Aylık enflasyon karşılaştırması
print(f"\n=== GERÇEK vs TAHMİN (Aylık % Değişim) ===")
gercek_aylik = test_orig.pct_change().iloc[1:] * 100
pred_aylik   = pred_test.pct_change().iloc[1:] * 100
karsilastir  = pd.DataFrame({'Gerçek': gercek_aylik.round(2),
                              'Tahmin': pred_aylik.round(2)})
print(karsilastir.to_string())

# ── GRAFİK 1: TAHMİN vs GERÇEK ───────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# -- Üst: Orijinal ölçek
son_60 = df['TUFE_Endeks'].iloc[-60:]   # son 5 yıl
axes[0].plot(son_60.index, son_60, color='steelblue', linewidth=2, label='Gerçek')
axes[0].plot(pred_orig.index, pred_orig, color='crimson',
             linewidth=2, linestyle='--', label='Tahmin')
axes[0].fill_between(pred_orig.index, ci_low_orig, ci_high_orig,
                     color='crimson', alpha=0.15, label='%95 GA')
axes[0].axvline(test.index[0], color='gray', linestyle=':', linewidth=1.5, label='Test başlangıcı')
axes[0].set_title('SARIMA(1,1,0)(0,1,1)[12] — TÜFE Endeks Tahmini', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Endeks Değeri')
axes[0].legend()
axes[0].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(alpha=0.3)

# -- Alt: Yıllık enflasyon karşılaştırması
tum_pred = pred_orig
yillik_gercek = np.exp(df['log_tufe']).pct_change(12).iloc[-24:] * 100
yillik_tahmin = tum_pred.pct_change(12) * 100

axes[1].plot(yillik_gercek.index, yillik_gercek,
             color='steelblue', linewidth=2, label='Gerçek Yıllık Enf.')
axes[1].plot(yillik_tahmin.index, yillik_tahmin,
             color='crimson', linewidth=2, linestyle='--', label='Tahmin Yıllık Enf.')
axes[1].axvline(test.index[0], color='gray', linestyle=':', linewidth=1.5, label='Test başlangıcı')
axes[1].set_title('Yıllık Enflasyon — Gerçek vs Tahmin (%)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('% Değişim')
axes[1].legend()
axes[1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('tahmin_sonuclari.png', dpi=150, bbox_inches='tight')
plt.show()

# ── GRAFİK 2: MODEL TANILARI ─────────────────────────────────────
fig2 = sonuc.plot_diagnostics(figsize=(14, 8))
plt.suptitle('Model Tanı Grafikleri', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('model_tani.png', dpi=150, bbox_inches='tight')
plt.show()