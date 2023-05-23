import requests
import json
import os
import base64
from datetime import datetime
from itertools import cycle
import random
import time
import sys

url = 'https://atmos.co.id/products.json?limit=250'
discord_webhook_url = 'https://discord.com/api/webhooks/1109907397776003232/RPsTNW21a-58LFoy8VJ_1WzQkGRZgXr1CIG52R4gQVcyjy_gSoUnkEAfSG_MLR5mLxMF'
data_file_path = 'atmos.json'

proxy_list = []
# Read proxy list from proxy.txt file
with open('proxy1.txt', 'r') as file:
    proxy_list = file.read().splitlines()


def send_webhook_notification(embeds, proxy=None):
    payload = {'embeds': embeds}
    headers = {'Content-Type': 'application/json'}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    response = requests.post(discord_webhook_url, data=json.dumps(payload), headers=headers, proxies=proxies)
    if response.status_code == 204:
        print('Data berhasil dikirim ke Discord webhook.')
    else:
        print('Terjadi kesalahan saat mengirim data ke Discord webhook:', response.status_code)


def compare_products(previous_products, current_products):
    new_products = []
    restocked_products = []
    updated_sizes_products = []

    previous_product_ids = {product['id']: product for product in previous_products}
    current_product_ids = {product['id']: product for product in current_products}

    for product_id, current_product in current_product_ids.items():
        if product_id not in previous_product_ids:
            new_products.append(current_product)
        else:
            previous_product = previous_product_ids[product_id]
            previous_sizes = set(
                [variant['option1'] for variant in previous_product['variants'] if variant['option1'].startswith('US ')]
            )
            current_sizes = set(
                [variant['option1'] for variant in current_product['variants'] if variant['option1'].startswith('US ')]
            )

            if current_sizes - previous_sizes:
                updated_sizes_products.append(current_product)

    for product_id, previous_product in previous_product_ids.items():
        if product_id not in current_product_ids:
            restocked_products.append(previous_product)

    return new_products, restocked_products, updated_sizes_products

def load_previous_products():
    if not os.path.exists(data_file_path):
        with open(data_file_path, 'w') as file:
            json.dump([], file)

    with open('atmos.json', 'r') as file:
        data = file.read()
        return json.loads(data)

def save_current_products(current_products):
    with open(data_file_path, 'w') as file:
        json.dump(current_products, file)

