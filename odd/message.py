import sys
import aiohttp
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
import re

# Mengonfigurasi codec output konsol menjadi 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
page_link = 'https://www.ourdailydose.net/latest.html'
webhook_url = "https://discord.com/api/webhooks/1108469757033840681/3Fa3lNCnfzGbRnDBsyF4lKpAdpOxMTe6QLQh3fLTT4AB0wljv23q3B8AKQzUXpfJcbag"
current_page = 27

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
        await session.post(url, json=data)
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
    
    asyncio.create_task(getProduct(li_elements))

async def scrap(playwright):
    global current_page
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto(page_link)
    
    while await page.is_visible('.product-items'):
        print(await page.is_visible('.product-items'))
        await page.goto(f"{page_link}?p={current_page}")
        
        asyncio.create_task(scrap_page(page))
        
        print(f'Task running for page {current_page}')
        current_page += 1

    # Menutup browser
    await browser.close()
    print('Scraping completed')

    # wait for 10 seconds and cancel all tasks
    await asyncio.sleep(10)
    for task in asyncio.all_tasks():
        task.cancel()
    
async def main():
    async with async_playwright() as playwright:
        await scrap(playwright)

asyncio.run(main())