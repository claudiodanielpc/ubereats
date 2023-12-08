from setuptools import setup, find_packages

setup(
    name='marketscraper',
    version='1.0',
    packages=find_packages(),
       install_requires=[
        'pandas',
        'bs4',
        'requests',
        'selenium',
        'unidecode',
        'cachecontrol',
        'numpy',
    ],
    include_package_data=True, 
    url='https://github.com/labdatos-se/marketscraper',
    author='Claudio Daniel Pacheco-Castro',
    author_email='claudio@comunidad.unam.mx')