def run_with_proxy():
    while True:
        try:
            proxy = random.choice(proxy_list)
            proxy_parts = proxy.split(':')
            host = proxy_parts[0]
            port = proxy_parts[1]
            username = proxy_parts[2]
            password = proxy_parts[3]

            proxy_cred = f"{username}:{password}"
            proxy_auth = "Basic " + base64.b64encode(proxy_cred.encode()).decode()

            proxies = {
                'http': f'http://{host}:{port}',
                'proxy-authorization': proxy_auth
            }

            response = requests.get(url, proxies=proxies)
            if response.status_code == 200:
                json_content = response.json()
                current_products = json_content['products']

                previous_products = load_previous_products()

                new_products, restocked_products, updated_sizes_products = compare_products(previous_products,current_products)

                for product in new_products:
                    if 'title' in product:
                        title = product['title']
                        if 'variants' in product and len(product['variants']) > 0:
                            variants = product['variants']
                            available_sizes = [variant['option1'] for variant in variants if variant['available'] and variant['option1'].startswith('US ')]

                            if available_sizes:
                                sizes_str = '\n'.join([f'[Size {size}](https://atmos.co.id/cart/{variant["id"]}:1)' for variant in variants for size in available_sizes if variant['option1'] == size])
                                price = variants[0]['price']
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                product_url = f'https://atmos.co.id/products/{product["handle"]}'
                                product_link = f'[Product Link]({product_url})'

                                embeds = [
                                    {
                                        'title': f'{title}\n\n' "New Product Loaded",
                                        'description': f'Fetch: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n**{title}**\n\n**Price:** {price}\n\n**Available Sizes:**\n{sizes_str}',
                                        'image': {'url': product['images'][0]['src']}
                                    }
                                ]

                                send_webhook_notification(embeds)
                                time.sleep(3)  # 3-second delay

                if restocked_products:
                    embeds = []
                    for product in restocked_products:
                        if 'variants' in product and len(product['variants']) > 0:
                            variants = product['variants']
                            available_sizes = [variant['option1'] for variant in variants if variant['available'] and variant['option1'].startswith('US ')]
                            sizes_str = ', '.join(available_sizes) if available_sizes else 'No available sizes'

                            product_url = f'https://atmos.co.id/products/{product["handle"]}'
                            product_link = f'[Product Link]({product_url})'

                            embed = {
                                'title': f'{title}\n\n' "New Product Restocked",
                                'description': f'**{product["title"]}**\n\n{product_link}',
                                'fields': [
                                    {'name': 'Available Sizes', 'value': sizes_str}
                                ]
                            }
                            embeds.append(embed)

                            sizes_str = '\n'.join([f'[Size {size}](https://atmos.co.id/cart/{variant["id"]}:1)' for variant in variants for size in available_sizes if variant['option1'] == size])
                            price = variants[0]['price']
                            timestamp = datetime.now().strftime("%H:%M:%S")

                            embeds.append({
                                'title': f'{title}\n\n' "New Product Restocked",
                                'description': f'Atmos Monitor - Hari Ini: {timestamp}\n\n**{title}**\n\n**Price:** {price}\n\n**Available Sizes:**\n{sizes_str}',
                                'url': product_url,
                                'image': {'url': product['images'][0]['src']}
                            })

                    send_webhook_notification(embeds)
                    time.sleep(3)  # 3-second delay
                    
                if updated_sizes_products:
                    for product in updated_sizes_products:
                        title = product['title']
                        variants = product['variants']
                        available_sizes = [
                            variant['option1'] for variant in variants if variant['available'] and variant['option1'].startswith('US ')
                        ]

                        sizes_str = '\n'.join([f'[Size {size}](https://atmos.co.id/cart/{variant["id"]}:1)' for variant in variants for size in
                        available_sizes if variant['option1'] == size])
                        price = variants[0]['price']
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        product_url = f'https://atmos.co.id/products/{product["handle"]}'
                        product_link = f'[Product Link]({product_url})'

                        embeds = [
                            {
                                'title': f'{title}\n\n' "New Available Size",
                                'description': f'Fetch: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n**{title}**\n\n**Price:** {price}\n\n**Available Sizes:**\n{sizes_str}',
                                'image': {'url': product['images'][0]['src']}
                            }
                        ]

                        send_webhook_notification(embeds)
                        time.sleep(3)  # 3-second delay
                else:
                    print('Tidak Ada Produk Restock')

                save_current_products(current_products)

            else:
                print('Terjadi kesalahan saat fetching:', response.status_code)

            time.sleep(3)  # 3-second delay before making the next request

        except requests.exceptions.RequestException as e:
            print('Terjadi kesalahan saat melakukan request:', str(e))

