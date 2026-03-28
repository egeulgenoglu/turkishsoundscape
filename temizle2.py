import pandas as pd
import numpy as np

df = pd.read_csv("master.csv", encoding="utf-8-sig", low_memory=False)
baslangic = len(df)
print(f"Baslangic: {baslangic} satir")

def ilk_dolu(*vals):
    for v in vals:
        if pd.notna(v) and str(v).strip() not in ["", "nan"]:
            return str(v).strip()
    return np.nan

def birlestir_degerler(*vals):
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

def max_sayi(*vals):
    sayilar = []
    for val in vals:
        if pd.notna(val):
            for v in str(val).split("|"):
                try:
                    sayilar.append(float(v.strip()))
                except:
                    pass
    return int(max(sayilar)) if sayilar else np.nan

def birlestir_grup(grup):
    if len(grup) == 1:
        return grup.iloc[0]
    sonuc = {}
    for col in grup.columns:
        degerler = grup[col].dropna().astype(str).str.strip()
        degerler = degerler[degerler.str.lower() != "nan"]
        if len(degerler) == 0:
            sonuc[col] = np.nan
        elif col in ["Followers", "Popularity"]:
            sayilar = []
            for v in degerler:
                for p in str(v).split("|"):
                    try:
                        sayilar.append(float(p.strip()))
                    except:
                        pass
            sonuc[col] = int(max(sayilar)) if sayilar else np.nan
        else:
            benzersiz = list(dict.fromkeys(degerler.tolist()))
            sonuc[col] = benzersiz[0] if len(benzersiz) == 1 else ", ".join(benzersiz)
    return pd.Series(sonuc)

# Spotify ID olanlar
df_id = df[df["Spotify_ID"].notna() & (df["Spotify_ID"].astype(str).str.strip() != "nan")].copy()
df_noid = df[df["Spotify_ID"].isna() | (df["Spotify_ID"].astype(str).str.strip() == "nan")].copy()

print(f"Spotify ID li: {len(df_id)}, IDsiz: {len(df_noid)}")

# Spotify ID tekrarlarini birlestir
df_id_temiz = df_id.groupby("Spotify_ID", sort=False).apply(birlestir_grup, include_groups=False).reset_index()
print(f"ID tekrarlari birlestirildikten sonra: {len(df_id_temiz)} satir")

# IDsiz satirlari isim bazinda birlestir
df_noid["isim_norm"] = df_noid["isim"].astype(str).str.lower().str.strip()
df_noid_temiz = df_noid.groupby("isim_norm", sort=False).apply(birlestir_grup, include_groups=False).reset_index()
df_noid_temiz = df_noid_temiz.drop(columns=["isim_norm"], errors="ignore")
print(f"IDsiz isim tekrarlari birlestirildikten sonra: {len(df_noid_temiz)} satir")

# IDsiz ama ismi ID'li listede olanlari birlestir
df_id_temiz["isim_norm"] = df_id_temiz["isim"].astype(str).str.lower().str.strip()
df_noid_temiz["isim_norm"] = df_noid_temiz["isim"].astype(str).str.lower().str.strip()

df_id_isimler = set(df_id_temiz["isim_norm"].tolist())
df_noid_eslesen = df_noid_temiz[df_noid_temiz["isim_norm"].isin(df_id_isimler)].copy()
df_noid_kalan = df_noid_temiz[~df_noid_temiz["isim_norm"].isin(df_id_isimler)].copy()

print(f"IDsiz ama isim eslesen: {len(df_noid_eslesen)}, tamamen yeni: {len(df_noid_kalan)}")

if len(df_noid_eslesen) > 0:
    df_birlesmis = pd.concat([df_id_temiz, df_noid_eslesen], ignore_index=True)
    df_id_temiz = df_birlesmis.groupby("isim_norm", sort=False).apply(birlestir_grup, include_groups=False).reset_index()
    print(f"Isim bazli birlestirmeden sonra: {len(df_id_temiz)} satir")

df_id_temiz = df_id_temiz.drop(columns=["isim_norm"], errors="ignore")
df_noid_kalan = df_noid_kalan.drop(columns=["isim_norm"], errors="ignore")

# Followers ve Popularity duzelt
for df_temp in [df_id_temiz, df_noid_kalan]:
    df_temp["Followers"] = pd.to_numeric(df_temp["Followers"], errors="coerce")
    df_temp["Popularity"] = pd.to_numeric(df_temp["Popularity"], errors="coerce")

# Sirala
df_id_temiz = df_id_temiz.sort_values("Followers", ascending=False, na_position="last")
df_noid_kalan = df_noid_kalan.sort_values("isim", ascending=True, na_position="last")

# Birlestir
df_final = pd.concat([df_id_temiz, df_noid_kalan], ignore_index=True)

print(f"\nBaslangic: {baslangic} satir")
print(f"Sonuc: {len(df_final)} satir")
print(f"Eksiltilen: {baslangic - len(df_final)} satir")

df_final.to_csv("master_temiz2.csv", index=False, encoding="utf-8-sig")
print("master_temiz2.csv kaydedildi!")