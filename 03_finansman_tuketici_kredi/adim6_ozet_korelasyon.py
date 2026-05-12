import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

df = pd.read_csv('veri.csv', sep=';', encoding='utf-8-sig')
df = df.dropna(subset=['Tarih'])
df = df[df['Tarih'].str.strip() != '']

numeric_cols = ['toplam_kredi', 'tuketici_kredileri_tl_yp', 'tasit', 'ihtiyac']
etiketler = {'toplam_kredi': 'Toplam Kredi', 'tuketici_kredileri_tl_yp': 'Tüketici',
             'tasit': 'Taşıt', 'ihtiyac': 'İhtiyaç'}

for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
df = df.sort_values('Tarih').reset_index(drop=True)

for col in numeric_cols:
    df[f'{col}_pct'] = df[col].pct_change() * 100

pct_cols = [f'{col}_pct' for col in numeric_cols]
pct_df = df[pct_cols].dropna()
pct_df.columns = [etiketler[c.replace('_pct', '')] for c in pct_cols]

# === KORELASYON MATRİSİ (seviye) ===
seviye_df = df[numeric_cols].copy()
seviye_df.columns = [etiketler[c] for c in numeric_cols]
print("=== KORELASYON MATRİSİ (Seviye) ===")
print(seviye_df.corr().round(3).to_string())

print("\n=== KORELASYON MATRİSİ (Haftalık Değişim %) ===")
print(pct_df.corr().round(3).to_string())

# === VOLATİLİTE KARŞILAŞTIRMASI ===
print("\n=== VOLATİLİTE (Haftalık Değişim % Standart Sapması) ===")
for col in numeric_cols:
    std = df[f'{col}_pct'].std()
    ort = df[f'{col}_pct'].mean()
    print(f"{etiketler[col]:20s}: Ort %{ort:.2f}  |  Std %{std:.2f}  |  CV={std/abs(ort):.1f}x")

# === GRAFİK: 2x2 panel ===
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Finansman Şirketleri - Korelasyon & Volatilite Analizi', fontsize=14, fontweight='bold')

# 1. Korelasyon ısı haritası (seviye)
ax1 = axes[0, 0]
corr_seviye = seviye_df.corr()
im = ax1.imshow(corr_seviye, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
ax1.set_xticks(range(len(corr_seviye)))
ax1.set_yticks(range(len(corr_seviye)))
ax1.set_xticklabels(corr_seviye.columns, rotation=30, ha='right')
ax1.set_yticklabels(corr_seviye.columns)
for i in range(len(corr_seviye)):
    for j in range(len(corr_seviye)):
        ax1.text(j, i, f'{corr_seviye.iloc[i, j]:.2f}', ha='center', va='center', fontsize=11, fontweight='bold')
ax1.set_title('Korelasyon Matrisi (Seviye)', fontweight='bold')
plt.colorbar(im, ax=ax1, shrink=0.8)

# 2. Korelasyon ısı haritası (haftalık değişim)
ax2 = axes[0, 1]
corr_pct = pct_df.corr()
im2 = ax2.imshow(corr_pct, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
ax2.set_xticks(range(len(corr_pct)))
ax2.set_yticks(range(len(corr_pct)))
ax2.set_xticklabels(corr_pct.columns, rotation=30, ha='right')
ax2.set_yticklabels(corr_pct.columns)
for i in range(len(corr_pct)):
    for j in range(len(corr_pct)):
        ax2.text(j, i, f'{corr_pct.iloc[i, j]:.2f}', ha='center', va='center', fontsize=11, fontweight='bold')
ax2.set_title('Korelasyon Matrisi (Haftalık Değişim %)', fontweight='bold')
plt.colorbar(im2, ax=ax2, shrink=0.8)

# 3. Volatilite (rolling std 8 hafta)
ax3 = axes[1, 0]
renkler = ['#1f4e79', '#2e86c1', '#b7770d', '#7b241c']
for col, renk in zip(numeric_cols, renkler):
    rolling_std = df[f'{col}_pct'].rolling(8).std()
    ax3.plot(df['Tarih'], rolling_std, color=renk, linewidth=2, label=etiketler[col])
ax3.set_title('8 Haftalık Hareketli Volatilite (Std %)', fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=30)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'%{x:.1f}'))

# 4. Scatter: Taşıt vs Tüketici (haftalık değişim)
ax4 = axes[1, 1]
ax4.scatter(pct_df['Taşıt'], pct_df['Tüketici'], alpha=0.6, color='#2e86c1', edgecolor='white', s=60)
z = np.polyfit(pct_df['Taşıt'].dropna(), pct_df['Tüketici'].dropna(), 1)
p = np.poly1d(z)
x_line = np.linspace(pct_df['Taşıt'].min(), pct_df['Taşıt'].max(), 100)
ax4.plot(x_line, p(x_line), color='red', linewidth=1.5, linestyle='--')
ax4.axhline(0, color='black', linewidth=0.5)
ax4.axvline(0, color='black', linewidth=0.5)
ax4.set_xlabel('Taşıt Haftalık Değişim %')
ax4.set_ylabel('Tüketici Haftalık Değişim %')
ax4.set_title('Taşıt vs Tüketici Kredileri (Haftalık %)', fontweight='bold')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('korelasyon_volatilite.png', dpi=150, bbox_inches='tight')
plt.show()
print("Grafik kaydedildi: korelasyon_volatilite.png")