import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import requests
import random
from bs4 import BeautifulSoup
import tqdm
import googlemaps
import geopandas as gpd
from shapely import wkt


options = webdriver.ChromeOptions()
#Incognito
options.add_argument('--incognito')
options.add_argument('--headless')


def buscador(tipo_busqueda, adress, producto):
    options = webdriver.ChromeOptions()
    # You can set Chrome options here if needed
    driver = webdriver.Chrome(options=options)

    if tipo_busqueda == "básica":
        
        url="https://www.ubereats.com/category-feed/Shop?mod=locationManager&modctx=feed&next=%2Fcategory-feed%2FShop%3Fpl%3DJTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%253D%26ps%3D1%26sc%3DSHORTCUTS&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%3D&ps=1&sc=SHORTCUTS"
        driver.get(url)
        try:
            wait = WebDriverWait(driver, 10)
            control_direct = wait.until(
                EC.element_to_be_clickable((By.ID, "location-typeahead-location-manager-input"))
            )
            control_direct.clear()
            cp=adress
            control_direct.send_keys(adress)
            time.sleep(3)
            control_direct.send_keys(Keys.RETURN)
        except Exception as e:
            print("Error:", e)
            driver.quit()
            return pd.DataFrame()  # Return empty dataframe on failure

        time.sleep(3)
        grocery="https://www.ubereats.com/category-feed/Grocery?stores=all"
        driver.get(grocery)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        store_links = soup.find_all('a', {'data-testid': 'store-card'})
        stores = [{'name': link.find('h3').get_text(), 'url': link['href']} for link in store_links]

        df_stores = pd.DataFrame(stores)
        df_stores = pd.DataFrame([{'name': adress.split('/')[-1].replace('-', ' '), 'url': adress}])

    # The following code is common for both basic and advanced searches
    prod, precios, tienda, sucursal = [], [], [], []
    for index, row in df_stores.iterrows():
        driver.get(row['url'])
        time.sleep(3)

        try:
            product_search = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-suggestions-typeahead-input"))
            )
            product_search.clear()
            product_search.send_keys(producto)
            time.sleep(3)
            product_search.send_keys(Keys.ENTER)
            time.sleep(3)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            product_items = soup.find_all('div', attrs={'data-testid': lambda value: value and value.startswith('store-menu-item')})
            
            for item in product_items:
                rich_texts = item.find_all('span', {'data-testid': 'rich-text'})
                if len(rich_texts) >= 2:
                    price = rich_texts[0].get_text(strip=True)
                    prod_name = rich_texts[1].get_text(strip=True)
                    prod.append(prod_name)
                    precios.append(price)
                    tienda.append(row['name'])
                    sucursal.append(row['url'].split('/')[-2].replace('-', ' '))
                else:
                    prod.append(None)
                    precios.append(None)
                    tienda.append(row['name'])
                    sucursal.append(row['url'].split('/')[-2].replace('-', ' '))
        except Exception as e:
            print(f"Error on product search in store: {row['name']} - {e}")

    driver.quit()
    df = pd.DataFrame({'producto': prod, 'precio': precios, 'tienda': tienda, 'sucursal': sucursal})
    df['producto'] = df['producto'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    return df




# def buscador(tipo_busqueda:"básica",adress:str,producto:str):
#     if tipo_busqueda=="básica":
#         url="https://www.ubereats.com/category-feed/Shop?mod=locationManager&modctx=feed&next=%2Fcategory-feed%2FShop%3Fpl%3DJTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%253D%26ps%3D1%26sc%3DSHORTCUTS&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%3D&ps=1&sc=SHORTCUTS"
#         driver = webdriver.Chrome(options=options)
#         wait = WebDriverWait(driver, 10)
#         driver.get(url)
#         try:
#             # Wait for the input element to be clickable
#             control_direct = wait.until(
#                 EC.element_to_be_clickable((By.ID, "location-typeahead-location-manager-input"))
#             )
            
#             # Clear the input field if needed
#             control_direct.clear()    # Type the address
#             cp=adress
#             control_direct.send_keys(cp)
#             time.sleep(3)
#             control_direct.send_keys(Keys.RETURN)
#         except Exception as e:
#             print("Error:", e)
#         time.sleep(3)

#         #Ahora visitar la página de grocery
#         grocery="https://www.ubereats.com/category-feed/Grocery?stores=all"
#         driver.get(grocery)
#         time.sleep(3)
#         #Obtener html
#         html = driver.page_source
#         sopa=BeautifulSoup(html, 'html.parser')
#         store_links = sopa.find_all('a', {'data-testid': 'store-card'})
#         stores = [{'name': link.find('h3').get_text(), 'url': link['href']} for link in store_links]
#         df_stores=pd.DataFrame(stores)
#         #Dejar lo que está después de /store/ y antes del segundo /
#         #Hacer copia de de url
#         df_stores['sucursal']=df_stores['url'].copy()
#         df_stores['sucursal']=df_stores['sucursal'].str.split('/store/').str[1]
#         #Quitar lo que está después del segundo /
#         df_stores['sucursal']=df_stores['sucursal'].str.split('/').str[0]
#         #Eliminar "-" y reemplazar por espacio
#         df_stores['sucursal']=df_stores['sucursal'].str.replace('-',' ')
#         #Completar la url
#         df_stores['url']='https://www.ubereats.com'+df_stores['url']
#         #Dejar solo si contienen la palabra "Soriana", "Sumesa","City Market", "Comer", "Chedraui"
#         df_stores=df_stores[df_stores['name'].str.contains('Soriana|Sumesa|City Market|Comer|Chedraui')]
#         #Añadir columna de búsqueda de código postal
#         df_stores['cp']=cp
#         # Initialize lists to store data
#         prod = []
#         precios = []
#         tienda = []
#         sucursal = []

# # DataFrame of stores (assuming df_stores is predefined with columns 'url', 'name', 'sucursal')

#         # Search products in each store
#         for index, row in df_stores.iterrows():
#             for producto in productos:  # This loop was missing
#                 print("Busca producto", producto, "en", row['sucursal'])
#                 url = row['url']
#                 store_name = row['name']
#                 store_sucursal = row['sucursal']
#                 driver.get(url)

#                 # Allow time for the page to load
#                 time.sleep(3)
                
#                 # Find the product search input field and enter the product name
#                 product_search = driver.find_element(By.ID, "search-suggestions-typeahead-input")
#                 product_search.clear()
#                 product_search.send_keys(producto)
#                 time.sleep(3)
#                 product_search.send_keys(Keys.ENTER)
                
#                 # Allow time for the search results to load
#                 time.sleep(3)
                
#                 # Get the HTML of the page and parse it with BeautifulSoup
#                 html = driver.page_source
#                 soup = BeautifulSoup(html, 'html.parser')
#                 product_items = soup.find_all('div', attrs={'data-testid': lambda value: value and value.startswith('store-menu-item')})
                
#                 for item in product_items:
#                     # Extract rich-text elements, which should contain the price and product name
#                     rich_texts = item.find_all('span', {'data-testid': 'rich-text'})
#                     if len(rich_texts) >= 2:  # Make sure there are at least two rich-text elements
#                         try:
#                             price = rich_texts[0].get_text(strip=True)
#                             prod_name = rich_texts[1].get_text(strip=True)
#                             prod.append(prod_name)
#                             precios.append(price)
#                             tienda.append(store_name)
#                             sucursal.append(store_sucursal)
#                         except Exception as e:
#                             print(f"Error extracting data for store: {store_name} - {e}")
#                             prod.append(None)
#                             precios.append(None)
#                             tienda.append(store_name)
#                             sucursal.append(store_sucursal)
#                     else:
#                         # If not enough span elements found, append None values
#                         prod.append(None)
#                         precios.append(None)
#                         tienda.append(store_name)
#                         sucursal.append(store_sucursal)
#         df = pd.DataFrame({'producto': prod, 'precio': precios, 'tienda': tienda, 'sucursal': sucursal, 'direccion_busca': cp,'fecha_consulta':pd.to_datetime('today')})
#             #Todo a minúsculas
#         df['producto']=df['producto'].str.lower()
#             #Quitar acentos
#         df['producto']=df['producto'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
#     return df