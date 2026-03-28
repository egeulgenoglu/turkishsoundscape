import pandas as pd

def normalize(metin):
    if pd.isna(metin):
        return ""
    metin = str(metin).lower().strip()
    metin = metin.replace("ı", "i")
    metin = metin.replace("ö", "o")
    metin = metin.replace("ü", "u")
    metin = metin.replace("ş", "s")
    metin = metin.replace("ç", "c")
    metin = metin.replace("ğ", "g")
    metin = metin.replace("â", "a")
    metin = metin.replace("î", "i")
    metin = metin.replace("û", "u")
    return metin

rym = pd.read_csv("rym_nufus_kayit_final_v4.csv", encoding="utf-8-sig")
spotify = pd.read_csv("TURKISH_MUSIC_FINAL_ID_DATABASE.csv", encoding="utf-8-sig")

print(f"RYM: {len(rym)} sanatci")
print(f"Spotify: {len(spotify)} sanatci")

rym["_norm"] = rym["isim"].apply(normalize)
spotify["_norm"] = spotify["Sanatçı"].apply(normalize)

spotify_dict = {}
for _, row in spotify.iterrows():
    spotify_dict[row["_norm"]] = row

# Eşleştir
eslesen = []
eslesmeyenler_rym = []

for _, row in rym.iterrows():
    norm = row["_norm"]
    if norm in spotify_dict:
        sp = spotify_dict[norm]
        yeni = row.to_dict()
        yeni["Spotify_ID"] = sp["Spotify_ID"]
        yeni["Followers"] = sp["Followers"]
        yeni["Popularity"] = sp["Popularity"]
        yeni["Genres"] = sp["Genres"]
        yeni["Spotify_Tur"] = sp["Spotify"]
        yeni["Wikipedia_Tur"] = sp["Wikipedia"]
        yeni["EveryNoise_Tur"] = sp["Every Noise at Once"]
        eslesen.append(yeni)
    else:
        eslesmeyenler_rym.append(row.to_dict())

# Spotify'da olup RYM'de olmayanlar
rym_normlar = set(rym["_norm"].tolist())
eslesmeyenler_spotify = []
for _, row in spotify.iterrows():
    if row["_norm"] not in rym_normlar:
        eslesmeyenler_spotify.append(row.to_dict())

df_eslesen = pd.DataFrame(eslesen).drop(columns=["_norm"])
df_idsiz_rym = pd.DataFrame(eslesmeyenler_rym).drop(columns=["_norm"])
df_idsiz_spotify = pd.DataFrame(eslesmeyenler_spotify).drop(columns=["_norm"])

# Spotify IDsi boş olanları da IDsiz'e taşı
df_eslesen_dolu = df_eslesen[df_eslesen["Spotify_ID"].notna() & (df_eslesen["Spotify_ID"] != "")]
df_eslesen_bos = df_eslesen[df_eslesen["Spotify_ID"].isna() | (df_eslesen["Spotify_ID"] == "")]

print(f"\nSpotify IDli (dolu): {len(df_eslesen_dolu)} sanatci")
print(f"Spotify IDsi bos eslesenler: {len(df_eslesen_bos)} sanatci")

# IDsiz listesi: RYM'de eslesmeyen + Spotify'da eslesmeyen + IDsi bos eslesenler
idsiz_isimler = pd.concat([
    df_idsiz_rym[["isim"]],
    df_idsiz_spotify[["Sanatçı"]].rename(columns={"Sanatçı": "isim"}),
    df_eslesen_bos[["isim"]]
], ignore_index=True)
idsiz_isimler = idsiz_isimler.drop_duplicates(subset=["isim"], keep="first")

print(f"Toplam IDsiz: {len(idsiz_isimler)} sanatci")

df_eslesen_dolu.to_csv("spotify_idli.csv", index=False, encoding="utf-8-sig")
idsiz_isimler.to_csv("spotify_idsiz.csv", index=False, encoding="utf-8-sig")

print(f"\nTamamlandi!")
print(f"spotify_idli.csv: {len(df_eslesen_dolu)} sanatci")
print(f"spotify_idsiz.csv: {len(idsiz_isimler)} sanatci")