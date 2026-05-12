import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

df = pd.read_excel('Veri.xlsx', sheet_name='Veri')
df['Toplam'] = df['Tarım'] + df['Sınai'] + df['Hizmetler']
df['Tarım_%'] = df['Tarım'] / df['Toplam'] * 100
df['Sınai_%'] = df['Sınai'] / df['Toplam'] * 100
df['Hizmetler_%'] = df['Hizmetler'] / df['Toplam'] * 100

fig, axes = plt.subplots(3, 1, figsize=(14, 18))
fig.suptitle("Türkiye'ye Yapılan Yatırımlar (Stok)\nSektörel Analiz — 2000–2024",
             fontsize=16, fontweight='bold', y=0.98)

renkler = {'Tarım': '#2ecc71', 'Sınai': '#3498db', 'Hizmetler': '#e74c3c'}
kriz_yillari = {2002: 'Ekonomik\nKriz', 2008: 'Finansal\nKriz', 2021: 'Pandemi\nSonrası'}

# ── GRAFIK 1: Toplam stok çizgi grafiği ──────────────────────────
ax1 = axes[0]
ax1.plot(df['Tarih'], df['Toplam'], color='#2c3e50', linewidth=2.5, marker='o',
         markersize=5, label='Toplam Stok')
ax1.fill_between(df['Tarih'], df['Toplam'], alpha=0.12, color='#2c3e50')

for yil, etiket in kriz_yillari.items():
    val = df.loc[df['Tarih'] == yil, 'Toplam'].values[0]
    ax1.axvline(x=yil, color='red', linestyle='--', alpha=0.4, linewidth=1)
    ax1.text(yil + 0.15, val * 1.04, etiket, fontsize=7.5, color='red', alpha=0.8)

ax1.set_title('Toplam Yatırım Stoku (Milyon USD)', fontsize=12, fontweight='bold', pad=10)
ax1.set_ylabel('Milyon USD')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
ax1.set_xticks(df['Tarih'])
ax1.set_xticklabels(df['Tarih'], rotation=45, fontsize=8)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
ax1.legend(fontsize=9)

# ── GRAFIK 2: Sektörlere göre yığılmış alan grafiği (mutlak) ─────
ax2 = axes[1]
ax2.stackplot(df['Tarih'],
              df['Tarım'], df['Sınai'], df['Hizmetler'],
              labels=['Tarım', 'Sınai', 'Hizmetler'],
              colors=[renkler['Tarım'], renkler['Sınai'], renkler['Hizmetler']],
              alpha=0.85)

for yil in kriz_yillari:
    ax2.axvline(x=yil, color='red', linestyle='--', alpha=0.4, linewidth=1)

ax2.set_title('Sektörel Yatırım Stoku — Mutlak Değer (Milyon USD)', fontsize=12, fontweight='bold', pad=10)
ax2.set_ylabel('Milyon USD')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
ax2.set_xticks(df['Tarih'])
ax2.set_xticklabels(df['Tarih'], rotation=45, fontsize=8)
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.legend(loc='upper left', fontsize=9)

# ── GRAFIK 3: Sektör payları — yüzde alan grafiği ────────────────
ax3 = axes[2]
ax3.stackplot(df['Tarih'],
              df['Tarım_%'], df['Sınai_%'], df['Hizmetler_%'],
              labels=['Tarım', 'Sınai', 'Hizmetler'],
              colors=[renkler['Tarım'], renkler['Sınai'], renkler['Hizmetler']],
              alpha=0.85)

for yil in kriz_yillari:
    ax3.axvline(x=yil, color='red', linestyle='--', alpha=0.4, linewidth=1)

ax3.set_title('Sektörel Pay Dağılımı (%)', fontsize=12, fontweight='bold', pad=10)
ax3.set_ylabel('Pay (%)')
ax3.set_ylim(0, 100)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'%{x:.0f}'))
ax3.set_xticks(df['Tarih'])
ax3.set_xticklabels(df['Tarih'], rotation=45, fontsize=8)
ax3.grid(axis='y', linestyle='--', alpha=0.4)
ax3.legend(loc='upper left', fontsize=9)

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('yatirim_analizi.png', dpi=150, bbox_inches='tight')
plt.show()
print("Grafik kaydedildi: yatirim_analizi.png")