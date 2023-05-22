import sys
import time
import aiohttp
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup

# Mengonfigurasi codec output konsol menjadi 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
current_page = 1
page_link = 'https://www.ourdailydose.net/latest.html'
webhook_url = "https://discord.com/api/webhooks/1108469757033840681/3Fa3lNCnfzGbRnDBsyF4lKpAdpOxMTe6QLQh3fLTT4AB0wljv23q3B8AKQzUXpfJcbag"

products = []

# Fungsi untuk mengirim pesan dan gambar ke Discord webhook
async def send_discord_webhook(url, message, image_url, link, title, price):
    data = {
        "content": message,
        "embeds": [
            {
                "title": title,
                "description": f"Price: {price}",
                "url": link,
                "image": {
                    "url": image_url
                }
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=data)
        print('webhook sent')
        # if response.status_code == 204:
        #     print("Pesan dan gambar berhasil dikirim ke Discord webhook.")
        # else:
        #     print("Gagal mengirim pesan dan gambar ke Discord webhook.")
        
        
async def getProduct(li_elements):
    for li_element in li_elements:
        link = li_element.find('a', href=True)['href']
        title = li_element.find('img', {'class': 'product-image-photo'})['alt']
        image_url = li_element.find('img', {'class': 'product-image-photo'})['src']
        price = li_element.find('span', {'class': 'price'}).text
        
        product = {
            'title': title,
            'image_url': image_url,
            'link': link,
            'price': price
        }
        
        await send_discord_webhook(webhook_url, "New Item Found", product['image_url'], product['link'], product['title'], product['price'])
        
async def scrap(playwright):
    global current_page
    global products
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    # Mengarahkan halaman ke URL target
    # Menunggu hingga halaman selesai dimuat
    while current_page < 5:
        await page.goto(f"{page_link}?p={current_page}")
        html = await page.inner_html('.product-items')
        soup = BeautifulSoup(html, 'html.parser')
        li_elements = soup.find_all('li', {'class': 'product-item'})
        
        asyncio.create_task(getProduct(li_elements))
        await asyncio.sleep(0)
        print('task running')
        current_page += 1

    # Menutup browser
    await browser.close()
    print('scrap completed')
    
async def main():
    async with async_playwright() as playwright:
        asyncio.create_task(scrap(playwright))
        # print('task running')
        await asyncio.wait(asyncio.all_tasks())
        print('all tasks completed')

asyncio.run(main())