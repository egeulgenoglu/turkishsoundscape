import pandas as pd
import numpy as np

df = pd.read_csv("master_temiz.csv", encoding="utf-8-sig", low_memory=False)
print(f"Toplam: {len(df)} satir")

TURK_TURLER = [
    "turkish", "turkce", "turk ", "arabesk", "anadolu rock", "anatolian rock",
    "karadeniz", "bozlak", "ilahi", "oyun havasi", "baglama", "rumeli",
    "huzunlu sarkilar", "ulkucu sarkilar", "cocuk sarkilari", "cocuk masallari",
    "mevlevi sufi", "new school turkce", "classic turkish", "deep turkish",
    "turk sanat", "tulum", "darbuka", "neyin", "ney ", "kanun", "qanun",
    "turkce drill", "turkce kadin rap", "turkce remix", "turkce slow",
    "turkce trap", "turk sanat muzigi"
]

TURK_SEHIRLER = [
    "turkey", "istanbul", "ankara", "izmir", "bursa", "antalya",
    "adana", "konya", "trabzon", "eskisehir", "gaziantep", "kayseri",
    "samsun", "diyarbakir", "mersin", "urfa", "malatya", "erzurum",
    "van", "manisa", "balikesir", "denizli", "sakarya", "tekirdag",
    "hatay", "kocaeli", "gebze", "adapazari", "bolu", "afyon",
    "aydin", "canakkale", "edirne", "kirklareli", "kirikkale",
    "nevsehir", "nigde", "ordu", "rize", "sinop", "tokat", "zonguldak"
]

def turk_mu(row):
    tur_cols = ["Spotify_Tur", "EveryNoise_Tur", "Wikipedia_Tur", "muzik_turu (Wikidata)"]
    sehir_cols = ["dogum_yeri", "aktif_sehir", "arama_sehri"]

    for col in tur_cols:
        val = str(row.get(col, "")).lower()
        if val and val != "nan":
            if any(k in val for k in TURK_TURLER):
                return True

    for col in sehir_cols:
        val = str(row.get(col, "")).lower()
        if val and val != "nan":
            if any(s in val for s in TURK_SEHIRLER):
                return True

    return False

df["_turk"] = df.apply(turk_mu, axis=1)

turk = df[df["_turk"] == True].copy()
yabanci = df[df["_turk"] == False].copy()

print(f"Turk: {len(turk)}")
print(f"Turk olmayan: {len(yabanci)}")

# Turkler followers a gore sirali
turk = turk.sort_values("Followers", ascending=False, na_position="last")

# Yabanciler A dan Z ye
yabanci = yabanci.sort_values("isim", ascending=True, na_position="last")

# Birlestir
df_final = pd.concat([turk, yabanci], ignore_index=True)
df_final = df_final.drop(columns=["_turk"], errors="ignore")

df_final.to_csv("master_temiz.csv", index=False, encoding="utf-8-sig")
print(f"master_temiz.csv guncellendi: {len(df_final)} satir")
