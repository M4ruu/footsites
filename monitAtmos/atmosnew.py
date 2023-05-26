import base64
import json
import os
import random
import time
import requests
import locale

session = requests.Session()
url = 'https://atmos.co.id/collections/new-arrivals/products.json?limit=250'
discord_webhook_url = 'https://discord.com/api/webhooks/1111512598903521311/JUnhE8bq9vQ23GO9C8IVixGWQFQEad-oH6yuT1kf_-wggLDkBlCCNJ8u8b5G9Ogs3CfN'
data_file_path = 'atmos.json'
proxy_list = []

def save_product_data(json_obj):
    with open('atmos.json', 'w') as file:
        json.dump(json_obj, file, indent=4)

def debug_json(json_obj):
    with open('debug.json', 'w') as file:
        json.dump(json_obj, file, indent=4)

def rupiah_format(angka, with_prefix=False, desimal=0):
    locale.setlocale(locale.LC_NUMERIC, 'IND')
    rupiah = locale.format_string("%.*f", (desimal, angka), True)
    if with_prefix:
        return "Rp. {}".format(rupiah)
    return rupiah

def compare_products(previous_products, current_products):
    new_products = [] # list of new products
    restocked_products = [] # list of restocked products
    available_product_size = [] # list of available product size

    previous_product_ids = {product['id']: product for product in previous_products}
    current_product_ids = {product['id']: product for product in current_products}

    for product_id, current_product in current_product_ids.items():
        if product_id not in previous_product_ids:
            new_products.append(current_product)
            for variant in current_product['variants']:
                if variant['available'] == True:
                    available_product_size.append(
                        {   'id': product_id, 
                            'available_size': [variant['option1'] for variant in current_product['variants'] if variant['available'] == True], 
                            'variant_id': [variant['id'] for variant in current_product['variants'] if variant['available'] == True], 
                            'title': current_product['title'], 
                            'image': current_product['images'][0]['src'], 
                            'price': current_product['variants'][0]['price']
                        })

        else:
            previous_product = previous_product_ids[product_id]
            previous_product_variants = {variant['id']: variant for variant in previous_product['variants']}
            current_product_variants = {variant['id']: variant for variant in current_product['variants']}

            for variant_id, current_variant in current_product_variants.items():
                previous_variant = previous_product_variants[variant_id]
                if previous_variant['available'] == False and current_variant['available'] == True:
                        restocked_products.append(current_product)
                        for variant in current_product['variants']:
                            if variant['available'] == True:
                                available_product_size.append(
                                    {
                                        'id': product_id, 
                                        'available_size': [variant['option1'] for variant in current_product['variants'] if variant['available'] == True], 
                                        'variant_id': [variant['id'] for variant in current_product['variants'] if variant['available'] == True], 
                                        'title': current_product['title'],
                                        'image': current_product['images'][0]['src'],
                                        'price': current_product['variants'][0]['price']
                                    })


            
    debug_json(available_product_size)
    return new_products, restocked_products, available_product_size

def load_previous_products():
    if not os.path.exists(data_file_path):
        with open(data_file_path, 'w') as file:
            json.dump([], file)

    with open('atmos.json', 'r') as file:
        data = file.read()
        return json.loads(data)
    
def get_available_products(product_id, available_product_size):
    for product in available_product_size:
        if product['id'] == product_id:
            return product

