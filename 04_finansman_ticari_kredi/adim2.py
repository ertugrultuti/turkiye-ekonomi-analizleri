import pandas as pd
import numpy as np

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"] = (df["YP"] / df["Toplam"] * 100).round(2)

# --- Haftalık Değişim (%) ---
for col in ["Toplam", "TL", "YP"]:
    df[f"{col}_haf_deg"] = df[col].pct_change() * 100

# --- Aylık bazda gruplama (ay sonu değerleri) ---
df["Yil_Ay"] = df["Tarih"].dt.to_period("M")
aylik = df.groupby("Yil_Ay").last().reset_index()
for col in ["Toplam", "TL", "YP"]:
    aylik[f"{col}_aylik_deg"] = aylik[col].pct_change() * 100

# --- Yıllık bazda (yıl sonu değerleri) ---
df["Yil"] = df["Tarih"].dt.year
yillik = df.groupby("Yil").last().reset_index()[["Yil", "Toplam", "TL", "YP", "YP_Payi"]]

# --- Dönem başı/sonu karşılaştırması ---
ilk = df.iloc[0]
son = df.iloc[-1]
sure_gun = (son["Tarih"] - ilk["Tarih"]).days
sure_yil = sure_gun / 365

print("=== DÖNEM BAŞI / SONU KARŞILAŞTIRMA ===")
print(f"Başlangıç: {ilk['Tarih'].date()}  |  Bitiş: {son['Tarih'].date()}  |  Süre: {sure_gun} gün ({sure_yil:.1f} yıl)")
print(f"\n{'':20} {'Başlangıç':>15} {'Bitiş':>15} {'Mutlak Değ.':>15} {'% Değ.':>10} {'CAGR':>8}")
for col in ["Toplam", "TL", "YP"]:
    bas = ilk[col]
    bit = son[col]
    mutlak = bit - bas
    pct = (bit / bas - 1) * 100
    cagr = ((bit / bas) ** (1 / sure_yil) - 1) * 100
    print(f"{col:20} {bas:>15,.1f} {bit:>15,.1f} {mutlak:>15,.1f} {pct:>9.1f}% {cagr:>7.1f}%")

print(f"\nYP Payı Başlangıç: {ilk['YP_Payi']:.2f}%  →  Bitiş: {son['YP_Payi']:.2f}%")

print("\n=== AYLIK DEĞİŞİM (%) ===")
print(aylik[["Yil_Ay", "Toplam", "TL", "YP", "Toplam_aylik_deg", "TL_aylik_deg", "YP_aylik_deg"]].to_string(index=False))

print("\n=== YILLIK ÖZET ===")
print(yillik.to_string(index=False))

print("\n=== HAFTALIK DEĞİŞİM İSTATİSTİKLERİ ===")
for col in ["Toplam", "TL", "YP"]:
    seri = df[f"{col}_haf_deg"].dropna()
    print(f"\n{col}:")
    print(f"  Ort: {seri.mean():.2f}%  |  Std: {seri.std():.2f}%  |  Min: {seri.min():.2f}%  |  Max: {seri.max():.2f}%")
    print(f"  Pozitif hafta: {(seri>0).sum()}  |  Negatif hafta: {(seri<0).sum()}")