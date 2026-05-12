import pandas as pd
import numpy as np

# Veriyi yükle
df = pd.read_excel("Veri.xlsx", sheet_name="Veri")

# Tarih sütununu düzenle
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)

# Genel bilgi
print("=== VERİ BOYUTU ===")
print(f"Satır: {len(df)}, Sütun: {len(df.columns)}")
print(f"Tarih Aralığı: {df['Tarih'].min().date()} → {df['Tarih'].max().date()}")
print(f"Toplam Hafta Sayısı: {len(df)}")

print("\n=== İLK 5 SATIR ===")
print(df.head())

print("\n=== TEMEL İSTATİSTİKLER (Milyon TL) ===")
desc = df[["Toplam", "TL", "YP"]].describe().round(2)
print(desc)

print("\n=== EKSİK DEĞER KONTROLÜ ===")
print(df.isnull().sum())

print("\n=== YP PAYI (%) ===")
df["YP_Payi"] = (df["YP"] / df["Toplam"] * 100).round(2)
print(df[["Tarih", "Toplam", "TL", "YP", "YP_Payi"]].to_string(index=False))