def send_size_to_discord(product_sizes):
    if product_sizes == None:
        return
    
    product_title = product_sizes['title']
    product_image_url = product_sizes['image']
    product_price = product_sizes['price']
    product_size_url = []
    for i in range (len(product_sizes['available_size'])):
        product_size_url.append(f"[Size {product_sizes['available_size'][i]}](https://atmos.co.id/cart/{product_sizes['variant_id'][i]}:1)")

    product_size = '\n'.join(product_size_url)

    data = {
        'username': 'Atmos Scraper',
        'avatar_url': 'https://i.ibb.co/svSBg3Z/Screenshot-2022-06-07-115600.png',
        'embeds': [
            {
                'fields': [
                    {
                        'name': 'Available Sizes',
                        'value': product_size,
                        'inline': True
                    },
                    {
                        'name': 'Price',
                        'value': rupiah_format(float(product_price), True),
                        'inline': True
                    }
                ],
                'author': {
                    'name': product_title,
                },
                'thumbnail': {
                    'url': product_image_url
                },
                'footer': {
                    'text': 'Atmos Scraper'
                },
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
        ]
    }

    response = session.post(discord_webhook_url, json=data)
    if response.status_code == 204:
        print(f"Product {product_title} sent to Discord!")
    else:
        print(f"Terjadi kesalahan saat mengirim product {product_title} ke Discord!")
        print(response.text)

def scrap():
    while True:
        try:
            response = session.get(url)
            if response.status_code == 200:
                json_content = response.json()
                current_products = json_content['products']
                previous_products = load_previous_products()

                new_products, restocked_products, available_product_size = compare_products(previous_products, current_products)

                if len(new_products) > 0:
                    print('New products found!')
                    print('Sending to Discord...')
                    for product in new_products:
                        product_title = product['title']
                        product_url = f"https://atmos.co.id/products/{product['handle']}"
                        product_image_url = product['images'][0]['src']
                        product_price = product['variants'][0]['price']

                        data = {
                            'username': 'CuanCuanCuan',
                            'avatar_url': 'https://i.ibb.co/svSBg3Z/Screenshot-2022-06-07-115600.png',
                            'content': 'New Product!',
                            'embeds': [
                                {
                                    'title': 'Product Link',
                                    'url': product_url,
                                    'description': f"Price : {rupiah_format(float(product_price), True)}",
                                    'author': {
                                        'name': product_title
                                    },
                                    'image': {
                                        'url': product_image_url
                                    },
                                    "footer": {
                                        "text": "PutuBot"
                                    },
                                    "timestamp": "2023-05-23"
                                }
                            ]
                        }

                        response = session.post(discord_webhook_url, json=data)
                        if response.status_code == 204:
                            print(f"Product {product_title} sent to Discord!")
                        else:
                            print(f"Terjadi kesalahan saat mengirim product {product_title} ke Discord:", response.status_code)
                        
                        send_size_to_discord(get_available_products(product['id'], available_product_size))
                        time.sleep(3)

                if len(restocked_products) > 0:
                    print('Restocked products found!')
                    print('Sending to Discord...')
                    for product in new_products:
                        product_title = product['title']
                        product_url = f"https://atmos.co.id/products/{product['handle']}"
                        product_image_url = product['images'][0]['src']
                        product_price = product['variants'][0]['price']

                        data = {
                            'username': 'CuanCuanCuan',
                            'avatar_url': 'https://i.ibb.co/svSBg3Z/Screenshot-2022-06-07-115600.png',
                            'content': 'New Product!',
                            'embeds': [
                                {
                                    'title': 'Product Link',
                                    'url': product_url,
                                    'description': f"Price : {rupiah_format(float(product_price), True)}",
                                    'author': {
                                        'name': product_title
                                    },
                                    'image': {
                                        'url': product_image_url
                                    },
                                    "footer": {
                                        "text": "PutuBot"
                                    },
                                    "timestamp": "2023-05-23"
                                }
                            ]
                        }

                        response = session.post(discord_webhook_url, json=data)
                        if response.status_code == 204:
                            print(f"Product {product_title} sent to Discord!")
                        else:
                            print(f"Terjadi kesalahan saat mengirim product {product_title} ke Discord:", response.status_code)
                        
                        send_size_to_discord(get_available_products(product['id'], available_product_size))
                        time.sleep(3)

                save_product_data(current_products)

            else:
                print('Terjadi kesalahan saat fetching:', response.status_code)

            time.sleep(3)  # 3-second delay before making the next request

        except requests.exceptions.RequestException as e:
            print('Terjadi kesalahan saat melakukan request:', str(e))

def run_with_proxy():
    global session
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

    session.proxies.update(proxies)
    scrap()

def main():
    print("1. Run with Proxy")
    print("2. Run without Proxy")
    option = input("Pilih opsi: ")

    if option == "1":
        run_with_proxy()
    elif option == "2":
        scrap()
    else:
        print("Opsi yang Anda pilih tidak valid.")

if __name__ == '__main__':
    main()