import pandas as pd
import numpy as np
import itertools
import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings('ignore')

# ── VERİYİ YÜKLE ─────────────────────────────────────────────────
df = pd.read_excel("Veri.xlsx")
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m')
df = df.set_index('Tarih')
df = df.asfreq('MS')
df['log_tufe'] = np.log(df['TUFE_Endeks'])

# ── TRAIN / TEST AYIRIMI ──────────────────────────────────────────
# Son 12 ayı test için ayır
train = df['log_tufe'][:-12]
test  = df['log_tufe'][-12:]

print(f"Train: {train.index[0].strftime('%Y-%m')} → {train.index[-1].strftime('%Y-%m')}  ({len(train)} gözlem)")
print(f"Test : {test.index[0].strftime('%Y-%m')}  → {test.index[-1].strftime('%Y-%m')}  ({len(test)} gözlem)")

# ── AIC GRID SEARCH ───────────────────────────────────────────────
p_vals = [0, 1, 2]
q_vals = [0, 1, 2]
P_vals = [0, 1]
Q_vals = [0, 1]
d, D, S = 1, 1, 12

sonuclar = []

toplam = len(p_vals) * len(q_vals) * len(P_vals) * len(Q_vals)
sayac = 0

print(f"\n{toplam} kombinasyon deneniyor...\n")

for p, q, P, Q in itertools.product(p_vals, q_vals, P_vals, Q_vals):
    sayac += 1
    try:
        model = SARIMAX(train,
                        order=(p, d, q),
                        seasonal_order=(P, D, Q, S),
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        sonuc = model.fit(disp=False)
        sonuclar.append({
            'order': f'({p},{d},{q})({P},{D},{Q})[{S}]',
            'AIC': round(sonuc.aic, 2),
            'BIC': round(sonuc.bic, 2)
        })
        print(f"  [{sayac:2d}/{toplam}] SARIMA{f'({p},{d},{q})({P},{D},{Q})[{S}]':25s} AIC={sonuc.aic:.2f}")
    except Exception as e:
        print(f"  [{sayac:2d}/{toplam}] SARIMA({p},{d},{q})({P},{D},{Q})[{S}] → HATA: {e}")

# ── SONUÇLARI SIRALA ─────────────────────────────────────────────
sonuc_df = pd.DataFrame(sonuclar).sort_values('AIC').reset_index(drop=True)

print("\n=== EN İYİ 5 MODEL (AIC'ye göre) ===")
print(sonuc_df.head(5).to_string(index=False))