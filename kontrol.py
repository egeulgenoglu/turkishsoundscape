import pandas as pd

df = pd.read_csv("master.csv", encoding="utf-8-sig")
print(f"Toplam satir: {len(df)}")
print(f"Toplam sutun: {len(df.columns)}")
print(f"\nSutunlar: {df.columns.tolist()}")
print(f"\nIlk 3 satir:")
print(df.head(3).to_string())
print(f"\nBos deger istatistikleri:")
print(df.isnull().sum().to_string())