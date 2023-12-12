import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

def search_products(mode, address, producto, url=None):
    # Set up the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-cache')
    options.add_argument('--disable-cookies')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 10)

    # Initialize lists to store data
    prod = []
    precios = []
    tienda = []
    sucursal = []
    df_basica=None
    df_avanzada=None
    if mode == 'basica' and url is None:
        # Navigate to the initial URL for basic mode
        basic_url = "https://www.ubereats.com/category-feed/Shop?mod=locationManager&modctx=feed&next=%2Fcategory-feed%2FShop%3Fpl%3DJTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%253D%26ps%3D1%26sc%3DSHORTCUTS&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkVqZSUyMHZpYWwlMjA0JTIwU3VyJTIwWG9sYSUyMDE5NSUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMmY0OGYwNmQ2LTcyMjEtNzk0ZS1lODE4LTI5NTIxY2JlN2NlMCUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJ1YmVyX3BsYWNlcyUyMiUyQyUyMmxhdGl0dWRlJTIyJTNBMTkuMzkzOSUyQyUyMmxvbmdpdHVkZSUyMiUzQS05OS4xMzg3MTQlN0Q%3D&ps=1&sc=SHORTCUTS"
        driver.get(basic_url)
        print("Buscando", producto, "en los supermercados de Uber Eats para la ubicación ", address,". Por favor espere⏳...")
        # Set the location
        try:
            control_direct = wait.until(
                EC.element_to_be_clickable((By.ID, "location-typeahead-location-manager-input"))
            )
            control_direct.clear()
            control_direct.send_keys(address)
            time.sleep(3)
            control_direct.send_keys(Keys.RETURN)
        except Exception as e:
            print("Error:", e)
            driver.quit()
            return
        time.sleep(3)

        # Navigate to the grocery page
        grocery = "https://www.ubereats.com/category-feed/Grocery?stores=all"
        driver.get(grocery)
        time.sleep(3)

        # Extract store links
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        store_links = soup.find_all('a', {'data-testid': 'store-card'})
        stores = [{'name': link.find('h3').get_text(), 'url': link['href']} for link in store_links]

        # DataFrame for stores
        df_stores = pd.DataFrame(stores)
        df_stores['sucursal'] = df_stores['url'].str.split('/store/').str[1].str.split('/').str[0].replace('-', ' ')
        df_stores['url'] = 'https://www.ubereats.com' + df_stores['url']
        df_stores['cp'] = address

        # Search for each product in every store
        for index, row in tqdm(df_stores.iterrows(), total=df_stores.shape[0], desc="Recolectando productos y precios😊"):
            store_url = row['url']
            store_name = row['name']
            store_sucursal = row['sucursal']
            driver.get(store_url)
            time.sleep(3)
            # Search for the product
           
            try:
                product_search = driver.find_element(By.ID, "search-suggestions-typeahead-input")
                product_search.clear()
                product_search.send_keys(producto)
                time.sleep(3)
                product_search.send_keys(Keys.ENTER)
                time.sleep(3)

                # Extract product info
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                product_items = soup.find_all('div', attrs={'data-testid': lambda value: value and value.startswith('store-menu-item')})
            
                for item in product_items:
                    # Extract rich-text elements, which should contain the price and product name
                    rich_texts = item.find_all('span', {'data-testid': 'rich-text'})
                    if len(rich_texts) >= 2:
                        try:
                            price = rich_texts[0].get_text(strip=True)
                            prod_name = rich_texts[1].get_text(strip=True)
                            prod.append(prod_name)
                            precios.append(price)
                            tienda.append(store_name)
                            sucursal.append(store_sucursal)
                        except Exception as e:
                            print(f"Error extracting data for store: {store_name} - {e}")
                            prod.append(None)
                            precios.append(None)
                            tienda.append(store_name)
                            sucursal.append(store_sucursal)
                    else:
                        prod.append(None)
                        precios.append(None)
                        tienda.append(store_name)
                        sucursal.append(store_sucursal)
            except Exception as e:
                print(f"Producto no encontrado en tienda {store_name}")

        df_basica=pd.DataFrame({'producto': prod,'precio': precios,'tienda': tienda, 'sucursal':sucursal,'fecha_consulta': pd.to_datetime('today')})
        df_basica["precio"] = df_basica["precio"].str.replace("MX$", "").str.replace(",", "")
        try:
            df_basica[["precio", "unidad"]] = df_basica["precio"].str.split("/", expand=True)
        except:
            pass
        df_basica["precio"] = pd.to_numeric(df_basica["precio"], errors='coerce')
        df_basica['producto'] = df_basica['producto'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        #Eliminar guiones de sucursal
        df_basica['sucursal']=df_basica['sucursal'].str.replace('-',' ')
        #Agregar busqueda
        df_basica['busqueda']=producto



    elif mode == 'avanzada' and url is not None:
        # Open the provided URL for advanced mode
        driver.get(url)
        print("Buscando ", producto, " en el supermercado, por favor espere⏳...")
        time.sleep(3)



        #Dirección
        control_direct = wait.until(EC.element_to_be_clickable((By.ID, "location-typeahead-location-manager-input")))
        control_direct.clear()
        #Usar códigos postales de la df de supermercados
        control_direct.send_keys('06720 cdmx')
        time.sleep(3)
        control_direct.send_keys(Keys.RETURN)
        time.sleep(3)

        try:
            product_search = driver.find_element(By.ID, "search-suggestions-typeahead-input")
            product_search.clear()
            product_search.send_keys(producto)
            time.sleep(3)
            product_search.send_keys(Keys.ENTER)
            time.sleep(10)

            # Get the HTML of the page and parse it with BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            #product_items = soup.find_all('li', class_=lambda value: value and value.startswith("g1"))
            product_items = soup.find_all('div', attrs={'data-testid': lambda value: value and value.startswith('store-menu-item')})
            for item in tqdm(product_items, total=len(product_items), desc="Recolectando productos y precios😊"):
                rich_texts = item.find_all('span', {'data-testid': 'rich-text'})

                if len(rich_texts) >= 2:
                    try:
                        price = rich_texts[0].get_text(strip=True)
                        if "•" in rich_texts[1].text:
                            prod_name = rich_texts[3].get_text(strip=True)
                        else:
                            prod_name = rich_texts[1].get_text(strip=True)
                        prod.append(prod_name)
                        precios.append(price)
                    except Exception as e:
                        print(f"Producto no encontrado en tienda")
                        prod.append(None)
                        precios.append(None)
                else:
                    prod.append(None)
                    precios.append(None)

        except Exception as e:
            print(f"Producto no encontrado en tienda")


   

        # Create DataFrame from collected data
        df_avanzada = pd.DataFrame({
            'producto': prod,
            'precio': precios,
            'fecha_consulta': pd.to_datetime('today')})
        df_avanzada["producto"]=df_avanzada["producto"].astype(str)
        df_avanzada['producto'] = df_avanzada['producto'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        df_avanzada['sucursal'] = url.split('/store/')[1].split('/')[0].replace('-', ' ')
        df_avanzada['precio'] = df_avanzada['precio'].astype(str)
        df_avanzada["precio"]=df_avanzada["precio"].str.replace("MX$","")
        #Eliminar comas
        df_avanzada["precio"]=df_avanzada["precio"].str.replace(",","")
        #Split columna de precio en dos columnas si tiene "/"
        try:
            df_avanzada[["precio","unidad"]]=df_avanzada["precio"].str.split("/",expand=True)
        except:
            pass

        #Transformar columna de precio a float
        df_avanzada["precio"]=pd.to_numeric(df_avanzada["precio"])
        #Agregar busqueda
        df_avanzada['busqueda']=producto
    else:
        print("En el modo 'basica' no se puede ingresar una URL. Si intenta con el modo avanzada, es necesaria la url. Por favor intente de nuevo.")
        driver.quit()
        return None

    driver.quit()
    if mode == 'basica':
        return df_basica
    elif mode == 'avanzada':
        return df_avanzada