import sys
import requests
from playwright.sync_api import sync_playwright

# Mengonfigurasi codec output konsol menjadi 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# Fungsi untuk mengirim pesan dan gambar ke Discord webhook
def send_discord_webhook(url, message, image_url, link, title, price):
    data = {
        "content": message,
        "embeds": [
            {
                "title": title,
                "description": f"Price: {price}",
                "image": {
                    "url": image_url
                },
                "url": link
            }
        ]
    }
    response = requests.post(url, json=data)
    if response.status_code == 204:
        print("Pesan dan gambar berhasil dikirim ke Discord webhook.")
    else:
        print("Gagal mengirim pesan dan gambar ke Discord webhook.")

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    # Mengarahkan halaman ke URL target
    page.goto('https://www.ourdailydose.net/latest.html')

    # Menunggu hingga halaman selesai dimuat
    page.wait_for_load_state('networkidle')

    # Mencari elemen <div> dengan class "page-wrapper"
    page_wrapper_div = page.query_selector('div.page-wrapper')

    # Mencari elemen <main> dengan class "page-main" di dalam page_wrapper_div
    page_main_elem = page_wrapper_div.query_selector('main.page-main')

    # Mencari elemen <div> dengan id "amasty-shopby-product-list" di dalam page_main_elem
    shopby_product_list_div = page_main_elem.query_selector('div#amasty-shopby-product-list')

    # Mencari semua elemen <ol> dengan class "product-items" di dalam shopby_product_list_div
    product_items_ols = shopby_product_list_div.query_selector_all('ol.product-items')

    # Mengirimkan data elemen <li> yang ditemukan ke Discord webhook
    for product_items_ol in product_items_ols:
        li_elements = product_items_ol.query_selector_all('li')

        for li_element in li_elements:
            # Mendapatkan elemen <a> dari li_element
            link_element = li_element.query_selector('a')
            link = link_element.get_attribute('href')

            # Mendapatkan elemen <img> dari li_element
            image_element = li_element.query_selector('img')
            image_url = image_element.get_attribute('src')
            title = image_element.get_attribute('alt')

            # Mendapatkan elemen <span> dengan class "price" dari li_element
            price_element = li_element.query_selector('span.price')
            price = price_element.inner_text()

            # URL Discord webhook
            webhook_url = "https://discord.com/api/webhooks/1108469757033840681/3Fa3lNCnfzGbRnDBsyF4lKpAdpOxMTe6QLQh3fLTT4AB0wljv23q3B8AKQzUXpfJcbag"

            # Mengirim pesan dan gambar ke Discord webhook
            send_discord_webhook(webhook_url, "New item found!", image_url, link, title, price)

    # Menutup browser
    browser.close()
