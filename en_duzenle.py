import pandas as pd
import numpy as np
import re

df = pd.read_csv("en_sanatcilar2.csv", encoding="utf-8-sig")
print(f"Toplam: {len(df)} satir")

# Sehir temizleme - sadece ilk sehir ismini al
def sehir_temizle(val):
    if pd.isna(val) or str(val).strip() in ["", "nan"]:
        return np.nan
    val = str(val).strip()
    # Virgülle ayrılmışsa ilk parçayı al
    val = val.split(",")[0].strip()
    # | ile ayrılmışsa ilk parçayı al
    val = val.split("|")[0].strip()
    # "Turkey" veya "Türkiye" kelimesini kaldır
    val = re.sub(r"\bturkey\b", "", val, flags=re.IGNORECASE).strip()
    val = re.sub(r"\bturkiye\b", "", val, flags=re.IGNORECASE).strip()
    val = re.sub(r"\bturkey\b", "", val, flags=re.IGNORECASE).strip()
    # Sonunda kalan noktalama işaretlerini temizle
    val = val.strip(",./ ").strip()
    return val if val else np.nan

df["sehir"] = df["sehir"].apply(sehir_temizle)

# Cinsiyet - grup olanlara "grup" yaz
def cinsiyet_duzenle(row):
    tip = str(row.get("tip", "")).strip().lower()
    cinsiyet = row.get("cinsiyet", np.nan)
    
    if tip == "grup":
        return "grup"
    return cinsiyet

df["cinsiyet"] = df.apply(cinsiyet_duzenle, axis=1)

print(f"Sehir doluluk: {df['sehir'].notna().sum()}/{len(df)}")
print(f"Cinsiyet doluluk: {df['cinsiyet'].notna().sum()}/{len(df)}")
print("\nCinsiyet dagilimi:")
print(df["cinsiyet"].value_counts())

df.to_csv("en_sanatcilar2.csv", index=False, encoding="utf-8-sig")
print("\nen_sanatcilar2.csv guncellendi!")
