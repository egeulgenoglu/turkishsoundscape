import pandas as pd
import numpy as np

df = pd.read_csv("en_sanatcilar2.csv", encoding="utf-8-sig")
print(f"Toplam: {len(df)} satir")

TUR_MAP = {
    # Turkish Pop
    "classic turkish pop": "Turkish Pop",
    "deep turkish pop": "Turkish Pop",
    "turkce slow sarkilar": "Turkish Pop",
    "huzunlu sarkilar": "Turkish Pop",
    "karadeniz pop": "Turkish Pop",
    "turkce remix": "Turkish Pop",
    "turkish pop": "Turkish Pop",

    # Turkish Rock
    "anadolu rock": "Turkish Rock",
    "turkish alternative rock": "Turkish Rock",
    "turkish alt pop": "Turkish Rock",
    "turkish psych": "Turkish Rock",
    "turkish punk": "Turkish Rock",
    "turkish post-punk": "Turkish Rock",
    "turkish rock": "Turkish Rock",

    # Turkish Hip Hop & Trap
    "new school turkce rap": "Turkish Hip Hop & Trap",
    "turkish trap": "Turkish Hip Hop & Trap",
    "turkce drill": "Turkish Hip Hop & Trap",
    "turkce kadin rap": "Turkish Hip Hop & Trap",
    "turkce trap metal": "Turkish Hip Hop & Trap",
    "turkish hip hop": "Turkish Hip Hop & Trap",

    # Turkish Folk
    "baglama": "Turkish Folk",
    "karadeniz turkuleri": "Turkish Folk",
    "rumeli turkuleri": "Turkish Folk",
    "bozlak": "Turkish Folk",
    "oyun havasi": "Turkish Folk",
    "turkish folk": "Turkish Folk",

    # Turkish Sanat & Klasik
    "turk sanat muzigi": "Turkish Sanat & Klasik",
    "arabesk": "Turkish Sanat & Klasik",
    "turkish classical": "Turkish Sanat & Klasik",
    "turkish classical performance": "Turkish Sanat & Klasik",
    "ilahiler": "Turkish Sanat & Klasik",

    # Turkish Metal & Hardcore
    "turkish metal": "Turkish Metal & Hardcore",
    "turkish death metal": "Turkish Metal & Hardcore",
    "turkish black metal": "Turkish Metal & Hardcore",
    "turkish hardcore": "Turkish Metal & Hardcore",

    # Turkish Electronic
    "turkish electronic": "Turkish Electronic",
    "turkish edm": "Turkish Electronic",
    "turkish deep house": "Turkish Electronic",
    "turkish experimental": "Turkish Electronic",

    # Turkish Jazz & Instrumental
    "turkish jazz": "Turkish Jazz & Instrumental",
    "turkish modern jazz": "Turkish Jazz & Instrumental",
    "turkish instrumental": "Turkish Jazz & Instrumental",
    "turkish soundtrack": "Turkish Jazz & Instrumental",

    # Tematik & Ozel
    "cocuk sarkilari": "Tematik & Ozel",
    "ulkucu sarkilar": "Tematik & Ozel",

    # Diger
    "turkish reggae": "Diger",
    "turkish singer-songwriter": "Turkish Rock",
}

def genre_ata(en_tur):
    if pd.isna(en_tur) or str(en_tur).strip() in ["", "nan"]:
        return np.nan
    en_tur = str(en_tur).lower().strip()
    return TUR_MAP.get(en_tur, np.nan)

df["Genre"] = df["EveryNoise_Tur"].apply(genre_ata)

print(f"\nGenre doluluk: {df['Genre'].notna().sum()}/{len(df)}")
print("\nGenre dagilimi:")
print(df["Genre"].value_counts().to_string())

# Sutun sirasini duzenle
cols = df.columns.tolist()
cols.remove("Genre")
# Genre'yi EveryNoise_Tur'dan hemen once ekle
idx = cols.index("EveryNoise_Tur")
cols.insert(idx, "Genre")
df = df[cols]

df.to_csv("en_sanatcilar2.csv", index=False, encoding="utf-8-sig")
print("\nen_sanatcilar2.csv guncellendi!")
