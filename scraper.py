import requests
from bs4 import BeautifulSoup
import json
from tabulate import tabulate
import time

def scrape_products():
    base_url = "https://books.toscrape.com"
    url = base_url
    products = []
    page_count = 0
    max_pages = 2
    
    while url and page_count < max_pages:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() 
            
            soup = BeautifulSoup(response.content.decode('utf-8', errors='replace'), 'html.parser')
            book_listings = soup.select('article.product_pod')
            
            for book in book_listings:
                title = book.h3.a['title']
                price_str = book.select_one('p.price_color').text
                price_gbp = float(price_str.replace('£', ''))
                products.append({
                    'name': title,
                    'price_gbp': price_gbp
                })
            
            # Pagination: Get next page URL
            next_button = soup.select_one('li.next > a')
            url = f"{base_url}/{next_button['href']}" if next_button else None
            page_count += 1
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping page: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
            
    return products

def get_exchange_rate():
    api_key = "491da7f3c51c72bbab3262ff"
    api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/GBP"
    max_retries = 3
    wait_time = 2  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['conversion_rates']['KES']
        except requests.exceptions.RequestException as e:
            print(f"API Error (Attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(wait_time)
            wait_time *= 2
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Data parsing error: {e}")
            break
    return None


if __name__ == "__main__":
    products = scrape_products()
    if not products:
        print("No products scraped. 🤔Exiting.")
        exit()
        
    exchange_rate = get_exchange_rate()
    if exchange_rate is None:
        print("Failed to get exchange rate. 😭Exiting.")
        exit()
        
    # Add converted prices
    for product in products:
        product['price_kes'] = round(product['price_gbp'] * exchange_rate, 2)
    
    # Save to JSON
    try:
        with open('products.json', 'w') as f:
            json.dump(products, f, indent=2)
        print("Data saved to products.json🎉")
    except IOError as e:
        print(f"Error saving JSON file: {e}😭")
    
    # Display table
    table_data = []
    for idx, product in enumerate(products[:10], start=1):
        table_data.append([
            idx,
            product['name'][:50] + '...' if len(product['name']) > 50 else product['name'],
            # f"£{product['price_gbp']:.2f}",
            f"KES {product['price_kes']:,.2f}"
        ])

    headers = ["#", "Name", "Price (KES)"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))