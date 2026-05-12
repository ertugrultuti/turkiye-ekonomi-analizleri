import pandas as pd
import numpy as np

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"] = (df["YP"] / df["Toplam"] * 100).round(2)

# --- Periyotlar tanımla ---
periyotlar = {
    "2024 H2 (Haz-Ara)": ("2024-06-28", "2024-12-27"),
    "2025 H1 (Oca-Haz)": ("2025-01-03", "2025-06-27"),
    "2025 H2 (Tem-Ara)": ("2025-07-04", "2025-12-26"),
    "2026 YTD (Oca-Nis)": ("2026-01-02", "2026-04-10"),
}

print("=== PERİYOT BAZLI ANALİZ ===\n")
print(f"{'Periyot':<22} {'Başl. Toplam':>14} {'Bitiş Toplam':>14} {'Büyüme':>8} {'Başl. YP%':>10} {'Bitiş YP%':>10} {'TL Büy.':>8} {'YP Büy.':>8}")
print("-" * 100)

for isim, (bas_t, bit_t) in periyotlar.items():
    alt = df[(df["Tarih"] >= bas_t) & (df["Tarih"] <= bit_t)]
    if len(alt) < 2:
        continue
    ilk = alt.iloc[0]
    son = alt.iloc[-1]
    top_buy = (son["Toplam"] / ilk["Toplam"] - 1) * 100
    tl_buy  = (son["TL"]     / ilk["TL"]     - 1) * 100
    yp_buy  = (son["YP"]     / ilk["YP"]     - 1) * 100
    print(f"{isim:<22} {ilk['Toplam']:>14,.1f} {son['Toplam']:>14,.1f} {top_buy:>7.1f}% {ilk['YP_Payi']:>9.2f}% {son['YP_Payi']:>9.2f}% {tl_buy:>7.1f}% {yp_buy:>7.1f}%")

# --- Aylık bazda 3 aylık hareketli ortalama ---
df["Toplam_3haf_ort"] = df["Toplam"].rolling(3).mean()
df["TL_3haf_ort"]     = df["TL"].rolling(3).mean()
df["YP_3haf_ort"]     = df["YP"].rolling(3).mean()

# --- En yüksek / en düşük haftalık değişimler ---
df["Toplam_haf_deg"] = df["Toplam"].pct_change() * 100

print("\n\n=== EN YÜKSEK 5 HAFTALIK ARTIŞ (Toplam) ===")
top5_yukari = df.nlargest(5, "Toplam_haf_deg")[["Tarih", "Toplam", "Toplam_haf_deg"]]
print(top5_yukari.to_string(index=False))

print("\n=== EN YÜKSEK 5 HAFTALIK DÜŞÜŞ (Toplam) ===")
top5_asagi = df.nsmallest(5, "Toplam_haf_deg")[["Tarih", "Toplam", "Toplam_haf_deg"]]
print(top5_asagi.to_string(index=False))

# --- YP Payındaki kritik dönüşler ---
print("\n\n=== YP PAYI TARİHSEL SEYRİ (Aylık) ===")
df["Yil_Ay"] = df["Tarih"].dt.to_period("M")
aylik_yp = df.groupby("Yil_Ay").last().reset_index()[["Yil_Ay", "YP_Payi", "YP"]]
print(aylik_yp.to_string(index=False))

# --- Mutlak büyüme katkısı: TL vs YP ---
print("\n\n=== BÜYÜMEYE KATKI ANALİZİ (Mutlak, Milyon TL) ===")
print(f"{'Periyot':<22} {'TL Katkı':>12} {'YP Katkı':>12} {'TL Katkı%':>11} {'YP Katkı%':>11}")
print("-" * 70)
for isim, (bas_t, bit_t) in periyotlar.items():
    alt = df[(df["Tarih"] >= bas_t) & (df["Tarih"] <= bit_t)]
    if len(alt) < 2:
        continue
    ilk = alt.iloc[0]
    son = alt.iloc[-1]
    tl_katki  = son["TL"] - ilk["TL"]
    yp_katki  = son["YP"] - ilk["YP"]
    toplam_katki = tl_katki + yp_katki
    print(f"{isim:<22} {tl_katki:>12,.1f} {yp_katki:>12,.1f} {tl_katki/toplam_katki*100:>10.1f}% {yp_katki/toplam_katki*100:>10.1f}%")