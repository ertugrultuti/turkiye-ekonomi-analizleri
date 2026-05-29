import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# --- Veri yükle ---
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")
df.index.freq = "MS"

df["log"] = np.log(df["endeks"])

# --- Train / Test bölümü (son 12 ay test) ---
train = df["log"].iloc[:-12]
test  = df["log"].iloc[-12:]

print(f"Train: {train.index[0].strftime('%Y-%m')} → {train.index[-1].strftime('%Y-%m')}  ({len(train)} gözlem)")
print(f"Test : {test.index[0].strftime('%Y-%m')} → {test.index[-1].strftime('%Y-%m')}  ({len(test)} gözlem)")

# --- SARIMA(1,2,1)(1,0,1)[12] ---
model = SARIMAX(
    train,
    order=(1, 2, 1),
    seasonal_order=(1, 0, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)
fit = model.fit(disp=False)
print("\n=== MODEL ÖZETİ ===")
print(fit.summary())

# --- Test dönemi tahmini ---
pred_test = fit.get_forecast(steps=12)
pred_mean_log = pred_test.predicted_mean
pred_ci_log   = pred_test.conf_int(alpha=0.05)

pred_mean = np.exp(pred_mean_log)
pred_ci_low  = np.exp(pred_ci_log.iloc[:, 0])
pred_ci_high = np.exp(pred_ci_log.iloc[:, 1])
test_orig = np.exp(test)

# --- Hata metrikleri ---
mae  = mean_absolute_error(test_orig, pred_mean)
rmse = np.sqrt(mean_squared_error(test_orig, pred_mean))
mape = np.mean(np.abs((test_orig - pred_mean) / test_orig)) * 100

print("\n=== TEST DÖNEMİ HATA METRİKLERİ ===")
print(f"  MAE  : {mae:.2f}")
print(f"  RMSE : {rmse:.2f}")
print(f"  MAPE : %{mape:.2f}")

# --- 12 ay ileri tahmin (tüm veriyle) ---
model_full = SARIMAX(
    df["log"],
    order=(1, 2, 1),
    seasonal_order=(1, 0, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)
fit_full = model_full.fit(disp=False)

horizon = 12
pred_future = fit_full.get_forecast(steps=horizon)
future_mean_log = pred_future.predicted_mean
future_ci_log   = pred_future.conf_int(alpha=0.05)

future_mean = np.exp(future_mean_log)
future_low  = np.exp(future_ci_log.iloc[:, 0])
future_high = np.exp(future_ci_log.iloc[:, 1])

print("\n=== 12 AYLIK TAHMİN (Nisan 2026 – Mart 2027) ===")
print(f"{'Tarih':<15} {'Tahmin':>10} {'Alt %95':>10} {'Üst %95':>10}")
print("-" * 47)
for tarih, tahmin, alt, ust in zip(future_mean.index, future_mean, future_low, future_high):
    print(f"{tarih.strftime('%Y-%m'):.<15} {tahmin:>10.2f} {alt:>10.2f} {ust:>10.2f}")

# --- Grafik ---
fig, axes = plt.subplots(2, 1, figsize=(13, 10))

# Üst: Train/Test karşılaştırma
ax = axes[0]
ax.plot(train.index, np.exp(train), color="#2c7bb6", linewidth=1.5, label="Eğitim verisi")
ax.plot(test_orig.index, test_orig, color="#1a9641", linewidth=2, label="Gerçek (test)")
ax.plot(pred_mean.index, pred_mean, color="#d62728", linewidth=2, linestyle="--", label="SARIMA tahmini")
ax.fill_between(pred_mean.index, pred_ci_low, pred_ci_high, alpha=0.2, color="#d62728", label="%95 GA")
ax.set_title(f"SARIMA(1,2,1)(1,0,1)[12] — Test Dönemi  |  MAPE: %{mape:.2f}", fontweight="bold")
ax.set_ylabel("Endeks")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# Alt: İleri tahmin
ax = axes[1]
son_24 = df["endeks"].iloc[-24:]
ax.plot(son_24.index, son_24, color="#2c7bb6", linewidth=1.8, label="Gerçek (son 24 ay)")
ax.plot(future_mean.index, future_mean, color="#d62728", linewidth=2.2,
        linestyle="--", label="12 Aylık Tahmin", marker="o", markersize=4)
ax.fill_between(future_mean.index, future_low, future_high,
                alpha=0.2, color="#d62728", label="%95 Güven Aralığı")
# Son gerçek değer ile tahmini birleştir
ax.plot([son_24.index[-1], future_mean.index[0]],
        [son_24.iloc[-1], future_mean.iloc[0]],
        color="#d62728", linewidth=2.2, linestyle="--")
ax.set_title("12 Aylık İleri Tahmin (Nisan 2026 – Mart 2027)", fontweight="bold")
ax.set_ylabel("Endeks")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# Tahmin değerlerini grafik üzerine yaz
for tarih, val in zip(future_mean.index[::3], future_mean.iloc[::3]):
    ax.annotate(f"{val:.0f}", xy=(tarih, val), xytext=(0, 10),
                textcoords="offset points", ha="center", fontsize=8, color="#a50026")

plt.suptitle("Tarımsal Girdi Fiyat Endeksi — SARIMA Tahmini", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("adim10_sarima.png", dpi=150, bbox_inches="tight")
plt.show()
print("Kaydedildi: adim10_sarima.png")