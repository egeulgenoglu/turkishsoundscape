import pandas as pd
import re
import numpy as np

print("master.csv okunuyor...")
df = pd.read_csv("master.csv", encoding="utf-8-sig", low_memory=False)
print(f"Baslangic: {len(df)} satir, {len(df.columns)} sutun")

def normalize(isim):
    if not isinstance(isim, str):
        return ""
    isim = isim.lower().strip()
    isim = isim.replace("\u0131", "i").replace("\u00f6", "o").replace("\u00fc", "u")
    isim = isim.replace("\u015f", "s").replace("\u00e7", "c").replace("\u011f", "g")
    isim = re.sub(r"[^a-z0-9]", "", isim)
    return isim

df["_norm"] = df["isim"].apply(normalize)
df["baslangic_yili"] = np.nan

# isim bos olanlari sil
df = df[df["isim"].notna() & (df["isim"].astype(str).str.strip() != "")]
print(f"Isim bos olanlari sildikten sonra: {len(df)} satir")

# isim kucuk harf turkce karakter koru
def turkce_lower(s):
    if not isinstance(s, str):
        return s
    s = s.replace("I", "\u0131").replace("\u0130", "i")
    return s.lower().strip()

df["isim"] = df["isim"].apply(turkce_lower)

# Followers ve Popularity: | ile ayrilanlarda en buyugu al
def max_deger(val):
    if pd.isna(val):
        return np.nan
    val = str(val)
    parcalar = [v.strip() for v in val.split("|")]
    sayilar = []
    for p in parcalar:
        try:
            sayilar.append(float(p))
        except:
            pass
    if sayilar:
        return int(max(sayilar))
    return np.nan

df["Followers"] = df["Followers"].apply(max_deger)
df["Popularity"] = df["Popularity"].apply(max_deger)

# Tum degerleri birlestiren yardimci fonksiyon
def birlestir(*vals):
    tum = []
    gorulen = set()
    for val in vals:
        if pd.notna(val) and str(val).strip() not in ["", "nan"]:
            for t in str(val).split(","):
                t = t.strip()
                if t and t.lower() not in gorulen:
                    gorulen.add(t.lower())
                    tum.append(t)
    return ", ".join(tum) if tum else np.nan

# Spotify tur birlesimi
spotify_tur_cols = ["Spotify_Tur", "Genres", "Spotify"]
mevcut_spotify = [c for c in spotify_tur_cols if c in df.columns]
df["Spotify_Tur"] = df[mevcut_spotify].apply(lambda r: birlestir(*r), axis=1)

# EveryNoise tur birlesimi
en_cols = ["EveryNoise_Tur", "Every Noise at Once"]
mevcut_en = [c for c in en_cols if c in df.columns]
df["EveryNoise_Tur"] = df[mevcut_en].apply(lambda r: birlestir(*r), axis=1)

# Wikipedia birlesimi
wiki_cols = ["Wikipedia", "Wikipedia_Tur"]
mevcut_wiki = [c for c in wiki_cols if c in df.columns]
df["Wikipedia_Tur"] = df[mevcut_wiki].apply(lambda r: birlestir(*r), axis=1)

# Tip birlesimi
def tip_duzenle(val):
    if pd.isna(val) or str(val).strip() in ["", "nan"]:
        return np.nan
    val = str(val).lower()
    parcalar = re.split(r"[|,]", val)
    tipler = set()
    for p in parcalar:
        p = p.strip()
        if any(x in p for x in ["group", "grup"]):
            tipler.add("grup")
        elif any(x in p for x in ["solo", "person"]):
            tipler.add("solo")
    if "grup" in tipler:
        return "grup"
    elif "solo" in tipler:
        return "solo"
    return np.nan

tip_cols = [c for c in df.columns if "tip" in c.lower() or "type" in c.lower()]
if tip_cols:
    df["tip"] = df[tip_cols].apply(
        lambda r: tip_duzenle("|".join([str(v) for v in r if pd.notna(v) and str(v).strip() != "nan"])),
        axis=1
    )
else:
    df["tip"] = np.nan

# Dogum yeri
dogum_cols = [c for c in df.columns if "dogum" in c.lower()]
aktif_cols = [c for c in df.columns if "aktif" in c.lower()]
arama_cols = [c for c in df.columns if "arama" in c.lower()]

def ilk_dolu(*vals):
    for v in vals:
        if pd.notna(v) and str(v).strip() not in ["", "nan"]:
            return str(v).strip()
    return np.nan

df["dogum_yeri"] = df[dogum_cols].apply(lambda r: ilk_dolu(*r), axis=1) if dogum_cols else np.nan
df["aktif_sehir"] = df[aktif_cols].apply(lambda r: ilk_dolu(*r), axis=1) if aktif_cols else np.nan
df["arama_sehri"] = df[arama_cols].apply(lambda r: ilk_dolu(*r), axis=1) if arama_cols else np.nan

# Cinsiyet
cinsiyet_cols = [c for c in df.columns if "cinsiyet" in c.lower()]
df["cinsiyet"] = df[cinsiyet_cols].apply(lambda r: ilk_dolu(*r), axis=1) if cinsiyet_cols else np.nan