def run_without_proxy():
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                json_content = response.json()
                current_products = json_content['products']

                previous_products = load_previous_products()

                new_products, restocked_products, updated_sizes_products = compare_products(previous_products,current_products)

                for product in new_products:
                    if 'title' in product:
                        title = product['title']
                        if 'variants' in product and len(product['variants']) > 0:
                            variants = product['variants']
                            available_sizes = [variant['option1'] for variant in variants if variant['available'] and variant['option1'].startswith('US ')]

                            if available_sizes:
                                sizes_str = '\n'.join([f'[Size {size}](https://atmos.co.id/cart/{variant["id"]}:1)' for variant in variants for size in available_sizes if variant['option1'] == size])
                                price = variants[0]['price']
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                product_url = f'https://atmos.co.id/products/{product["handle"]}'
                                product_link = f'[Product Link]({product_url})'

                                embeds = [
                                    {
                                        'title': f'{title}\n\n' "New Product Loaded",
                                        'description': f'Fetch: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n**{title}**\n\n**Price:** {price}\n\n**Available Sizes:**\n{sizes_str}',
                                        'url': product_url,
                                        'image': {'url': product['images'][0]['src']}
                                    }
                                ]

                                send_webhook_notification(embeds, None)
                                time.sleep(3)  # 3-second delay

                if restocked_products:
                    embeds = []
                    for product in restocked_products:
                        if 'variants' in product and len(product['variants']) > 0:
                            variants = product['variants']
                            available_sizes = [variant['option1'] for variant in variants if variant['available'] and variant['option1'].startswith('US ')]
                            sizes_str = ', '.join(available_sizes) if available_sizes else 'No available sizes'

                            product_url = f'https://atmos.co.id/products/{product["handle"]}'
                            product_link = f'[Product Link]({product_url})'

                            embed = {
                                'title': f'{title}\n\n' "New Product Restocked",
                                'description': f'**{product["title"]}**\n\n{product_link}',
                                'fields': [
                                    {'name': 'Available Sizes', 'value': sizes_str}
                                ]
                            }
                            embeds.append(embed)

                            sizes_str = '\n'.join([f'[Size {size}](https://atmos.co.id/cart/{variant["id"]}:1)' for variant in variants for size in available_sizes if variant['option1'] == size])
                            price = variants[0]['price']
                            timestamp = datetime.now().strftime("%H:%M:%S")

                            embeds.append({
                                'title': f'{title}\n\n' "New Product Restocked",
                                'description': f'Fetch: {timestamp}\n\n**{title}**\n\n**Price:** {price}\n\n**Available Sizes:**\n{sizes_str}',
                                'url': product_url,
                                'image': {'url': product['images'][0]['src']}
                            })

                    send_webhook_notification(embeds, None)
                    time.sleep(3)  # 3-second delay
                    
                if updated_sizes_products:
                    for product in updated_sizes_products:
                        title = product['title']
                        variants = product['variants']
                        available_sizes = [
                            variant['option1'] for variant in variants if variant['available'] and variant['option1'].startswith('US ')
                        ]

                        sizes_str = '\n'.join([f'[Size {size}](https://atmos.co.id/cart/{variant["id"]}:1)' for variant in variants for size in
                        available_sizes if variant['option1'] == size])
                        price = variants[0]['price']
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        product_url = f'https://atmos.co.id/products/{product["handle"]}'
                        product_link = f'[Product Link]({product_url})'

                        embeds = [
                            {
                                'title': f'{title}\n\n' "New Available Size",
                                'description': f'Fetch: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n**{title}**\n\n**Price:** {price}\n\n**Available Sizes:**\n{sizes_str}',
                                'image': {'url': product['images'][0]['src']}
                            }
                        ]
                        send_webhook_notification(embeds)
                        time.sleep(3)  # 3-second delay
                        save_current_products(current_products)
                else:
                    print('Tidak Ada Produk Restock')

                save_current_products(current_products)

            else:
                print('Terjadi kesalahan saat fetching:', response.status_code)

            time.sleep(3)  # 3-second delay before making the next request

        except requests.exceptions.RequestException as e:
            print('Terjadi kesalahan saat melakukan request:', str(e))

def main():
    print("1. Run with Proxy")
    print("2. Run without Proxy")
    option = input("Pilih opsi: ")

    if option == "1":
        run_with_proxy()
    elif option == "2":
        run_without_proxy()
    else:
        print("Opsi yang Anda pilih tidak valid.")

    # Menunggu tombol enter ditekan untuk menghentikan monitor mode
    input("Tekan enter untuk menghentikan monitor mode...")
    sys.exit(0)


if __name__ == '__main__':
    main()