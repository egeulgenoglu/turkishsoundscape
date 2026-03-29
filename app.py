from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import base64
import math

app = Flask(__name__)

CLIENT_ID = "2348db0864b4498ea20b6015473770b5"
CLIENT_SECRET = "819a70f0160747a38818b21ca0f752e3"

def get_spotify_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return r.json()["access_token"]

print("CSV yukleniyor...")
df = pd.read_csv("ana_liste.csv", encoding="utf-8-sig")
df["Takipci"] = pd.to_numeric(df["Takipci"], errors="coerce").fillna(0).astype(int)
df["isim_lower"] = df["isim"].astype(str).str.lower()
df = df.sort_values("Takipci", ascending=False)
print(f"{len(df)} sanatci yuklendi!")

@app.route("/")
def index():
    genres = sorted(df["Genre"].dropna().unique().tolist())
    sehirler = sorted(df["sehir"].dropna().unique().tolist())
    tipler = sorted(df["tip"].dropna().unique().tolist())
    return render_template("index.html", genres=genres, sehirler=sehirler, tipler=tipler)

@app.route("/ara")
def ara():
    q = request.args.get("q", "").lower().strip()
    if len(q) < 2:
        return jsonify([])

    def eslesir(isim):
        parcalar = isim.lower().split()
        return any(p.startswith(q) for p in parcalar)

    eslesler = df[df["isim_lower"].apply(eslesir)].head(5)
    sonuclar = []
    for _, row in eslesler.iterrows():
        sonuclar.append({
            "isim": row["isim"],
            "genre": str(row.get("Genre", "")) if pd.notna(row.get("Genre")) else "",
            "sehir": str(row.get("sehir", "")) if pd.notna(row.get("sehir")) else "",
            "takipci": int(row["Takipci"]),
            "spotify_id": str(row.get("Spotify_ID", "")) if pd.notna(row.get("Spotify_ID")) else "",
            "foto": str(row.get("foto_url", "")) if pd.notna(row.get("foto_url")) else ""
        })
    return jsonify(sonuclar)

@app.route("/filtrele")
def filtrele():
    genre = request.args.get("genre", "").strip()
    sehir = request.args.get("sehir", "").strip()
    tip = request.args.get("tip", "").strip()
    sayfa = int(request.args.get("sayfa", 1))
    limit = 50

    sonuc = df.copy()
    if genre:
        sonuc = sonuc[sonuc["Genre"] == genre]
    if sehir:
        sonuc = sonuc[sonuc["sehir"].astype(str).str.contains(sehir, case=False, na=False)]
    if tip:
        sonuc = sonuc[sonuc["tip"] == tip]

    toplam = len(sonuc)
    toplam_sayfa = math.ceil(toplam / limit)
    sonuc = sonuc.iloc[(sayfa-1)*limit : sayfa*limit]

    sanatcilar = []
    for _, row in sonuc.iterrows():
        sanatcilar.append({
            "isim": row["isim"],
            "genre": str(row.get("Genre", "")) if pd.notna(row.get("Genre")) else "",
            "sehir": str(row.get("sehir", "")) if pd.notna(row.get("sehir")) else "",
            "takipci": int(row["Takipci"]),
            "spotify_id": str(row.get("Spotify_ID", "")) if pd.notna(row.get("Spotify_ID")) else "",
            "tip": str(row.get("tip", "")) if pd.notna(row.get("tip")) else "",
            "foto": str(row.get("foto_url", "")) if pd.notna(row.get("foto_url")) else ""
        })

    return jsonify({
        "sanatcilar": sanatcilar,
        "toplam": toplam,
        "toplam_sayfa": toplam_sayfa,
        "sayfa": sayfa
    })

@app.route("/sanatci/<spotify_id>")
def sanatci_detay(spotify_id):
    try:
        token = get_spotify_token()
        r = requests.get(
            f"https://api.spotify.com/v1/artists/{spotify_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return jsonify({
                "isim": data["name"],
                "takipci": data["followers"]["total"],
                "populerlik": data["popularity"],
                "turler": data.get("genres", []),
                "fotograf": data["images"][0]["url"] if data.get("images") else None,
                "spotify_url": data["external_urls"]["spotify"]
            })
    except Exception as e:
        pass
    return jsonify({"hata": "Veri alinamadi"})

if __name__ == "__main__":
    app.run(debug=True)