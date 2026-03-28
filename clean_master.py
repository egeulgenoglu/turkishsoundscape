import pandas as pd
import os
import re

# --- normalize (eşleşme için) ---
def normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace("ı", "i").replace("ö", "o").replace("ü", "u")
    text = text.replace("ş", "s").replace("ç", "c").replace("ğ", "g")
    text = re.sub(r"[^a-z0-9]", "", text)
    return text

# --- isim/sanatçı kolonu bul ---
def isim_kolonu_bul(df):
    for col in df.columns:
        c = col.lower()
        if "isim" in c or "sanat" in c or "artist" in c or "name" in c:
            return col
    return None

# --- spotify id bul ---
def spotify_id_bul(df):
    for col in df.columns:
        c = col.lower()
        if "spotify" in c and "id" in c:
            return col
    return None

# --- Followers / Popularity için max seç ---
def pick_max(series):
    nums = []

    for value in series.dropna():
        parts = str(value).split("|")
        for p in parts:
            try:
                nums.append(float(p.strip()))
            except:
                pass

    if not nums:
        return None

    return int(max(nums))

# --- text merge (duplicate temiz) ---
def merge_text(series):
    vals = set()

    for item in series.dropna():
        parts = str(item).split("|")
        for p in parts:
            p = p.strip()
            if p:
                vals.add(p)

    return " | ".join(sorted(vals)) if vals else None


print("Dosyalar okunuyor...\n")

tum_df = []

for file in os.listdir():
    if file.endswith(".csv") or file.endswith(".xlsx"):
        print(f"→ {file}")

        try:
            if file.endswith(".csv"):
                df = pd.read_csv(file, encoding="utf-8-sig", low_memory=False)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            print(f"❌ hata: {e}")
            continue

        isim_col = isim_kolonu_bul(df)
        if not isim_col:
            print("⚠️ isim yok → atlandı\n")
            continue

        # orijinal isim korunur
        df = df.rename(columns={isim_col: "isim_orijinal"})

        # normalize eşleşme için
        df["_norm"] = df["isim_orijinal"].apply(normalize)

        # spotify id
        sid_col = spotify_id_bul(df)
        if sid_col:
            df["Spotify_ID"] = df[sid_col]
        else:
            df["Spotify_ID"] = None

        tum_df.append(df)

print("\nBirleştiriliyor...\n")
master = pd.concat(tum_df, ignore_index=True)

# --- GROUP KEY ---
master["group_key"] = master["Spotify_ID"].fillna(master["_norm"])

print("Sanatçılar birleştiriliyor...\n")

def merge_group(group):
    result = {}

    # isim → en iyi/orijinal olanı seç
    isimler = group["isim_orijinal"].dropna().tolist()
    result["isim"] = max(isimler, key=len) if isimler else None

    # Spotify ID
    result["Spotify_ID"] = (
        group["Spotify_ID"].dropna().iloc[0]
        if group["Spotify_ID"].notna().any()
        else None
    )

    for col in group.columns:
        if col in ["isim_orijinal", "_norm", "group_key", "Spotify_ID"]:
            continue

        col_lower = col.lower()

        if "followers" in col_lower:
            result["Followers"] = pick_max(group[col])

        elif "popularity" in col_lower:
            result["Popularity"] = pick_max(group[col])

        elif any(x in col_lower for x in ["sehir", "city", "yer"]):
            result[col] = merge_text(group[col])

        elif any(x in col_lower for x in ["cinsiyet", "gender"]):
            result[col] = merge_text(group[col])

        elif any(x in col_lower for x in ["tur", "genre"]):
            result[col] = merge_text(group[col])

        else:
            result[col] = merge_text(group[col])

    return pd.Series(result)

# --- GROUPBY MERGE ---
master_final = master.groupby("group_key", as_index=False).apply(merge_group)

# --- SIRALAMA ---
master_final["has_spotify"] = master_final["Spotify_ID"].notna()

master_final = master_final.sort_values(
    by=["has_spotify", "isim"],
    ascending=[False, True]
)

master_final = master_final.drop(columns=["has_spotify"], errors="ignore")

# --- KAYDET ---
output_file = "final_master_clean_v2.xlsx"
master_final.to_excel(output_file, index=False)

print(f"\n✅ {output_file} hazır!")
print(f"Toplam sanatçı: {len(master_final)}")
print(f"Sütun sayısı: {len(master_final.columns)}")