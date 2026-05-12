import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats

df = pd.read_csv('veri.csv', sep=';', encoding='utf-8-sig')
df = df.dropna(subset=['Tarih'])
df = df[df['Tarih'].str.strip() != '']

numeric_cols = ['toplam_kredi', 'tuketici_kredileri_tl_yp', 'tasit', 'ihtiyac']
for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
df = df.sort_values('Tarih').reset_index(drop=True)

# 4 haftalık hareketli ortalama büyüme hızı
for col in numeric_cols:
    df[f'{col}_pct'] = df[col].pct_change() * 100
    df[f'{col}_ma4'] = df[col].rolling(4).mean()
    df[f'{col}_buyume_ma4'] = df[f'{col}_pct'].rolling(4).mean()

# Trend (lineer regresyon) - log ölçeğinde
t = np.arange(len(df))
print("=== LİNEER TREND (Haftalık Ortalama Büyüme Hızı, %) ===")
for col in numeric_cols:
    log_vals = np.log(df[col].dropna())
    t_clean = t[:len(log_vals)]
    slope, intercept, r, p, se = stats.linregress(t_clean, log_vals)
    haftalik_buyume = (np.exp(slope) - 1) * 100
    print(f"{col:35s}: Haftalık %{haftalik_buyume:+.2f}  |  Yıllık ~%{((1+haftalik_buyume/100)**52-1)*100:.1f}  |  R²={r**2:.3f}")

# Dönem karşılaştırması: 2024H2 vs 2025H1 vs 2025H2
print("\n=== DÖNEM ORTALAMALARI KARŞILAŞTIRMASI (Milyon TL) ===")
donemler = {
    '2024 H2 (Haz-Ara)': (df['Tarih'] >= '2024-06-01') & (df['Tarih'] < '2025-01-01'),
    '2025 H1 (Oca-Haz)': (df['Tarih'] >= '2025-01-01') & (df['Tarih'] < '2025-07-01'),
    '2025 H2 (Tem-Ara)': (df['Tarih'] >= '2025-07-01') & (df['Tarih'] < '2026-01-01'),
    '2026 Q1 (Oca-Mar)': (df['Tarih'] >= '2026-01-01'),
}
donем_df = pd.DataFrame({k: df.loc[v, numeric_cols].mean() for k, v in donemler.items()}).T.round(1)
print(donем_df.to_string())

print("\n=== DÖNEM BÜYÜME HIZLARI (%) ===")
print(donем_df.pct_change().mul(100).round(1).to_string())

# === GRAFİK: Büyüme hızı (4 haftalık MA) ===
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Finansman Şirketleri - 4 Haftalık Hareketli Ortalama Büyüme Hızı (%)',
             fontsize=14, fontweight='bold')

basliklar = ['Toplam Kredi', 'Tüketici Kredileri', 'Taşıt Kredileri', 'İhtiyaç Kredileri']
renkler = ['#1f4e79', '#2e86c1', '#b7770d', '#7b241c']

for ax, col, baslik, renk in zip(axes.flatten(), numeric_cols, basliklar, renkler):
    ax.plot(df['Tarih'], df[f'{col}_buyume_ma4'], color=renk, linewidth=2.5)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.fill_between(df['Tarih'], df[f'{col}_buyume_ma4'], 0,
                    where=df[f'{col}_buyume_ma4'] >= 0, alpha=0.2, color=renk)
    ax.fill_between(df['Tarih'], df[f'{col}_buyume_ma4'], 0,
                    where=df[f'{col}_buyume_ma4'] < 0, alpha=0.2, color='red')
    ax.set_title(baslik, fontweight='bold')
    ax.set_ylabel('Haftalık Büyüme % (4H MA)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'%{x:.1f}'))
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig('buyume_trend.png', dpi=150, bbox_inches='tight')
plt.show()
print("Grafik kaydedildi: buyume_trend.png")