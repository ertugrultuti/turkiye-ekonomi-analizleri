import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

df = pd.read_excel("Veri.xlsx", sheet_name="Veri")
df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
df = df.sort_values("Tarih").reset_index(drop=True)
df["YP_Payi"] = df["YP"] / df["Toplam"] * 100
df["Toplam_haf_deg"] = df["Toplam"].pct_change() * 100
df["TL_haf_deg"]     = df["TL"].pct_change() * 100
df["YP_haf_deg"]     = df["YP"].pct_change() * 100
df["Ay"]   = df["Tarih"].dt.month
df["Yil"]  = df["Tarih"].dt.year
df["AyAd"] = df["Tarih"].dt.strftime("%b")
AY_SIRALAMA = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
AY_TR = {"Jan":"Oca","Feb":"Şub","Mar":"Mar","Apr":"Nis","May":"May","Jun":"Haz",
          "Jul":"Tem","Aug":"Ağu","Sep":"Eyl","Oct":"Eki","Nov":"Kas","Dec":"Ara"}
df["AyTR"] = df["AyAd"].map(AY_TR)

# Ay bazında ortalama haftalık değişim
aylik_ort = df.groupby(["Ay","AyTR"])[["Toplam_haf_deg","TL_haf_deg","YP_haf_deg"]].mean().reset_index()
aylik_ort = aylik_ort.sort_values("Ay")

# Ay bazında ortalama YP payı
aylik_yp = df.groupby(["Ay","AyTR"])["YP_Payi"].mean().reset_index().sort_values("Ay")

# Çeyrek bazında ortalama haftalık değişim
df["Ceyrek"] = df["Tarih"].dt.quarter
ceyrek_ort = df.groupby("Ceyrek")[["Toplam_haf_deg","TL_haf_deg","YP_haf_deg"]].mean().reset_index()

# Yıl x Ay ısı haritası verisi (haftalık % değişim ortalaması)
pivot = df.pivot_table(index="Yil", columns="Ay", values="Toplam_haf_deg", aggfunc="mean")

print("=== AY BAZINDA ORT. HAFTALIK DEĞİŞİM (%) ===")
print(aylik_ort[["AyTR","Toplam_haf_deg","TL_haf_deg","YP_haf_deg"]].to_string(index=False))

print("\n=== ÇEYREK BAZINDA ORT. HAFTALIK DEĞİŞİM (%) ===")
print(ceyrek_ort.to_string(index=False))

print("\n=== YIL x AY ISITMA HARİTASI VERİSİ (Toplam Haf. Değ. %) ===")
print(pivot.round(2).to_string())

print("\n=== AY BAZINDA ORT. YP PAYI (%) ===")
print(aylik_yp[["AyTR","YP_Payi"]].to_string(index=False))

# Yıl sonu etkisi: Kasım-Aralık haftaları
kasaralik = df[df["Ay"].isin([11,12])][["Tarih","Toplam_haf_deg","TL_haf_deg","YP_haf_deg"]]
print("\n=== KASIM-ARALIK HAFTALIK DEĞİŞİMLER ===")
print(kasaralik.to_string(index=False))