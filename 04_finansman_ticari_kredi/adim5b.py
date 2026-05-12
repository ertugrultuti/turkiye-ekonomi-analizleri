import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from scipy import stats

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"]        = df["YP"] / df["Toplam"] * 100
df["Toplam_haf_deg"] = df["Toplam"].pct_change() * 100
df["TL_haf_deg"]     = df["TL"].pct_change() * 100
df["YP_haf_deg"]     = df["YP"].pct_change() * 100

# --- 1. Korelasyon matrisi ---
corr_df = df[["Toplam_haf_deg","TL_haf_deg","YP_haf_deg","YP_Payi"]].dropna()
corr = corr_df.corr().round(3)
print("=== KORELASYON MATRİSİ ===")
print(corr.to_string())

# --- 2. TL vs YP haftalık değişim regresyonu ---
temiz = df[["TL_haf_deg","YP_haf_deg"]].dropna()
slope, intercept, r, p, se = stats.linregress(temiz["TL_haf_deg"], temiz["YP_haf_deg"])
print(f"\n=== TL vs YP REGRESYON ===")
print(f"Eğim (β): {slope:.4f}  |  R²: {r**2:.4f}  |  p-değer: {p:.4f}")

# --- 3. Hareketli korelasyon (12 haftalık pencere) ---
df["rolling_corr"] = df["TL_haf_deg"].rolling(12).corr(df["YP_haf_deg"])
print("\n=== HAREKETLİ KORELASYON (12 Haftalık) ===")
print(df[["Tarih","rolling_corr"]].dropna().to_string(index=False))

# --- 4. Ayrışma dönemleri: TL ve YP'nin zıt yönde gittiği haftalar ---
df["ayrisma"] = np.sign(df["TL_haf_deg"]) != np.sign(df["YP_haf_deg"])
ayrisma_df = df[df["ayrisma"] == True][["Tarih","TL_haf_deg","YP_haf_deg"]]
print(f"\n=== AYRI YÖNDE HAREKETLİ HAFTALAR: {len(ayrisma_df)} / {len(df.dropna())} ===")
print(ayrisma_df.to_string(index=False))

# --- 5. YP payındaki trend: lineer regresyon ---
df_clean = df.dropna(subset=["YP_Payi"]).copy()
df_clean["t"] = np.arange(len(df_clean))
sl2, ic2, r2, p2, _ = stats.linregress(df_clean["t"], df_clean["YP_Payi"])
print(f"\n=== YP PAYI TREND ANALİZİ ===")
print(f"Haftalık Ortalama Değişim: {sl2:.4f} pp  |  R²: {r2**2:.4f}  |  p-değer: {p2:.6f}")
print(f"Toplam Trend Etkisi ({len(df_clean)} hafta): {sl2*len(df_clean):.2f} pp")

# --- 6. Yüksek YP büyümesi olan haftalar ---
yp_yuksek = df[df["YP_haf_deg"] > 5][["Tarih","YP_haf_deg","TL_haf_deg","YP_Payi"]]
print(f"\n=== YP HAFTALIK DEĞİŞİM > %5 OLAN HAFTALAR ===")
print(yp_yuksek.to_string(index=False))