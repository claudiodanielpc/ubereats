# ubereats 🛒
 


Paquete para obtener precios de productos en supermercados🛒 que cuenten con convenio con Ubereats en México. Solo necesitas una dirección o código postal y un producto para empezar a buscar😊

Si bien UberEats está constituido por la parte de comida, restaurantes y recientemente, supermercados, este paquete está diseñado para obtener información en supermercados. 

## Instalación🚀

Para poder utilizar la librería, se debe correr desde la terminal el siguiente comando:

```python
pip install git+https://github.com/claudiodanielpc/ubereats.git
```

## Ejemplos de uso

Se cuenta con una función única llamada search_products. Esta función tiene dos modos: básica y avanzada. La primera únicamente requiere de alguna ubicación o código postal y el producto para funcionar. El modo avanzada requiere, además de esto, una url de alguna tienda en particular para obtener la información. 


### Búsqueda básica
```python
import ubereats as ue

ue.search_products(mode="basica",address="06720 mx", producto="manzana")
```


![image](https://github.com/claudiodanielpc/ubereats/assets/61884019/f675b61f-8661-4bab-bc0c-46c176d3ea02)


En este ejemplo, le pedimos a UberEats datos de manzana para las tiendas que estén cerca o atiendan en el código postal 06720 de la Ciudad de México. El 13 en la barra de progreso corresponde al número de establecimientos que se encontraron para el código postal ingresado.
Si se dan cuenta, vienen algunos productos que no son precisamente manzana pero esa limpieza ya es trabajo de quien procese y analice los datos.


### Búsqueda avanzada
En el caso de la búsqueda avanzada, esta se realiza sobre una url en particular; es decir, sobre una tienda en específico.

```python
import ubereats as ue

ue.search_products(mode="avanzada",address="06720 mx", producto="manzana", url="https://www.ubereats.com/store/soriana-hiper-parque-delta/m8xvqtiuU6Ki9rJ56qAhYQ")
```

![image](https://github.com/claudiodanielpc/ubereats/assets/61884019/0a366fb0-5c92-4b66-93f8-a72db99a9e05)

En este caso, la búsqueda de manzana se hizo específicamente en Soriana Parque Delta.
