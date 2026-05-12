import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ── 1. VERİYİ YÜKLE ──────────────────────────────────────────────
df = pd.read_excel("Veri.xlsx")  # <-- kendi dosya adınla değiştir

# ── 2. VERİYİ HAZIRLA ────────────────────────────────────────────
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m')
df = df.set_index('Tarih')
df = df.asfreq('MS')

# Eksik değer kontrolü
print("=== EKSİK DEĞER KONTROLÜ ===")
print(df.isnull().sum())

print("\n=== TEMEL İSTATİSTİKLER ===")
print(df.describe())

print(f"\nBaşlangıç: {df.index.min().strftime('%Y-%m')}")
print(f"Bitiş    : {df.index.max().strftime('%Y-%m')}")
print(f"Gözlem   : {len(df)}")

# ── 3. TÜREMİŞ DEĞİŞKENLER ──────────────────────────────────────
df['Yillik_Enf'] = df['TUFE_Endeks'].pct_change(12) * 100
df['Aylik_Enf']  = df['TUFE_Endeks'].pct_change(1) * 100

# ── 4. GÖRSELLEŞTİR ─────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(13, 11))

# -- Grafik 1: Endeks seviyesi
axes[0].plot(df.index, df['TUFE_Endeks'], color='steelblue', linewidth=1.5)
axes[0].set_title('Türkiye TÜFE Endeksi (2005–2026)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Endeks Değeri')
axes[0].xaxis.set_major_locator(mdates.YearLocator(2))
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axes[0].grid(alpha=0.3)

# -- Grafik 2: Yıllık enflasyon (12 aylık değişim %)
axes[1].plot(df.index, df['Yillik_Enf'], color='crimson', linewidth=1.5)
axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
axes[1].set_title('Yıllık Enflasyon (12 Aylık % Değişim)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('% Değişim')
axes[1].xaxis.set_major_locator(mdates.YearLocator(2))
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axes[1].grid(alpha=0.3)

# -- Grafik 3: Aylık değişim %
axes[2].bar(df.index, df['Aylik_Enf'],
            color=['crimson' if x > 0 else 'steelblue' for x in df['Aylik_Enf'].fillna(0)],
            width=20)
axes[2].axhline(0, color='black', linewidth=0.8)
axes[2].set_title('Aylık Enflasyon (% Değişim)', fontsize=13, fontweight='bold')
axes[2].set_ylabel('% Değişim')
axes[2].xaxis.set_major_locator(mdates.YearLocator(2))
axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('tufe_genel_bakis.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== YILLIK ENF. ÖZET ===")
print(df['Yillik_Enf'].describe().round(2))