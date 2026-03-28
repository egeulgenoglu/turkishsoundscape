import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import os

sehirler = [
    ("Sivas", "50km", "Sivas"),
    ("Tekirdağ", "25km", "Tekirdağ"),
    ("Zonguldak", "25km", "Zonguldak"),
    ("Karaman", "25km", "Karaman"),
    ("Kırıkkale", "25km", "Kırıkkale"),
    ("Şırnak", "25km", "Şırnak"),
    ("Iğdır", "25km", "Iğdır"),
    ("Karabük", "25km", "Karabük"),
    ("Kilis", "25km", "Kilis"),
    ("Osmaniye", "25km", "Osmaniye"),
    ("Düzce", "25km", "Düzce"),
]

def insan_gibi_bekle():
    sure = random.uniform(20, 40)
    print(f"Bekleniyor: {sure:.1f} saniye...")
    time.sleep(sure)

def scroll_yap(driver):
    for _ in range(random.randint(2, 4)):
        driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)})")
        time.sleep(random.uniform(0.5, 1.5))

def parse_sanatci(artist_tag):
    isim = artist_tag.get_text(strip=True)
    dogum = ""
    aktif = ""
    tip = "solo"
    h3 = artist_tag.find_parent("h3")
    if not h3:
        return isim, dogum, aktif, tip
    ust_td = h3.find_parent("td")
    if not ust_td:
        return isim, dogum, aktif, tip
    info_table = ust_td.find("table", class_="mbgen")
    if not info_table:
        return isim, dogum, aktif, tip
    for row in info_table.select("tr"):
        cells = row.select("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            link = cells[1].select_one("a[href*='/location/']")
            if link:
                if "Born" in label:
                    dogum = link.get_text(strip=True)
                elif "Currently" in label:
                    aktif = link.get_text(strip=True)
            if label == "Members":
                tip = "grup"
    return isim, dogum, aktif, tip

def scrape_sehir(driver, arama_adi, vicinity, url):
    sanatcilar = []
    sayfa = 1
    while True:
        tam_url = f"https://rateyourmusic.com/location/{vicinity}/{url}/Turkey/_/artists/{sayfa}/"
        print(f"Cekiliyor: {arama_adi} ({vicinity}) - Sayfa {sayfa}")
        try:
            driver.get(tam_url)
            time.sleep(8)
            scroll_yap(driver)
            time.sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            if "Just a moment" in html or "Bir dakika" in html:
                print("Cloudflare engeli! 30 saniye bekleniyor...")
                time.sleep(30)
                continue
            artistler = soup.select("a.artist")
            if not artistler:
                if "captcha" in html.lower() or "verify you are human" in html.lower() or "i am not a robot" in html.lower():
                    print(f"\n  !! CAPTCHA ALGILANDI !!")
                    print(f"  Tarayicida CAPTCHA'yi coz, sonra ENTER'a bas...")
                    input()
                else:
                    print(f"  Bos sayfa, sehir bitti.")
                    print(f"\n{'='*40}")
                    print(f"{arama_adi} TAMAMLANDI")
                    print(f"Toplam sayfa: {sayfa-1}")
                    print(f"Toplam sanatci: {len(sanatcilar)}")
                    print(f"{'='*40}\n")
                    break
            else:
                for s in artistler:
                    isim, dogum, aktif, tip = parse_sanatci(s)
                    sanatcilar.append({
                        "isim": isim,
                        "dogum_yeri": dogum,
                        "aktif_sehir": aktif,
                        "tip": tip,
                        "arama_sehri": arama_adi
                    })
                print(f"  {len(artistler)} sanatci bulundu")
            sayfa += 1
            insan_gibi_bekle()
        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(15)
    return sanatcilar

def main():
    tamamlanan = set()
    if os.path.exists("rym_sanatcilar.csv"):
        mevcut = pd.read_csv("rym_sanatcilar.csv", encoding="utf-8-sig")
        tamamlanan = set(mevcut["arama_sehri"].unique())
        print(f"Mevcut veri: {len(mevcut)} sanatci, tamamlanan sehirler: {tamamlanan}")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    driver = uc.Chrome(options=options, driver_executable_path=r"C:\Users\Ege\AppData\Roaming\undetected_chromedriver\chromedriver.exe")
    driver.get("https://rateyourmusic.com")
    print("Tarayici acildi. Giris yap, sonra Enter'a bas...")
    input()

    for arama_adi, vicinity, url in sehirler:
        if arama_adi in tamamlanan:
            print(f"{arama_adi} zaten tamamlandi, atlaniyor...")
            continue
        sanatcilar = scrape_sehir(driver, arama_adi, vicinity, url)
        if sanatcilar:
            df = pd.DataFrame(sanatcilar)
            if os.path.exists("rym_sanatcilar.csv"):
                df.to_csv("rym_sanatcilar.csv", index=False, encoding="utf-8-sig", mode='a', header=False)
            else:
                df.to_csv("rym_sanatcilar.csv", index=False, encoding="utf-8-sig")
            print(f"Kaydedildi: {arama_adi} - {len(sanatcilar)} sanatci")

    driver.quit()
    toplam = pd.read_csv("rym_sanatcilar.csv", encoding="utf-8-sig")
    print(f"\nTUM SEHIRLER TAMAMLANDI!")
    print(f"Toplam sanatci: {len(toplam)}")

main()