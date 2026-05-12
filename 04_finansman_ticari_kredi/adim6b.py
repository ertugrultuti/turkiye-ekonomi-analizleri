import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import itertools

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df = df.set_index("Tarih")

tahmin_hafta = 52  # 1 yıl
son_tarih    = df.index[-1]
gelecek_idx  = pd.date_range(son_tarih + pd.Timedelta(weeks=1), periods=tahmin_hafta, freq="W")

def en_iyi_arima(seri, max_p=3, max_q=3):
    """AIC'e göre en iyi ARIMA(p,1,q) seç"""
    en_iyi_aic = np.inf
    en_iyi_pd  = (1, 1, 1)
    for p, q in itertools.product(range(max_p+1), range(max_q+1)):
        try:
            model = ARIMA(seri, order=(p, 1, q)).fit()
            if model.aic < en_iyi_aic:
                en_iyi_aic = model.aic
                en_iyi_pd  = (p, 1, q)
        except:
            continue
    return en_iyi_pd, en_iyi_aic

sonuclar = {}

for col in ["Toplam", "TL", "YP"]:
    seri = df[col].dropna()
    log_seri = np.log(seri)

    # En iyi order'ı bul
    order, aic = en_iyi_arima(log_seri)
    print(f"\n{'='*50}")
    print(f"  {col} — En iyi ARIMA{order}  (AIC: {aic:.2f})")

    # Modeli fit et
    model = ARIMA(log_seri, order=order).fit()
    print(model.summary().tables[1])

    # Tahmin üret (log uzayında)
    forecast = model.get_forecast(steps=tahmin_hafta)
    log_tahmin   = forecast.predicted_mean
    log_ci_lower = forecast.conf_int(alpha=0.05).iloc[:, 0]
    log_ci_upper = forecast.conf_int(alpha=0.05).iloc[:, 1]

    # Orijinal uzaya geri dön
    tahmin_df = pd.DataFrame({
        "Tarih"   : gelecek_idx,
        "Tahmin"  : np.exp(log_tahmin.values),
        "Alt_%95" : np.exp(log_ci_lower.values),
        "Ust_%95" : np.exp(log_ci_upper.values),
    })

    # Artık analizi
    residuals = model.resid
    print(f"\n  Artık İstatistikleri:")
    print(f"    Ort: {residuals.mean():.6f}  Std: {residuals.std():.6f}")
    print(f"    Min: {residuals.min():.6f}  Max: {residuals.max():.6f}")

    sonuclar[col] = {
        "order"     : order,
        "aic"       : aic,
        "model"     : model,
        "tahmin_df" : tahmin_df,
    }

# Özet tablo
print("\n\n=== 1 YILLIK TAHMİN ÖZETİ ===")
print(f"\n{'Seri':<10} {'Mevcut':>14} {'3 Ay':>14} {'6 Ay':>14} {'12 Ay':>14}  {'Büyüme'}")
print("-" * 80)
for col in ["Toplam", "TL", "YP"]:
    mevcut = df[col].iloc[-1]
    t      = sonuclar[col]["tahmin_df"]["Tahmin"]
    ay3    = t.iloc[12]
    ay6    = t.iloc[25]
    ay12   = t.iloc[51]
    buy    = (ay12 / mevcut - 1) * 100
    print(f"{col:<10} {mevcut:>14,.1f} {ay3:>14,.1f} {ay6:>14,.1f} {ay12:>14,.1f}  %{buy:>6.1f}")

# Aylık tahmin detayı
print("\n\n=== AYLIK TAHMİN DETAYI (Milyon TL) ===")
toplam_t = sonuclar["Toplam"]["tahmin_df"]
tl_t     = sonuclar["TL"]["tahmin_df"]
yp_t     = sonuclar["YP"]["tahmin_df"]

# Ay sonu değerlerini al
birlesik = pd.DataFrame({
    "Tarih"         : toplam_t["Tarih"],
    "Toplam_Tahmin" : toplam_t["Tahmin"],
    "Toplam_Alt"    : toplam_t["Alt_%95"],
    "Toplam_Ust"    : toplam_t["Ust_%95"],
    "TL_Tahmin"     : tl_t["Tahmin"],
    "YP_Tahmin"     : yp_t["Tahmin"],
})
birlesik["YP_Payi_Tahmin"] = birlesik["YP_Tahmin"] / birlesik["Toplam_Tahmin"] * 100
birlesik["Ay"] = birlesik["Tarih"].dt.to_period("M")
aylik_tahmin = birlesik.groupby("Ay").last().reset_index()

print(f"\n{'Dönem':<12} {'Toplam':>12} {'Alt %95':>12} {'Üst %95':>12} {'TL':>12} {'YP':>10} {'YP%':>7}")
print("-" * 80)
for _, row in aylik_tahmin.iterrows():
    print(f"{str(row['Ay']):<12} {row['Toplam_Tahmin']:>12,.0f} "
          f"{row['Toplam_Alt']:>12,.0f} {row['Toplam_Ust']:>12,.0f} "
          f"{row['TL_Tahmin']:>12,.0f} {row['YP_Tahmin']:>10,.0f} "
          f"{row['YP_Payi_Tahmin']:>6.1f}%")