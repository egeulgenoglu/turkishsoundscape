import pandas as pd
import requests
import time
import base64

CLIENT_ID = "2348db0864b4498ea20b6015473770b5"
CLIENT_SECRET = "819a70f0160747a38818b21ca0f752e3"

def normalize(metin):
    if not metin:
        return ""
    metin = str(metin).lower().strip()
    metin = metin.replace("i", "i")
    metin = metin.replace("o", "o")
    metin = metin.replace("u", "u")
    metin = metin.replace("s", "s")
    metin = metin.replace("c", "c")
    metin = metin.replace("g", "g")
    metin = metin.replace("a", "a")
    return metin

def normalize_tr(metin):
    if not metin:
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

def eslesme_skoru(isim1, isim2):
    n1 = normalize_tr(isim1)
    n2 = normalize_tr(isim2)
    if n1 == n2:
        return 100
    if n1 in n2 or n2 in n1:
        return 90
    return 0

def get_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return r.json()["access_token"]

def ara_sanatci(isim, token):
    url = "https://api.spotify.com/v1/search"
    params = {"q": isim, "type": "artist", "limit": 5}
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 401:
            return None, "token_expired"
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", 5))
            print(f"Rate limit! {wait} saniye bekleniyor...")
            time.sleep(wait)
            return None, "rate_limit"
        data = r.json()
        artists = data.get("artists", {}).get("items", [])
        for a in artists:
            skor = eslesme_skoru(isim, a["name"])
            if skor >= 90:
                genres = ", ".join(a.get("genres", []))
                return {
                    "Spotify_ID": a["id"],
                    "Spotify_Isim": a["name"],
                    "Followers": a["followers"]["total"],
                    "Popularity": a["popularity"],
                    "Genres": genres
                }, "ok"
        return None, "not_found"
    except Exception as e:
        print(f"Hata: {e}")
        return None, "error"

# Dosyaları oku
df = pd.read_csv("spotify_idsiz.csv", encoding="utf-8-sig")
print(f"Toplam aranacak: {len(df)} sanatci")

# Kaldığı yerden devam
mevcut = pd.DataFrame()
tamamlanan = set()
try:
    mevcut = pd.read_csv("spotify_ara_sonuc.csv", encoding="utf-8-sig")
    tamamlanan = set(mevcut["isim"].tolist())
    print(f"Daha once tamamlanan: {len(tamamlanan)}, kaldigi yerden devam...")
except Exception:
    pass

token = get_token()
token_sayac = 0
sonuclar = []
bulunan = 0
bulunamayan = 0

for i, row in df.iterrows():
    isim = row["isim"]
    if isim in tamamlanan:
        continue

    token_sayac += 1
    if token_sayac % 800 == 0:
        print("Token yenileniyor...")
        token = get_token()

    sonuc, durum = ara_sanatci(isim, token)

    if durum == "token_expired":
        token = get_token()
        sonuc, durum = ara_sanatci(isim, token)

    if durum == "rate_limit":
        sonuc, durum = ara_sanatci(isim, token)

    if sonuc:
        sonuclar.append({
            "isim": isim,
            "Spotify_ID": sonuc["Spotify_ID"],
            "Spotify_Isim": sonuc["Spotify_Isim"],
            "Followers": sonuc["Followers"],
            "Popularity": sonuc["Popularity"],
            "Genres": sonuc["Genres"]
        })
        bulunan += 1
    else:
        sonuclar.append({
            "isim": isim,
            "Spotify_ID": "",
            "Spotify_Isim": "",
            "Followers": "",
            "Popularity": "",
            "Genres": ""
        })
        bulunamayan += 1

    if len(sonuclar) % 100 == 0:
        df_ara = pd.DataFrame(sonuclar)
        if not mevcut.empty:
            df_ara = pd.concat([mevcut, df_ara], ignore_index=True)
        df_ara.to_csv("spotify_ara_sonuc.csv", index=False, encoding="utf-8-sig")
        son_100_bulunan = sum(1 for s in sonuclar[-100:] if s["Spotify_ID"] != "")
        son_100_bulunamayan = 100 - son_100_bulunan
        print(f"  {i+1}/{len(df)} | Son 100: {son_100_bulunan} bulundu, {son_100_bulunamayan} bulunamadi | Toplam: {bulunan} bulundu, {bulunamayan} bulunamadi")

    time.sleep(0.3)

# Son kayit
df_ara = pd.DataFrame(sonuclar)
if not mevcut.empty:
    df_ara = pd.concat([mevcut, df_ara], ignore_index=True)
df_ara.to_csv("spotify_ara_sonuc.csv", index=False, encoding="utf-8-sig")

print(f"\nTamamlandi!")
print(f"Bulunan: {bulunan}")
print(f"Bulunamayan: {bulunamayan}")