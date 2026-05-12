import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import rcParams

rcParams['font.family'] = 'DejaVu Sans'

df = pd.read_csv('veri.csv', sep=';', encoding='utf-8-sig')
df = df.dropna(subset=['Tarih'])
df = df[df['Tarih'].str.strip() != '']

numeric_cols = ['toplam_kredi', 'tuketici_kredileri_tl_yp', 'konut', 'tasit', 'ihtiyac']
for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
df = df.sort_values('Tarih').reset_index(drop=True)

for col in numeric_cols:
    df[f'{col}_kumulatif_pct'] = (df[col] / df[col].iloc[0] - 1) * 100
    df[f'{col}_haftalik_degisim'] = df[col].diff()

fig, axes = plt.subplots(3, 2, figsize=(16, 18))
fig.suptitle('Finansman Şirketleri - Seçilmiş Kredi Büyüklükleri Analizi\n(Milyon TL, Haziran 2024 - Mart 2026)',
             fontsize=15, fontweight='bold', y=0.98)

renkler = ['#1f4e79', '#2e86c1', '#117a65', '#b7770d', '#7b241c']

# 1. Toplam Kredi - Seviye
ax1 = axes[0, 0]
ax1.plot(df['Tarih'], df['toplam_kredi'] / 1000, color=renkler[0], linewidth=2.5)
ax1.fill_between(df['Tarih'], df['toplam_kredi'] / 1000, alpha=0.15, color=renkler[0])
ax1.set_title('Toplam Kredi (Milyar TL)', fontweight='bold')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=30)

# 2. Tüketici Kredileri - Seviye
ax2 = axes[0, 1]
ax2.plot(df['Tarih'], df['tuketici_kredileri_tl_yp'] / 1000, color=renkler[1], linewidth=2.5)
ax2.fill_between(df['Tarih'], df['tuketici_kredileri_tl_yp'] / 1000, alpha=0.15, color=renkler[1])
ax2.set_title('Tüketici Kredileri TL+YP (Milyar TL)', fontweight='bold')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=30)

# 3. Taşıt & İhtiyaç - Seviye (ikili)
ax3 = axes[1, 0]
ax3.plot(df['Tarih'], df['tasit'] / 1000, color=renkler[3], linewidth=2.5, label='Taşıt')
ax3.plot(df['Tarih'], df['ihtiyac'] / 1000, color=renkler[4], linewidth=2.5, label='İhtiyaç')
ax3.set_title('Taşıt & İhtiyaç Kredileri (Milyar TL)', fontweight='bold')
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.1f}'))
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=30)

# 4. Kümülatif Değişim (%)
ax4 = axes[1, 1]
etiketler = {'toplam_kredi': 'Toplam Kredi', 'tuketici_kredileri_tl_yp': 'Tüketici',
             'tasit': 'Taşıt', 'ihtiyac': 'İhtiyaç'}
for i, (col, etiket) in enumerate(etiketler.items()):
    ax4.plot(df['Tarih'], df[f'{col}_kumulatif_pct'], color=renkler[i], linewidth=2, label=etiket)
ax4.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax4.set_title('Kümülatif Değişim (%, Haziran 2024 = 0)', fontweight='bold')
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'%{x:+.0f}'))
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.tick_params(axis='x', rotation=30)

# 5. Toplam Kredi Haftalık Değişim (bar)
ax5 = axes[2, 0]
renkler_bar = ['#c0392b' if x < 0 else '#1a5276' for x in df['toplam_kredi_haftalik_degisim']]
ax5.bar(df['Tarih'], df['toplam_kredi_haftalik_degisim'] / 1000, color=renkler_bar, width=5)
ax5.axhline(0, color='black', linewidth=0.8)
ax5.set_title('Toplam Kredi - Haftalık Değişim (Milyar TL)', fontweight='bold')
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:+,.1f}'))
ax5.grid(True, alpha=0.3, axis='y')
ax5.tick_params(axis='x', rotation=30)

# 6. Taşıt & İhtiyaç Haftalık Değişim
ax6 = axes[2, 1]
ax6.plot(df['Tarih'], df['tasit_haftalik_degisim'], color=renkler[3], linewidth=1.5, label='Taşıt')
ax6.plot(df['Tarih'], df['ihtiyac_haftalik_degisim'], color=renkler[4], linewidth=1.5, label='İhtiyaç')
ax6.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax6.set_title('Taşıt & İhtiyaç - Haftalık Değişim (Milyon TL)', fontweight='bold')
ax6.legend()
ax6.grid(True, alpha=0.3)
ax6.tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig('kredi_analiz.png', dpi=150, bbox_inches='tight')
plt.show()
print("Grafik kaydedildi: kredi_analiz.png")