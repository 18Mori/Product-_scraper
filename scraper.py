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


