from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import random
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')


def find_best_price(product_data):
    best_price = float('inf')
    best_site = None

    for product in product_data:
        if product["price"] != "Not found":
            try:
                price = float(product["price"].strip('$').replace(',', ''))
                if price < best_price:
                    best_price = price
                    best_site = product["site"]
            except ValueError:
                # Handle case where conversion to float fails
                continue

    return best_site, best_price if best_price != float('inf') else "Not available"


@app.route('/scrape', methods=['POST'])
def scrape():
    print("called")
    url = request.form['url']

    product_data = []



#REQUEST AND AMAZON

    #Based off listing https://www.amazon.com/Tide-Eliminators-Laundry-Detergent-Invisible/dp/B0B1VVM7WF/ref=sr_1_2_sspa?crid=122CYK0C3S3WT&keywords=tide+pods&qid=1702095566&rdc=1&s=gift-cards&sprefix=tide+pod%2Cgift-cards%2C102&sr=1-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the URL
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    title_element = soup.find(id='productTitle')
    if title_element:
        title = title_element.get_text().strip()
        print("Title:", title)
    else:
        print("Title not found")

    price_whole_element = soup.find('span', class_='a-price-whole')
    price_fraction_element = soup.find('span', class_='a-price-fraction')
    
    if price_whole_element:
        price_whole = price_whole_element.get_text().strip()
        price_fraction = price_fraction_element.get_text().strip() if price_fraction_element else '00'
        price = f"${price_whole}{price_fraction}"
        print("Price:", price)
    else:
        print("Price not found")

    amazon_data = {
        "site": "Amazon",
        "link": url,
        "price": price if price_whole_element else "Not found"
    }
    product_data.append(amazon_data)


#WALMART
    #Search google for the Walmart link!
    search_query = "Walmart " + title
    driver.get("https://www.google.com")

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find the first Walmart link
    #time.sleep(random.uniform(2,4))
    walmart_link = soup.find('a', href=lambda href: href and "walmart.com" in href)
    if walmart_link:
        print("Walmart link found:", walmart_link['href'])
    else:
        print("Walmart link not found")

    

    # Open the Walmart html file of listing

    file_path="sites/Walmart.html"

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Extract price
    price_element = soup.find('span', {'itemprop': 'price'})
    if price_element:
        price = price_element.get_text().strip()
        print("walmart's Price:", price)
    else:
        print("Price not found")

    walmart_data = {
        "site": "Walmart",
        "link": walmart_link['href'] if walmart_link else "Not found",
        "price": price if price_element else "Not found"
    }
    product_data.append(walmart_data)


#LOWES
    #Search google for the Lowes link!
    search_query = "Lowes " + title
    driver.get("https://www.google.com")

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find the first Lowes link
    #time.sleep(random.uniform(2,4))
    Lowes_link = soup.find('a', href=lambda href: href and "lowes.com" in href)
    if Lowes_link:
        print("Lowes link found:", Lowes_link['href'])
    else:
        print("Lowes link not found")

    # Open the Lowes  html file of listing

    file_path="sites/Lowes.html"

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    price_div = soup.find('div', class_="main-price undefined split split-left")

    if price_div:
        # Find the dollar and cent span elements
        dollar_span = price_div.find('span', class_="item-price-dollar")
        cent_span = price_div.find('span', class_="PriceUIstyles__Cent-sc-14j12uk-0 bktBXX item-price-cent")

        # Extract text and concatenate
        dollar = dollar_span.get_text() if dollar_span else '$0'
        cent = cent_span.get_text().strip() if cent_span else '.00'

        price = f"{dollar}{cent}"
        print("Lowes Price:", price)
    else:
        print("Price element not found")
    lowes_data = {
        "site": "Lowes",
        "link": Lowes_link['href'] if Lowes_link else "Not found",
        "price": price if price_div else "Not found"
    }
    product_data.append(lowes_data)



#MEIJER
    #Search google for the Meijer link!
    search_query = "Meijer " + title
    driver.get("https://www.google.com")

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find the first Lowes link
    #time.sleep(random.uniform(2,4))
    meijer_link = soup.find('a', href=lambda href: href and "meijer.com" in href)
    if meijer_link:
        print("Meijer link found:", meijer_link['href'])
    else:
        print("meijerlink not found")


    meijer_file_path = "sites/Meijer.html" 

    if os.path.exists(meijer_file_path):
        with open(meijer_file_path, 'r', encoding='utf-8') as file:
            meijer_content = file.read()

        meijer_soup = BeautifulSoup(meijer_content, 'html.parser')

        # Extract price
        price_element = meijer_soup.find('span', class_='product-info__standard-price')
        if price_element and price_element.span:
            meijer_price = price_element.span.get_text().strip()
            print("Meijer Price:", meijer_price)
        else:
            print("Meijer Price not found")
    else:
        print(f"File not found at {meijer_file_path}")
    
    meijer_data = {
        "site": "Meijer",
        "link": meijer_link['href'] if meijer_link else "Not found",
        "price": meijer_price if price_element else "Not found"
    }
    product_data.append(meijer_data)

    best_site, best_price = find_best_price(product_data)
    best_price_info = {
        "site": best_site,
        "price": f"${best_price}" if best_price != "Not available" else best_price
    }

    # Close the browser
    driver.quit()
    print(product_data)
    return render_template('results.html', data=product_data, best_price=best_price_info)

if __name__ == '__main__':
    app.run(debug=True)