# Muzik turu (Wikidata)
muzik_cols = [c for c in df.columns if "muzik_turu" in c.lower()]
df["muzik_turu (Wikidata)"] = df[muzik_cols].apply(lambda r: ilk_dolu(*r), axis=1) if muzik_cols else np.nan

# Spotify isim
spotisim_cols = [c for c in df.columns if "spotify_isim" in c.lower()]
df["Spotify_Isim"] = df[spotisim_cols].apply(lambda r: ilk_dolu(*r), axis=1) if spotisim_cols else np.nan

# IDs
mb_id_cols = [c for c in df.columns if "musicbrainz" in c.lower() and "id" in c.lower()]
df["MusicBrainz_ID"] = df[mb_id_cols].apply(lambda r: ilk_dolu(*r), axis=1) if mb_id_cols else np.nan

wd_id_cols = [c for c in df.columns if "wikidata_id" in c.lower()]
df["wikidata_id"] = df[wd_id_cols].apply(lambda r: ilk_dolu(*r), axis=1) if wd_id_cols else np.nan

# Kaynak
kaynak_cols = [c for c in df.columns if "kaynak" in c.lower()]
df["kaynak"] = df[kaynak_cols].apply(lambda r: ilk_dolu(*r), axis=1) if kaynak_cols else np.nan

# Spotify ID tekrarlarini birlestir
print("Spotify ID tekrarlari birlestiriliyor...")

df_id = df[df["Spotify_ID"].notna() & (df["Spotify_ID"].astype(str).str.strip() != "nan")].copy()
df_noid = df[df["Spotify_ID"].isna() | (df["Spotify_ID"].astype(str).str.strip() == "nan")].copy()

print(f"Spotify ID li: {len(df_id)}, IDsiz: {len(df_noid)}")

def birlestir_satirlar(grup):
    if len(grup) == 1:
        return grup.iloc[0]
    sonuc = {}
    for col in grup.columns:
        degerler = grup[col].dropna().astype(str).str.strip()
        degerler = degerler[degerler.str.lower() != "nan"]
        if len(degerler) == 0:
            sonuc[col] = np.nan
        elif col in ["Followers", "Popularity"]:
            try:
                sayilar = [float(v) for v in degerler if v.replace(".","").isdigit()]
                sonuc[col] = int(max(sayilar)) if sayilar else np.nan
            except:
                sonuc[col] = np.nan
        else:
            benzersiz = list(dict.fromkeys(degerler.tolist()))
            sonuc[col] = benzersiz[0] if len(benzersiz) == 1 else ", ".join(benzersiz)
    return pd.Series(sonuc)

df_id_temiz = df_id.groupby("Spotify_ID", sort=False).apply(birlestir_satirlar).reset_index(drop=True)
print(f"ID tekrarlari birlestirildikten sonra: {len(df_id_temiz)} satir")

df_noid_temiz = df_noid.groupby("isim", sort=False).apply(birlestir_satirlar).reset_index(drop=True)
print(f"IDsiz isim tekrarlari birlestirildikten sonra: {len(df_noid_temiz)} satir")

# IDsiz ama ismi ID'li listede olanlari birlestir
df_id_isimler = set(df_id_temiz["isim"].dropna().str.strip().tolist())
df_noid_eslesen = df_noid_temiz[df_noid_temiz["isim"].isin(df_id_isimler)].copy()
df_noid_kalan = df_noid_temiz[~df_noid_temiz["isim"].isin(df_id_isimler)].copy()
print(f"IDsiz ama isim eslesen: {len(df_noid_eslesen)}, tamamen yeni: {len(df_noid_kalan)}")

if len(df_noid_eslesen) > 0:
    df_birlesmis = pd.concat([df_id_temiz, df_noid_eslesen], ignore_index=True)
    df_id_temiz = df_birlesmis.groupby("isim", sort=False).apply(birlestir_satirlar).reset_index(drop=True)
    print(f"Isim bazli birlestirmeden sonra: {len(df_id_temiz)} satir")

df = pd.concat([df_id_temiz, df_noid_kalan], ignore_index=True)
print(f"Toplam: {len(df)} satir")

# Son sutun secimi
final_cols = [
    "isim",
    "Spotify_ID",
    "Spotify_Isim",
    "Followers",
    "Popularity",
    "Spotify_Tur",
    "EveryNoise_Tur",
    "Wikipedia_Tur",
    "muzik_turu (Wikidata)",
    "cinsiyet",
    "tip",
    "dogum_yeri",
    "aktif_sehir",
    "arama_sehri",
    "baslangic_yili",
    "MusicBrainz_ID",
    "wikidata_id",
    "kaynak"
]

mevcut = [c for c in final_cols if c in df.columns]
df = df[mevcut]

df.to_csv("master_temiz.csv", index=False, encoding="utf-8-sig")
print(f"\nmaster_temiz.csv: {len(df)} satir, {len(df.columns)} sutun kaydedildi!")
print(f"Sutunlar: {df.columns.tolist()}")
