import time
import requests
import argparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Fungsi untuk mengirim pesan dan gambar ke Discord webhook
def send_discord_webhook(url, message, image_url, link, brand):
    data = {
        "content": message,
        "embeds": [
            {
                "title": brand,
                "image": {
                    "url": image_url
                },
                "description": f"Link: {link}"
            }
        ]
    }
    response = requests.post(url, json=data)
    if response.status_code == 204:
        print("Pesan dan gambar berhasil dikirim ke Discord webhook.")
    else:
        print("Gagal mengirim pesan dan gambar ke Discord webhook.")

# Fungsi untuk memeriksa apakah banner baru telah dimuat
def check_new_banner(page, previous_html):
    div_element = page.query_selector('div.banner-homepage')
    if div_element:
        current_html = div_element.inner_html()
        if current_html != previous_html:
            return True, current_html
    return False, previous_html


# Fungsi untuk menjalankan otomasi refresh jika terdeteksi banner baru
def run_refresh_automation():
    # Kode implementasi fungsi run_refresh_automation

    # Menyimpan HTML awal dari elemen banner
    previous_html = None

    while True:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)  # Mengubah ke mode headless
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0", screen={"width": 1920, "height": 1080})
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = context.new_page()

            # Membuka halaman web Foot Locker Indonesia
            page.goto('https://www.footlocker.id')

            # Memeriksa apakah ada banner baru yang terload
            banner_loaded, current_html = check_new_banner(page, previous_html)
            if not banner_loaded:
                print("Tidak ada banner baru yang terload. Selesai.")
                browser.close()
                break

            # Mengirim pesan ke Discord webhook jika ada banner baru
            div_element = page.query_selector('div.banner-homepage')
            if div_element:
                # Menemukan elemen-elemen dengan class "owl-item" di dalam div "banner-homepage"
                owl_items = div_element.query_selector_all('.owl-item')

                for owl_item in owl_items:
                    # Mendapatkan elemen <img> dari owl_item
                    image_element = owl_item.query_selector('img')
                    image_url = image_element.get_attribute('data-src')

                    # Mendapatkan elemen <a> dari owl_item
                    link_element = owl_item.query_selector('a')
                    link = link_element.get_attribute('href')

                    # Mendapatkan atribut data-brand dari elemen <a>
                    brand = link_element.get_attribute('data-brand')

                    # URL Discord webhook
                    webhook_url = "https://discord.com/api/webhooks/1108383185533947985/Yfq7oX9ohSTkTOvORhx5liPA0wg6QckaUSnnz24ILtoRpq22i8TVQfC6KDbYCvY665of"

                    # Mengirim pesan dan gambar ke Discord webhook
                    send_discord_webhook(webhook_url, "Banner telah dimuat.", image_url, link, brand)

            # Menyimpan HTML baru sebagai previous_html
            previous_html = current_html

            # Menutup browser
            browser.close()

            # Tunggu beberapa detik agar halaman selesai dimuat
            time.sleep(5)

# Menjalankan otomasi refresh jika terdeteksi banner baru
run_refresh_automation()