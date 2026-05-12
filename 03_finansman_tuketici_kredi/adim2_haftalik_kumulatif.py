import pandas as pd
import numpy as np

df = pd.read_csv('veri.csv', sep=';', encoding='utf-8-sig')
df = df.dropna(subset=['Tarih'])
df = df[df['Tarih'].str.strip() != '']

numeric_cols = ['toplam_kredi', 'tuketici_kredileri_tl_yp', 'konut', 'tasit', 'ihtiyac']
for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
df = df.sort_values('Tarih').reset_index(drop=True)

# === HAFTALIK DEĞİŞİM (Mutlak, Milyon TL) ===
for col in numeric_cols:
    df[f'{col}_haftalik_degisim'] = df[col].diff()

# === HAFTALIK DEĞİŞİM (%) ===
for col in numeric_cols:
    df[f'{col}_haftalik_pct'] = df[col].pct_change() * 100

# === KÜMÜLATİF DEĞİŞİM (başlangıca göre %) ===
for col in numeric_cols:
    df[f'{col}_kumulatif_pct'] = (df[col] / df[col].iloc[0] - 1) * 100

# Başlangıç ve bitiş değerleri
print("=== BAŞLANGIÇ → BİTİŞ DEĞERLERİ (Milyon TL) ===")
for col in numeric_cols:
    baslangic = df[col].iloc[0]
    bitis = df[col].iloc[-1]
    degisim = bitis - baslangic
    pct = (bitis / baslangic - 1) * 100
    print(f"{col:35s}: {baslangic:>10,.1f} → {bitis:>10,.1f}  |  {degisim:>+10,.1f} Mn TL  |  %{pct:>+7.1f}")

# Haftalık değişim istatistikleri
print("\n=== HAFTALIK DEĞİŞİM İSTATİSTİKLERİ (Mutlak, Milyon TL) ===")
haftalik_cols = [f'{col}_haftalik_degisim' for col in numeric_cols]
print(df[haftalik_cols].describe().round(1).to_string())

print("\n=== HAFTALIK DEĞİŞİM İSTATİSTİKLERİ (%) ===")
haftalik_pct_cols = [f'{col}_haftalik_pct' for col in numeric_cols]
print(df[haftalik_pct_cols].describe().round(2).to_string())

# En yüksek ve en düşük haftalık değişimler (toplam_kredi için)
print("\n=== TOPLAM KREDİ: EN YÜKSEK 5 HAFTALIK ARTIŞ ===")
print(df[['Tarih', 'toplam_kredi', 'toplam_kredi_haftalik_degisim', 'toplam_kredi_haftalik_pct']]
      .nlargest(5, 'toplam_kredi_haftalik_degisim').to_string(index=False))

print("\n=== TOPLAM KREDİ: EN YÜKSEK 5 HAFTALIK DÜŞÜŞ ===")
print(df[['Tarih', 'toplam_kredi', 'toplam_kredi_haftalik_degisim', 'toplam_kredi_haftalik_pct']]
      .nsmallest(5, 'toplam_kredi_haftalik_degisim').to_string(index=False))