import pandas as pd
import requests
import time

def wikidata_sorgula(offset=0):
    url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?sanatci ?sanatciLabel ?dogumYeri ?dogumYeriLabel ?cinsiyet ?cinsiyetLabel ?muzikTuru ?muzikTuruLabel ?spotify WHERE {{
      ?sanatci wdt:P31 wd:Q5 .
      ?sanatci wdt:P27 wd:Q43 .
      ?sanatci wdt:P106 ?meslek .
      VALUES ?meslek {{
        wd:Q639669 wd:Q177220 wd:Q488205 wd:Q36834
        wd:Q855091 wd:Q183945 wd:Q386854 wd:Q2526255
      }}
      OPTIONAL {{ ?sanatci wdt:P19 ?dogumYeri . }}
      OPTIONAL {{ ?sanatci wdt:P21 ?cinsiyet . }}
      OPTIONAL {{ ?sanatci wdt:P136 ?muzikTuru . }}
      OPTIONAL {{ ?sanatci wdt:P1902 ?spotify . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "tr,en" . }}
    }}
    LIMIT 1000
    OFFSET {offset}
    """
    
    headers = {
        "User-Agent": "TurkishMusicArchive/1.0",
        "Accept": "application/json"
    }
    
    try:
        r = requests.get(url, params={"query": query, "format": "json"}, headers=headers, timeout=60)
        if r.status_code == 200:
            return r.json().get("results", {}).get("bindings", [])
        else:
            print(f"Hata: {r.status_code}")
            return []
    except Exception as e:
        print(f"Istek hatasi: {e}")
        return []

tum_sanatcilar = {}
offset = 0

while True:
    print(f"Sorgu: offset={offset}...")
    sonuclar = wikidata_sorgula(offset)
    
    if not sonuclar:
        print("Sonuc kalmadi, bitti.")
        break
    
    for s in sonuclar:
        wid = s.get("sanatci", {}).get("value", "").split("/")[-1]
        if not wid:
            continue
        
        if wid not in tum_sanatcilar:
            tum_sanatcilar[wid] = {
                "isim": s.get("sanatciLabel", {}).get("value", ""),
                "wikidata_id": wid,
                "dogum_yeri": s.get("dogumYeriLabel", {}).get("value", ""),
                "cinsiyet": s.get("cinsiyetLabel", {}).get("value", ""),
                "muzik_turu": s.get("muzikTuruLabel", {}).get("value", ""),
                "Spotify_ID": s.get("spotify", {}).get("value", "")
            }
        else:
            # Müzik türü birden fazla olabilir, virgülle ekle
            mevcut_tur = tum_sanatcilar[wid]["muzik_turu"]
            yeni_tur = s.get("muzikTuruLabel", {}).get("value", "")
            if yeni_tur and yeni_tur not in mevcut_tur:
                tum_sanatcilar[wid]["muzik_turu"] = mevcut_tur + ", " + yeni_tur if mevcut_tur else yeni_tur
    
    print(f"  {len(sonuclar)} sonuc geldi, toplam: {len(tum_sanatcilar)}")
    
    if len(sonuclar) < 1000:
        break
    
    offset += 1000
    time.sleep(2)

df = pd.DataFrame(list(tum_sanatcilar.values()))
df = df.sort_values("isim", ascending=True)
df.to_csv("wikidata_sanatcilar.csv", index=False, encoding="utf-8-sig")
print(f"\nTamamlandi! wikidata_sanatcilar.csv: {len(df)} sanatci")