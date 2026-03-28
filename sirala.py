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

df = pd.read_csv("spotify_ara_sonuc.csv", encoding="utf-8-sig")
print(f"Toplam: {len(df)} sanatci")

def eslesme_tipi(row):
    isim = normalize(str(row["isim"]))
    spotify_isim = normalize(str(row["Spotify_Isim"])) if pd.notna(row["Spotify_Isim"]) and row["Spotify_Isim"] != "" else ""
    spotify_id = str(row["Spotify_ID"]) if pd.notna(row["Spotify_ID"]) and row["Spotify_ID"] != "" else ""
    
    if not spotify_id:
        return 3  # ID yok
    
    if isim == spotify_isim:
        return 1  # Tam eslesme
    
    # Kısmi eşleşme - biri diğerini içeriyor mu
    if isim in spotify_isim or spotify_isim in isim:
        return 2
    
    # İlk kelime eşleşiyor mu
    isim_kelimeler = isim.split()
    spotify_kelimeler = spotify_isim.split()
    if isim_kelimeler and spotify_kelimeler:
        if isim_kelimeler[0] == spotify_kelimeler[0]:
            return 2
    
    return 3  # ID var ama isim uyuşmuyor, IDsiz gibi say

df["_tip"] = df.apply(eslesme_tipi, axis=1)
df["_norm_isim"] = df["isim"].apply(normalize)

df = df.sort_values(["_tip", "_norm_isim"], ascending=[True, True])
df = df.drop(columns=["_tip", "_norm_isim"])

df.to_csv("spotify_ara_sirali.csv", index=False, encoding="utf-8-sig")
print(f"Tamamlandi! spotify_ara_sirali.csv kaydedildi.")
print(f"\nTam eslesen: {len(df[df.apply(lambda r: normalize(str(r['isim'])) == normalize(str(r['Spotify_Isim'])) if pd.notna(r['Spotify_Isim']) else False, axis=1)])}")
print(f"Kismen eslesen: {len(df[df.apply(lambda r: pd.notna(r['Spotify_ID']) and r['Spotify_ID'] != '' and normalize(str(r['isim'])) != normalize(str(r['Spotify_Isim'] if pd.notna(r['Spotify_Isim']) else '')), axis=1)])}")
print(f"ID yok: {len(df[df['Spotify_ID'].isna() | (df['Spotify_ID'] == '')])}")