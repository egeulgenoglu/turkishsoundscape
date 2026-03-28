import pandas as pd
import re

iller = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya",
    "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur",
    "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Edirne",
    "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane",
    "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu",
    "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya",
    "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu",
    "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray",
    "Bayburt", "Karaman", "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır",
    "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
]

il_sira = {il: i for i, il in enumerate(iller)}

def turkey_var_mi(row):
    dogum = str(row["dogum_yeri"]) if pd.notna(row["dogum_yeri"]) else ""
    aktif = str(row["aktif_sehir"]) if pd.notna(row["aktif_sehir"]) else ""
    return "Turkey" in dogum or "Turkey" in aktif

def latin_alfabe_mi(metin):
    if pd.isna(metin) or metin == "":
        return True
    yabanci = re.compile(r'[\u0400-\u04FF\u0530-\u058F\u0370-\u03FF\u0600-\u06FF\u4E00-\u9FFF]')
    return not yabanci.search(str(metin))

def sehir_bul(metin):
    if pd.isna(metin) or metin == "":
        return ""
    metin_lower = str(metin).lower()
    for il in iller:
        if il.lower() in metin_lower:
            return il
    return ""

def son_sehir_belirle(row):
    aktif = sehir_bul(row["aktif_sehir"])
    if aktif:
        return aktif
    dogum = sehir_bul(row["dogum_yeri"])
    if dogum:
        return dogum
    return ""

df = pd.read_csv("rym_temiz.csv", encoding="utf-8-sig")
print(f"Baslangic: {len(df)} satir")

# 1. Turkey filtresi
df = df[df.apply(turkey_var_mi, axis=1)]
print(f"Turkey filtresi sonrasi: {len(df)} satir")

# 2. Yabanci alfabe filtresi
df = df[df["isim"].apply(latin_alfabe_mi)]
print(f"Latin alfabe filtresi sonrasi: {len(df)} satir")

# 3. Son sehir sütunu oluştur
df["son_sehir"] = df.apply(son_sehir_belirle, axis=1)

# 4. son_sehir boş olanları ele
df = df[df["son_sehir"] != ""]
print(f"Son sehir bos olmayanlar: {len(df)} satir")

# 5. Sırala
df["_sira"] = df["son_sehir"].map(il_sira).fillna(999)
df = df.sort_values(["_sira", "isim"], ascending=[True, True])
df = df.drop(columns=["_sira", "arama_sehri"])

# 6. Kaydet
df.to_csv("rym_temiz.csv", index=False, encoding="utf-8-sig")
print(f"\nTamamlandi! rym_temiz.csv kaydedildi.")
print(df.head(10))