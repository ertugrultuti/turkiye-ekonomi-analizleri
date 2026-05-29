import pandas as pd 
df = pd.read_excel("Veri.xlsx", sheet_name="Veri", header=0)
df.columns = ["tarih", "endeks"]
df["tarih"] = pd.to_datetime(df["tarih"])
df = df.set_index("tarih")

print(df.shape)
print(df.head())
print(df.tail())
print(df.info())
print(df.describe().round(2))