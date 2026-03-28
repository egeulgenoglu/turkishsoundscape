import pandas as pd
import os
import re

# --- normalize ---
def normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace("ı", "i").replace("ö", "o").replace("ü", "u")
    text = text.replace("ş", "s").replace("ç", "c").replace("ğ", "g")
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

print("Dosyalar okunuyor...\n")

tum_df = []

for file in os.listdir():
    if file.endswith(".csv") or file.endswith(".xlsx"):
        print(f"→ {file}")

        try:
            if file.endswith(".csv"):
                try:
                    df = pd.read_csv(file, encoding="utf-8-sig")
                except:
                    df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            print(f"❌ okunamadı: {e}")
            continue

        isim_col = isim_kolonu_bul(df)

        if isim_col is None:
            print("⚠️ isim yok → atlandı\n")
            continue

        df = df.rename(columns={isim_col: "isim"})
        df["isim"] = df["isim"].apply(normalize)

        sid_col = spotify_id_bul(df)
        if sid_col:
            df["Spotify_ID"] = df[sid_col]
        else:
            df["Spotify_ID"] = None

        df["kaynak"] = file

        tum_df.append(df)

print("\nBirleştiriliyor...\n")
master = pd.concat(tum_df, ignore_index=True)

# --- KRİTİK KISIM: MERGE LOGIC ---
def merge_group(group):
    result = {}

    for col in group.columns:
        values = group[col].dropna().unique()

        if len(values) == 0:
            result[col] = None
        elif len(values) == 1:
            result[col] = values[0]
        else:
            # birden fazla farklı değer varsa → hepsini birleştir
            result[col] = " | ".join(map(str, values))

    return pd.Series(result)

print("Spotify ID'lere göre birleştiriliyor...\n")

# Spotify ID olanlar
with_id = master[master["Spotify_ID"].notna()]
merged_with_id = with_id.groupby("Spotify_ID", as_index=False).apply(merge_group)

# Spotify ID olmayanlar (bunlara dokunmuyoruz)
without_id = master[master["Spotify_ID"].isna()]

# tekrar birleştir
master_final = pd.concat([merged_with_id, without_id], ignore_index=True)

# --- sıralama ---
master_final["isim"] = master_final["isim"].fillna("")

master_final["has_spotify"] = master_final["Spotify_ID"].notna()

master_final = master_final.sort_values(
    by=["has_spotify", "isim"],
    ascending=[False, True]
)

master_final = master_final.drop(columns=["has_spotify"], errors="ignore")

# kaydet
master_final.to_csv("master.csv", index=False, encoding="utf-8-sig")

print("✅ master.csv hazır!")
print(f"Toplam satır: {len(master_final)}")
print(f"Sütun sayısı: {len(master_final.columns)}")