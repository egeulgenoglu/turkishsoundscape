import pandas as pd

def normalize(metin):
    if pd.isna(metin) or metin == "":
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

# Dosyaları oku
sirali = pd.read_csv("spotify_ara_sirali.csv", encoding="utf-8-sig")
turkish = pd.read_csv("TURKISH_MUSIC_FINAL_ID_DATABASE.csv", encoding="utf-8-sig")
rym = pd.read_csv("rym_nufus_kayit_final_v4.csv", encoding="utf-8-sig")

print(f"Sirali: {len(sirali)} sanatci")
print(f"Turkish Music: {len(turkish)} sanatci")
print(f"RYM: {len(rym)} sanatci")

# Turkish Music'i normalize et
turkish["_norm"] = turkish["Sanatçı"].apply(normalize)
turkish_dict = {row["_norm"]: row for _, row in turkish.iterrows()}

# RYM şehir bilgisini normalize et
rym["_norm"] = rym["isim"].apply(normalize)
rym_dict = {row["_norm"]: row for _, row in rym.iterrows()}

# Sirali listedeki her sanatçıyı işle
sonuclar = []

for _, row in sirali.iterrows():
    isim = row["isim"]
    norm = normalize(isim)
    spotify_id = str(row["Spotify_ID"]) if pd.notna(row["Spotify_ID"]) and str(row["Spotify_ID"]).strip() != "" else ""
    spotify_isim = str(row["Spotify_Isim"]) if pd.notna(row.get("Spotify_Isim", "")) and str(row.get("Spotify_Isim", "")).strip() != "" else ""
    
    yeni = {"isim": isim}
    
    # Şehir bilgisini RYM'den al
    if norm in rym_dict:
        yeni["dogum_yeri"] = rym_dict[norm]["dogum_yeri"]
        yeni["aktif_sehir"] = rym_dict[norm]["aktif_sehir"]
        yeni["arama_sehri"] = rym_dict[norm]["arama_sehri"]
        yeni["tip"] = rym_dict[norm]["tip"]
    else:
        yeni["dogum_yeri"] = ""
        yeni["aktif_sehir"] = ""
        yeni["arama_sehri"] = ""
        yeni["tip"] = ""

    # Spotify bilgilerini ekle
    yeni["Spotify_ID"] = spotify_id
    yeni["Spotify_Isim"] = spotify_isim
    yeni["Followers"] = row.get("Followers", "")
    yeni["Popularity"] = row.get("Popularity", "")
    yeni["Genres"] = row.get("Genres", "")

    # Turkish Music'ten tür bilgilerini ekle
    if norm in turkish_dict:
        t = turkish_dict[norm]
        yeni["Spotify_Tur"] = t.get("Spotify", "")
        yeni["Wikipedia_Tur"] = t.get("Wikipedia", "")
        yeni["EveryNoise_Tur"] = t.get("Every Noise at Once", "")
    else:
        yeni["Spotify_Tur"] = ""
        yeni["Wikipedia_Tur"] = ""
        yeni["EveryNoise_Tur"] = ""

    # Eşleşme tipi belirle
    if spotify_id:
        if normalize(isim) == normalize(spotify_isim):
            yeni["_tip"] = 1  # ID var, isim tam eşleşiyor
        else:
            yeni["_tip"] = 2  # ID var, isim eşleşmiyor
    elif yeni["Spotify_Tur"] or yeni["Wikipedia_Tur"] or yeni["EveryNoise_Tur"]:
        yeni["_tip"] = 3  # ID yok ama tür bilgisi var
    else:
        yeni["_tip"] = 4  # Hiçbir şey yok

    sonuclar.append(yeni)

# Turkish Music'te olup sirali'de olmayanları da ekle
sirali_normlar = set(sirali["isim"].apply(normalize).tolist())
for _, row in turkish.iterrows():
    norm = row["_norm"]
    if norm not in sirali_normlar:
        spotify_id = str(row["Spotify_ID"]) if pd.notna(row["Spotify_ID"]) else ""
        yeni = {
            "isim": row["Sanatçı"],
            "dogum_yeri": "",
            "aktif_sehir": "",
            "arama_sehri": "",
            "tip": "",
            "Spotify_ID": spotify_id,
            "Spotify_Isim": row["Sanatçı"],
            "Followers": row.get("Followers", ""),
            "Popularity": row.get("Popularity", ""),
            "Genres": row.get("Genres", ""),
            "Spotify_Tur": row.get("Spotify", ""),
            "Wikipedia_Tur": row.get("Wikipedia", ""),
            "EveryNoise_Tur": row.get("Every Noise at Once", ""),
            "_tip": 1 if spotify_id else 3
        }
        sonuclar.append(yeni)

df = pd.DataFrame(sonuclar)

print(f"\nTip 1 (ID var, isim eslesıyor): {len(df[df['_tip']==1])}")
print(f"Tip 2 (ID var, isim eslesmiyor): {len(df[df['_tip']==2])}")
print(f"Tip 3 (ID yok, tur bilgisi var): {len(df[df['_tip']==3])}")
print(f"Tip 4 (Hicbir sey yok): {len(df[df['_tip']==4])}")

# Sırala
df["_norm_isim"] = df["isim"].apply(normalize)
df["_followers"] = pd.to_numeric(df["Followers"], errors="coerce").fillna(0)

df_tip1 = df[df["_tip"]==1].sort_values("_followers", ascending=False)
df_tip2 = df[df["_tip"]==2].sort_values("_followers", ascending=False)
df_tip3 = df[df["_tip"]==3].sort_values("_norm_isim", ascending=True)
df_tip4 = df[df["_tip"]==4].sort_values("_norm_isim", ascending=True)

df_final = pd.concat([df_tip1, df_tip2, df_tip3, df_tip4], ignore_index=True)
df_final = df_final.drop(columns=["_tip", "_norm_isim", "_followers"])

df_final.to_csv("turkiye_muzik_final.csv", index=False, encoding="utf-8-sig")
print(f"\nTamamlandi! turkiye_muzik_final.csv kaydedildi.")
print(f"Toplam: {len(df_final)} sanatci")