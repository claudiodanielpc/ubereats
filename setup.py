from setuptools import setup, find_packages

setup(
    name='ubereats',
    version='1.0',
    packages=find_packages(),
       install_requires=[
        'pandas',
        'geopandas',
        'bs4',
        'requests',
        'selenium',
        'setuptools',
        'shapely',
        'tqdm',
        'numpy',
    ],
    include_package_data=True, 
    url='https://github.com/claudiodanielpc/ubereats',
    author='Claudio Daniel Pacheco-Castro',
    author_email='claudio@comunidad.unam.mx')