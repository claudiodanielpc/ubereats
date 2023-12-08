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



def zip_code(zip_code:str):
    url="https://www.ubereats.com/category-feed/Shop?mod=locationManager&modctx=feed&next=%2Fcategory-feed%2FShop%3Fpl%3DJTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%253D%26ps%3D1%26sc%3DSHORTCUTS&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%3D&ps=1&sc=SHORTCUTS"
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    try:
        # Wait for the input element to be clickable
        control_direct = wait.until(
            EC.element_to_be_clickable((By.ID, "location-typeahead-location-manager-input"))
        )
        
        # Clear the input field if needed
        control_direct.clear()    # Type the address
        cp=zip_code
        control_direct.send_keys(cp)
        time.sleep(3)
        control_direct.send_keys(Keys.RETURN)
    except Exception as e:
        print("Error:", e)
    time.sleep(3)

    #Ahora visitar la página de grocery
    grocery="https://www.ubereats.com/category-feed/Grocery?stores=all"
    driver.get(grocery)
    time.sleep(3)
    #Obtener html
    html = driver.page_source
    sopa=BeautifulSoup(html, 'html.parser')
    store_links = sopa.find_all('a', {'data-testid': 'store-card'})
    stores = [{'name': link.find('h3').get_text(), 'url': link['href']} for link in store_links]
    df_stores=pd.DataFrame(stores)
    #Dejar lo que está después de /store/ y antes del segundo /
    #Hacer copia de de url
    df_stores['sucursal']=df_stores['url'].copy()
    df_stores['sucursal']=df_stores['sucursal'].str.split('/store/').str[1]
    #Quitar lo que está después del segundo /
    df_stores['sucursal']=df_stores['sucursal'].str.split('/').str[0]
    #Eliminar "-" y reemplazar por espacio
    df_stores['sucursal']=df_stores['sucursal'].str.replace('-',' ')
    #Completar la url
    df_stores['url']='https://www.ubereats.com'+df_stores['url']
    #Dejar solo si contienen la palabra "Soriana", "Sumesa","City Market", "Comer", "Chedraui"
    df_stores=df_stores[df_stores['name'].str.contains('Soriana|Sumesa|City Market|Comer|Chedraui')]
    #Añadir columna de búsqueda de código postal
    df_stores['cp']=cp
    return df_stores