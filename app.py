from flask import Flask, render_template, request, jsonify
import pandas as pd
import math

app = Flask(__name__)

print("CSV yukleniyor...")
df = pd.read_csv("en_sanatcilar2.csv", encoding="utf-8-sig")
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
    eslesler = df[df["isim_lower"].str.contains(q, na=False)].head(5)
    sonuclar = []
    for _, row in eslesler.iterrows():
        sonuclar.append({
            "isim": row["isim"],
            "genre": str(row.get("Genre", "")) if pd.notna(row.get("Genre")) else "",
            "sehir": str(row.get("sehir", "")) if pd.notna(row.get("sehir")) else "",
            "takipci": int(row["Takipci"]),
            "spotify_id": str(row.get("Spotify_ID", "")) if pd.notna(row.get("Spotify_ID")) else ""
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
            "tip": str(row.get("tip", "")) if pd.notna(row.get("tip")) else ""
        })

    return jsonify({
        "sanatcilar": sanatcilar,
        "toplam": toplam,
        "toplam_sayfa": toplam_sayfa,
        "sayfa": sayfa
    })

if __name__ == "__main__":
    app.run(debug=True)