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

    while page_count < max_pages:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        product_cards = soup.find_all("article", class_="product_pod")

        for card in product_cards:
            title = card.h3.a.attrs['title']
            price_str = card.select_one('p.price_color').text
            price = float(price_str.replace('£', ''))
            availability = card.select_one('p.availability').text.strip()
            products.append({
                'title': title,
                'price': price,
                'availability': availability,
            })

# Pagination: Get next page URL
            next_button = soup.select_one('li.next > a')
            url = f"{base_url}/{next_button['href']}" if next_button else None
            page_count += 1
            time.sleep(1)  # Be polite between requests
            
        # except requests.exceptions.RequestException as e:
        #     print(f"Error scraping page: {e}")
        #     break
        # except Exception as e:
        #     print(f"Unexpected error: {e}")
        #     break
            
    return products

# Get GBP to KES exchange rate with retries
def get_exchange_rate():
    api_url = "https://open.er-api.com/v6/latest/GBP"
    max_retries = 3
    wait_time = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['rates']['KES']
        except requests.exceptions.RequestException as e:
            print(f"API Error (Attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(wait_time)
            wait_time *= 2
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Data parsing error: {e}")
            break
    return None

