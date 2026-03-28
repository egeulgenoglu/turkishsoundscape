import pandas as pd
import re

def normalize(isim):
    if not isinstance(isim, str):
        return ""
    isim = isim.lower().strip()
    isim = isim.replace("i", "i").replace("o", "o").replace("u", "u")
    isim = isim.replace("s", "s").replace("c", "c").replace("g", "g")
    isim = re.sub(r"[^a-z0-9]", "", isim)
    return isim

print("Dosyalar okunuyor...")
tmf = pd.read_csv("turkiye_muzik_final.csv", encoding="utf-8-sig")
enf = pd.read_csv("every_noise_final.csv", encoding="utf-8-sig")
rym = pd.read_csv("rym_nufus_kayit_final_v4.csv", encoding="utf-8-sig")
mb = pd.read_excel("MusicBrainz_Tum_Turk_Sanatcilari.xlsx")
wd = pd.read_csv("wikidata_sanatcilar.csv", encoding="utf-8-sig")
tmid = pd.read_csv("TURKISH_MUSIC_FINAL_ID_DATABASE.csv", encoding="utf-8-sig")

tmf = tmf.rename(columns={
    "dogum_yeri": "dogum_yeri (RYM)",
    "aktif_sehir": "aktif_sehir (RYM)",
    "arama_sehri": "arama_sehri (RYM)",
    "tip": "tip (RYM)",
    "Spotify_Isim": "Spotify_Isim (Spotify)",
    "Genres": "Genres (Spotify)",
    "Spotify_Tur": "Spotify_Tur (Spotify)",
    "Wikipedia_Tur": "Wikipedia_Tur (Wikipedia)",
    "EveryNoise_Tur": "EveryNoise_Tur (TMF)"
})

enf = enf.rename(columns={
    "Spotify_Tur": "Spotify_Tur (EveryNoise)",
    "EveryNoise_Tur": "EveryNoise_Tur (EveryNoise)"
})

rym = rym.rename(columns={
    "dogum_yeri": "dogum_yeri (RYM)",
    "aktif_sehir": "aktif_sehir (RYM)",
    "tip": "tip (RYM)",
    "arama_sehri": "arama_sehri (RYM)"
})

mb = mb.rename(columns={
    "Sanatci": "isim",
    "MusicBrainz ID": "MusicBrainz_ID",
    "Tur (Type)": "tip (MusicBrainz)",
    "Sehir/Bolge": "sehir (MusicBrainz)",
    "Baslangic Yili": "baslangic_yili (MusicBrainz)"
})

wd = wd.rename(columns={
    "dogum_yeri": "dogum_yeri (Wikidata)",
    "cinsiyet": "cinsiyet (Wikidata)",
    "muzik_turu": "muzik_turu (Wikidata)"
})

tmid = tmid.rename(columns={
    "Sanatci": "isim",
    "Genres": "Genres (TMID)",
    "Spotify": "Spotify_Tur (TMID)",
    "Wikipedia": "Wikipedia_Tur (TMID)",
    "Every Noise at Once": "EveryNoise_Tur (TMID)"
})

for df in [tmf, enf, rym, mb, wd, tmid]:
    df["_norm"] = df["isim"].apply(normalize)

enf_id = enf.set_index("Spotify_ID")
wd_id = wd.set_index("Spotify_ID")
tmid_id = tmid.set_index("Spotify_ID")
rym_norm = rym.set_index("_norm")
mb_norm = mb.set_index("_norm")

ana = tmf.copy()

for col in ["Spotify_Tur (EveryNoise)", "EveryNoise_Tur (EveryNoise)"]:
    if col in enf_id.columns:
        ana[col] = ana["Spotify_ID"].map(enf_id[col])

for col in ["dogum_yeri (Wikidata)", "cinsiyet (Wikidata)", "muzik_turu (Wikidata)", "wikidata_id"]:
    if col in wd_id.columns:
        ana[col] = ana["Spotify_ID"].map(wd_id[col])

for col in ["Genres (TMID)", "Spotify_Tur (TMID)", "Wikipedia_Tur (TMID)", "EveryNoise_Tur (TMID)"]:
    if col in tmid_id.columns:
        ana[col] = ana["Spotify_ID"].map(tmid_id[col])

for col in ["MusicBrainz_ID", "tip (MusicBrainz)", "sehir (MusicBrainz)", "baslangic_yili (MusicBrainz)"]:
    if col in mb_norm.columns:
        ana[col] = ana["_norm"].map(mb_norm[col])

mevcut_idler = set(ana["Spotify_ID"].dropna().tolist())
enf_yeni = enf[~enf["Spotify_ID"].isin(mevcut_idler)].copy()
if len(enf_yeni) > 0:
    print(f"EveryNoise'dan {len(enf_yeni)} yeni sanatci ekleniyor...")
    ana = pd.concat([ana, enf_yeni], ignore_index=True)

mevcut_idler = set(ana["Spotify_ID"].dropna().tolist())
wd_yeni = wd[~w