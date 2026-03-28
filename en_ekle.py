import pandas as pd
import numpy as np
import re

def normalize(isim):
    if not isinstance(isim, str):
        return ""
    isim = isim.lower().strip()
    isim = isim.replace("\u0131", "i").replace("\u00f6", "o").replace("\u00fc", "u")
    isim = isim.replace("\u015f", "s").replace("\u00e7", "c").replace("\u011f", "g")
    isim = re.sub(r"[^a-z0-9]", "", isim)
    return isim

print("Dosyalar okunuyor...")
en = pd.read_csv("en_sanatcilar2.csv", encoding="utf-8-sig")
master = pd.read_csv("master.csv", encoding="utf-8-sig", low_memory=False)

print(f"en_sanatcilar2: {len(en)} satir")
print(f"master: {len(master)} satir")

# Master'da tip sutunu bul
tip_cols = [c for c in master.columns if "tip" in c.lower() or "type" in c.lower()]
cinsiyet_cols = [c for c in master.columns if "cinsiyet" in c.lower()]
aktif_cols = [c for c in master.columns if "aktif" in c.lower()]
dogum_cols = [c for c in master.columns if "dogum" in c.lower()]

print(f"Tip sutunlari: {tip_cols}")
print(f"Cinsiyet sutunlari: {cinsiyet_cols}")

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

def ilk_dolu(*vals):
    for v in vals:
        if pd.notna(v) and str(v).strip() not in ["", "nan"]:
            return str(v).strip()
    return np.nan

# Master'dan gerekli bilgileri hazirla
master["_tip"] = master[tip_cols].apply(
    lambda r: tip_duzenle("|".join([str(v) for v in r if pd.notna(v) and str(v).strip() != "nan"])),
    axis=1
) if tip_cols else np.nan

master["_cinsiyet"] = master[cinsiyet_cols].apply(
    lambda r: ilk_dolu(*r), axis=1
) if cinsiyet_cols else np.nan

master["_sehir"] = master[aktif_cols + dogum_cols].apply(
    lambda r: ilk_dolu(*r), axis=1
) if (aktif_cols or dogum_cols) else np.nan

# Spotify ID ile eslestir
master_id = master[master["Spotify_ID"].notna()].drop_duplicates(subset=["Spotify_ID"])
master_id = master_id.set_index("Spotify_ID")

en["tip"] = en["Spotify_ID"].map(master_id["_tip"])
en["cinsiyet"] = en["Spotify_ID"].map(master_id["_cinsiyet"])
en["sehir"] = en["Spotify_ID"].map(master_id["_sehir"])

# Spotify ID eslesmeyen satirlar icin isim bazli eslestir
master["_norm"] = master["isim"].apply(normalize) if "isim" in master.columns else ""
en["_norm"] = en["isim"].apply(normalize)

master_norm = master[master["_norm"] != ""].drop_duplicates(subset=["_norm"]).set_index("_norm")

eksik = en["tip"].isna()
en.loc[eksik, "tip"] = en.loc[eksik, "_norm"].map(master_norm["_tip"])
en.loc[eksik, "cinsiyet"] = en.loc[eksik, "_norm"].map(master_norm["_cinsiyet"])
en.loc[eksik, "sehir"] = en.loc[eksik, "_norm"].map(master_norm["_sehir"])

en = en.drop(columns=["_norm"], errors="ignore")

print(f"\nTip doluluk: {en['tip'].notna().sum()}/{len(en)}")
print(f"Cinsiyet doluluk: {en['cinsiyet'].notna().sum()}/{len(en)}")
print(f"Sehir doluluk: {en['sehir'].notna().sum()}/{len(en)}")

en.to_csv("en_sanatcilar2.csv", index=False, encoding="utf-8-sig")
print("en_sanatcilar2.csv guncellendi!")