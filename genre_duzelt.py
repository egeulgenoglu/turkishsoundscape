import pandas as pd
import numpy as np

df = pd.read_csv("en_sanatcilar2.csv", encoding="utf-8-sig")

EKSTRA_MAP = {
    "turkish trap pop": "Turkish Pop",
    "turkish alternative": "Turkish Rock",
}

def genre_guncelle(row):
    if pd.notna(row["Genre"]):
        return row["Genre"]
    en_tur = str(row["EveryNoise_Tur"]).lower().strip()
    return EKSTRA_MAP.get(en_tur, np.nan)

df["Genre"] = df.apply(genre_guncelle, axis=1)

print(f"Genre doluluk: {df['Genre'].notna().sum()}/{len(df)}")
print("\nHala bos kalanlar:")
bos = df[df["Genre"].isna()]
print(bos["EveryNoise_Tur"].value_counts().to_string())

df.to_csv("en_sanatcilar2.csv", index=False, encoding="utf-8-sig")
print("\nen_sanatcilar2.csv guncellendi!")
