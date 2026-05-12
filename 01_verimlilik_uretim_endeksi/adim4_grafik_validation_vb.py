import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from statsmodels.tsa.statespace.sarimax import SARIMAX

# --- Veri ---
df = pd.read_excel("Veri.xlsx")
df.columns = ["Tarih", "Toplam", "Madencilik", "Imalat"]

def parse_quarter(s):
    yil, ceyrek = s.split("-")
    ay = {"1Ç": 1, "2Ç": 4, "3Ç": 7, "4Ç": 10}[ceyrek]
    return pd.Timestamp(int(yil), ay, 1)

df["Tarih"] = df["Tarih"].apply(parse_quarter)
df = df.set_index("Tarih")
df.index = pd.DatetimeIndex(df.index, freq="QS")

# COVID dummy — pandas Series olarak
covid_dummy = pd.Series(
    (df.index == "2020-04-01").astype(float),
    index=df.index
)

seriler = {
    "Toplam Sanayi": (df["Toplam"],    (0,1,2), (1,1,1,4)),
    "Madencilik":    (df["Madencilik"], (2,1,2), (1,1,1,4)),
    "İmalat":        (df["Imalat"],    (0,1,2), (1,1,1,4)),
}
colors = {"Toplam Sanayi": "#2563EB", "Madencilik": "#16A34A", "İmalat": "#DC2626"}

n_test = 8

# --- Walk-forward validation ---
print("=" * 60)
print("WALK-FORWARD VALIDATION (Son 8 çeyrek test seti)")
print("=" * 60)

fig, axes = plt.subplots(3, 1, figsize=(14, 12))

for ax, (isim, (seri, order, seasonal)) in zip(axes, seriler.items()):
    renk = colors[isim]
    train = seri.iloc[:-n_test]
    test  = seri.iloc[-n_test:]
    covid_train = covid_dummy.iloc[:-n_test]
    covid_test  = covid_dummy.iloc[-n_test:]

    model = SARIMAX(train, order=order, seasonal_order=seasonal,
                    exog=covid_train, enforce_stationarity=False,
                    enforce_invertibility=False)
    fit = model.fit(disp=False)

    forecast = fit.get_forecast(steps=n_test, exog=covid_test)
    pred_mean = forecast.predicted_mean
    pred_ci   = forecast.conf_int(alpha=0.05)

    mae  = np.mean(np.abs(pred_mean.values - test.values))
    rmse = np.sqrt(np.mean((pred_mean.values - test.values)**2))
    mape = np.mean(np.abs((pred_mean.values - test.values) / test.values)) * 100

    ax.plot(train.index, train.values, color=renk, linewidth=1.5, label="Eğitim")
    ax.plot(test.index,  test.values,  color=renk, linewidth=2,
            linestyle="--", marker="o", markersize=5, label="Gerçek (Test)")
    ax.plot(pred_mean.index, pred_mean.values, color="black", linewidth=2,
            marker="s", markersize=5, label="Tahmin")
    ax.fill_between(pred_ci.index, pred_ci.iloc[:,0], pred_ci.iloc[:,1],
                    alpha=0.15, color=renk)
    ax.axvline(x=train.index[-1], color="gray", linestyle=":", linewidth=1.5)
    ax.set_title(f"{isim}  |  MAE={mae:.2f}  RMSE={rmse:.2f}  MAPE={mape:.2f}%",
                 fontsize=12, fontweight="bold")
    ax.set_ylabel("Endeks")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.spines[["top","right"]].set_visible(False)

    print(f"\n{isim}  —  MAE={mae:.3f}  RMSE={rmse:.3f}  MAPE={mape:.3f}%")

plt.suptitle("Walk-Forward Validation — Son 8 Çeyrek", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("06_validation.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nValidation grafiği kaydedildi.")

# --- Gelecek 8 çeyrek tahmini ---
print("\n" + "=" * 60)
print("TAHMİN — 2026Q1–2027Q4 (8 çeyrek)")
print("=" * 60)

fig, axes = plt.subplots(3, 1, figsize=(14, 12))

for ax, (isim, (seri, order, seasonal)) in zip(axes, seriler.items()):
    renk = colors[isim]
    model = SARIMAX(seri, order=order, seasonal_order=seasonal,
                    exog=covid_dummy, enforce_stationarity=False,
                    enforce_invertibility=False)
    fit = model.fit(disp=False)

    future_exog = np.zeros(8)
    forecast = fit.get_forecast(steps=8, exog=future_exog)
    pred_mean = forecast.predicted_mean
    pred_ci   = forecast.conf_int(alpha=0.05)

    pred_mean.index = pd.date_range("2026-01-01", periods=8, freq="QS")
    pred_ci.index   = pred_mean.index
    labels = [f"{y}Q{q}" for y in [2026,2027] for q in [1,2,3,4]]

    ax.plot(seri.index[-16:], seri.values[-16:], color=renk,
            linewidth=2, marker="o", markersize=4, label="Gerçek (Son 4 yıl)")
    ax.plot(pred_mean.index, pred_mean.values, color="black",
            linewidth=2, marker="s", markersize=5, label="Tahmin")
    ax.fill_between(pred_ci.index, pred_ci.iloc[:,0], pred_ci.iloc[:,1],
                    alpha=0.15, color=renk, label="%95 GA")
    ax.axvline(x=seri.index[-1], color="gray", linestyle=":", linewidth=1.5)
    ax.set_title(isim, fontsize=12, fontweight="bold")
    ax.set_ylabel("Endeks")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.spines[["top","right"]].set_visible(False)

    print(f"\n{isim}")
    tablo = pd.DataFrame({
        "Dönem":    labels,
        "Tahmin":   pred_mean.values.round(2),
        "Alt %95":  pred_ci.iloc[:,0].values.round(2),
        "Üst %95":  pred_ci.iloc[:,1].values.round(2),
    })
    print(tablo.to_string(index=False))

plt.suptitle("Gelecek Dönem Tahmini — 2026Q1–2027Q4", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("07_tahmin.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nTahmin grafiği kaydedildi.")