import pandas as pd
import numpy as np

df = pd.read_excel("Veri.xlsx")

# Sütun isimlerini kısalt (analiz kolaylığı için)
kisaltma = {
    "Tarih": "tarih",
    "Tüketici Güven Endeksi": "TGE",
    "Hanenin maddi durumu (12 ay öncesine göre mevcut dönemde)": "hane_mevcut",
    "Hanenin maddi durum beklentisi (gelecek 12 aylık dönemde)": "hane_beklenti",
    "Genel ekonomik durum (12 ay öncesine göre mevcut dönemde)": "ekonomi_mevcut",
    "Genel ekonomik durum beklentisi (gelecek 12 aylık dönemde)": "ekonomi_beklenti",
    "İşsizlerin sayısı beklentisi (gelecek 12 aylık dönemde)": "issizlik_beklenti",
    "Yarı_dayanıklı tüketim mallarına yönelik harcama yapma düşüncesi (geçen 3 aylık döneme göre gelecek 3 aylık dönemde)": "yari_dayanikli",
    "Mevcut dönemin dayanıklı tüketim malı satın almak için uygunluğu": "dayanikli_uygunluk",
    "Dayanıklı tüketim mallarına yönelik harcama yapma düşüncesi (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)": "dayanikli_beklenti",
    "Mevcut dönemin tasarruf etmek için uygunluğu": "tasarruf_uygunluk",
    "Hanenin içinde bulunduğu mali durumu": "hane_mali",
    "Tasarruf etme ihtimali (gelecek 12 aylık dönemde)": "tasarruf_ihtimal",
    "Tüketimin finansmanı amacıyla borç kullanma ihtimali (gelecek 3 aylık dönemde)": "borc_ihtimal",
    "Tüketici fiyatlarının değişimine ilişkin düşünce (geçen 12 aylık dönemde)": "fiyat_dusunce",
    "Tüketici fiyatlarının değişimine ilişkin beklenti (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)": "fiyat_beklenti",
    "Ücretlerin değişimine ilişkin beklenti (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)": "ucret_beklenti",
    "Otomobil satın alma ihtimali (gelecek 12 aylık dönemde)": "oto_ihtimal",
    "Konut tamiratına para harcama ihtimali (gelecek 12 aylık dönemde)": "konut_tamirat",
    "Konut satın alma veya inşa ettirme ihtimali (gelecek 12 aylık dönemde)": "konut_satin",
}
df.rename(columns=kisaltma, inplace=True)

# Tarih dönüşümü
df["tarih"] = pd.to_datetime(df["tarih"], format="%m/%Y")
df = df.sort_values("tarih").reset_index(drop=True)

print("=" * 60)
print("VERİ BOYUTU")
print(f"Satır: {df.shape[0]}, Sütun: {df.shape[1]}")

print("\n" + "=" * 60)
print("TARİH ARALIĞI")
print(f"Başlangıç : {df['tarih'].min().strftime('%B %Y')}")
print(f"Bitiş     : {df['tarih'].max().strftime('%B %Y')}")
print(f"Toplam ay : {df.shape[0]}")

print("\n" + "=" * 60)
print("EKSİK DEĞER KONTROLÜ")
eksik = df.isnull().sum()
print(eksik[eksik > 0] if eksik.sum() > 0 else "Eksik değer yok.")

print("\n" + "=" * 60)
print("TEMEL İSTATİSTİKLER")
print(df.drop(columns=["tarih"]).describe().round(2).to_string())

print("\n" + "=" * 60)
print("İLK 5 SATIR")
print(df[["tarih", "TGE", "hane_mevcut", "hane_beklenti",
          "ekonomi_mevcut", "ekonomi_beklenti"]].head().to_string())

print("\n" + "=" * 60)
print("SON 5 SATIR")
print(df[["tarih", "TGE", "hane_mevcut", "hane_beklenti",
          "ekonomi_mevcut", "ekonomi_beklenti"]].tail().to_string())