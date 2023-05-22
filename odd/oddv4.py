import sys
import aiohttp
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup

# Mengonfigurasi codec output konsol menjadi 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
page_link = 'https://www.ourdailydose.net/latest.html'
webhook_url = "https://discord.com/api/webhooks/1109033165227573348/lblQqGbyVTjgimusJ8XE4WASeVLmyeaN12QG6zAcm3c-F4pPY5RsLH-ug3iFTp5jBnts"

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
        print('Webhook sent')

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

async def scrap_page(page):
    html = await page.inner_html('.product-items')
    soup = BeautifulSoup(html, 'html.parser')
    li_elements = soup.find_all('li', {'class': 'product-item'})
    
    await getProduct(li_elements)

async def scrap(playwright):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    
    current_page = 1
    while current_page < 5:
        await page.goto(f"{page_link}?p={current_page}")
        await scrap_page(page)
        current_page += 1

    # Menutup browser
    await browser.close()
    print('Scraping completed')

async def main():
    async with async_playwright() as playwright:
        await scrap(playwright)

asyncio.run(main())