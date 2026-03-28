import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

TURLER = [
    "turkish pop", "turkish rock", "turkish hip hop", "turkish trap",
    "turkish alt pop", "turkish folk", "turkish singer-songwriter",
    "turkish alternative rock", "turkish deep house", "turkish jazz",
    "turkish trap pop", "turkish instrumental", "turkish psych",
    "turkish punk", "turkish metal", "turkish edm", "turkish electronic",
    "turkish post-punk", "turkish classical", "turkish classical performance",
    "turkish death metal", "turkish black metal", "turkish reggae",
    "turkish experimental", "turkish modern jazz", "turkish soundtrack",
    "turkish hardcore", "classic turkish pop", "deep turkish pop",
    "new school turkce rap", "turkce drill", "turkce slow sarkilar",
    "turkce kadin rap", "turkce remix", "turkce trap metal",
    "anadolu rock", "arabesk", "karadeniz turkuleri", "karadeniz pop",
    "turk sanat muzigi", "oyun havasi", "bozlak", "rumeli turkuleri",
    "ilahiler", "huzunlu sarkilar", "baglama", "ulkucu sarkilar",
    "cocuk sarkilari"
]

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(
    options=options,
    driver_executable_path=r"C:\Users\Ege\AppData\Roaming\undetected_chromedriver\chromedriver.exe"
)

tum_sanatcilar = {}

for tur in TURLER:
    tur_url = tur.replace(" ", "+")
    url = f"https://everynoise.com/research.cgi?mode=genre&name={tur_url}"
    print(f"\n'{tur}' yukleniyor...")

    try:
        driver.get(url)
        time.sleep(12)

        try:
            checkbox = driver.find_element(By.ID, "showtags")
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(3)
        except:
            pass

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        boxes = soup.find_all("div", class_="box")
        sanatci_sayac = 0

        for box in boxes:
            try:
                artbox = box.find("div", class_="artbox")
                if not artbox:
                    continue
                a_tag = artbox.find("a", href=True)
                if not a_tag:
                    continue
                href = a_tag["href"]
                if "spotify:artist:" not in href:
                    continue
                spotify_id = href.replace("spotify:artist:", "").strip()

                isim_div = box.find("div", class_="artistname")
                if not isim_div:
                    continue
                isim = isim_div.get_text(strip=True)

                notlar = box.find_all("div", class_="note")
                takipci = ""
                en_tur = ""
                spotify_tags = ""

                for not_div in notlar:
                    metin = not_div.get_text(strip=True)
                    siniflar = not_div.get("class", [])
                    if "followers" in metin.lower():
                        takipci = metin.lower().replace("followers", "").strip().replace(",", "")
                    elif "tags" in siniflar:
                        spotify_tags = metin.replace("#", "").strip()
                    elif not_div.find("a"):
                        en_link = not_div.find("a")
                        if en_link:
                            en_tur = en_link.get_text(strip=True)

                # Spotify ismi artistprofile linkinden al
                isim_link = isim_div.find("a", href=True)
                spotify_isim = isim_link.get_text(strip=True) if isim_link else isim

                if spotify_id not in tum_sanatcilar:
                    tum_sanatcilar[spotify_id] = {
                        "isim": isim,
                        "Spotify_Isim": spotify_isim,
                        "Spotify_ID": spotify_id,
                        "Takipci": takipci,
                        "EveryNoise_Tur": en_tur,
                        "Spotify_Tur": spotify_tags
                    }
                sanatci_sayac += 1

            except:
                continue

        print(f"  -> {sanatci_sayac} sanatci bulundu (toplam benzersiz: {len(tum_sanatcilar)})")

        if TURLER.index(tur) % 5 == 0:
            df_ara = pd.DataFrame(list(tum_sanatcilar.values()))
            df_ara.to_csv("en_ara.csv", index=False, encoding="utf-8-sig")

        time.sleep(5)

    except Exception as e:
        print(f"  Hata: {e}")
        time.sleep(5)

driver.quit()

print(f"\nToplam benzersiz sanatci: {len(tum_sanatcilar)}")
df = pd.DataFrame(list(tum_sanatcilar.values()))
df["Takipci"] = pd.to_numeric(df["Takipci"], errors="coerce")
df = df.sort_values("Takipci", ascending=False, na_position="last")
df.to_csv("en_sanatcilar2.csv", index=False, encoding="utf-8-sig")
print("en_sanatcilar2.csv kaydedildi!")