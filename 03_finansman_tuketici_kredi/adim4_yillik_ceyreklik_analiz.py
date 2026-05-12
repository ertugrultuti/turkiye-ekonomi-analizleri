import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

df = pd.read_csv('veri.csv', sep=';', encoding='utf-8-sig')
df = df.dropna(subset=['Tarih'])
df = df[df['Tarih'].str.strip() != '']

numeric_cols = ['toplam_kredi', 'tuketici_kredileri_tl_yp', 'konut', 'tasit', 'ihtiyac']
for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
df = df.sort_values('Tarih').reset_index(drop=True)

df['Yil'] = df['Tarih'].dt.year
df['Ay'] = df['Tarih'].dt.month
df['Ceyrek'] = df['Tarih'].dt.to_period('Q').astype(str)

# === ÇEYREK SONU DEĞERLERİ ===
ceyrek_sonu = df.groupby('Ceyrek').last().reset_index()
print("=== ÇEYREK SONU DEĞERLERİ (Milyon TL) ===")
print(ceyrek_sonu[['Ceyrek', 'Tarih'] + numeric_cols].to_string(index=False))

# === ÇEYREKLIK DEĞİŞİM ===
print("\n=== ÇEYREKLIK DEĞİŞİM (Milyon TL & %) ===")
for col in numeric_cols:
    ceyrek_sonu[f'{col}_degisim'] = ceyrek_sonu[col].diff()
    ceyrek_sonu[f'{col}_pct'] = ceyrek_sonu[col].pct_change() * 100

cols_degisim = ['Ceyrek'] + [f'{col}_pct' for col in numeric_cols]
print(ceyrek_sonu[cols_degisim].round(1).to_string(index=False))

# === YILLIK ORTALAMALAR ===
yillik = df.groupby('Yil')[numeric_cols].mean().round(1)
print("\n=== YILLIK ORTALAMALAR (Milyon TL) ===")
print(yillik.to_string())

# === YILLIK ORTALAMA DEĞİŞİM ===
print("\n=== YILLIK ORTALAMA DEĞİŞİM (%) ===")
print(yillik.pct_change().mul(100).round(1).to_string())

# === GRAFİK: Çeyreklik karşılaştırma (bar) ===
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Finansman Şirketleri - Çeyreklik Kredi Büyüklükleri\n(Milyon TL)',
             fontsize=14, fontweight='bold')

kolonlar = [
    ('toplam_kredi', 'Toplam Kredi', '#1f4e79'),
    ('tuketici_kredileri_tl_yp', 'Tüketici Kredileri', '#2e86c1'),
    ('tasit', 'Taşıt Kredileri', '#b7770d'),
    ('ihtiyac', 'İhtiyaç Kredileri', '#7b241c'),
]

for ax, (col, baslik, renk) in zip(axes.flatten(), kolonlar):
    bars = ax.bar(ceyrek_sonu['Ceyrek'], ceyrek_sonu[col] / 1000, color=renk, alpha=0.85, edgecolor='white')
    ax.set_title(baslik, fontweight='bold')
    ax.set_ylabel('Milyar TL')
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax.grid(True, alpha=0.3, axis='y')
    # Değer etiketleri
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + h * 0.01,
                f'{h:,.0f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

plt.tight_layout()
plt.savefig('ceyreklik_analiz.png', dpi=150, bbox_inches='tight')
plt.show()
print("Grafik kaydedildi: ceyreklik_analiz.png")