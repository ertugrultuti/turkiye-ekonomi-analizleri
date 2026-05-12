import pandas as pd
import numpy as np

df = pd.read_csv('veri.csv', sep=';', encoding='utf-8-sig')

# Boş satırları temizle
df = df.dropna(subset=['Tarih'])
df = df[df['Tarih'].str.strip() != '']

# Türkçe sayı formatını düzelt
numeric_cols = ['toplam_kredi', 'tuketici_kredileri_tl_yp', 'konut', 'tasit', 'ihtiyac']

for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Tarih formatını düzelt
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
df = df.sort_values('Tarih').reset_index(drop=True)

# Genel bilgi
print("=== VERİ GENEL BİLGİ ===")
print(f"Satır sayısı: {len(df)}")
print(f"Tarih aralığı: {df['Tarih'].min().date()} → {df['Tarih'].max().date()}")

print("\n=== İLK 5 SATIR ===")
print(df.head())

print("\n=== TEMEL İSTATİSTİKLER (Milyon TL) ===")
print(df[numeric_cols].describe().round(1))