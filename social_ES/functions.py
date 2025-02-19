from social_ES import utils_INE
from social_ES import utils_OpenDataBCN
from importlib import resources
from yaml import safe_load as yload
import shutil
import os

# Carga los datos del archivo collections.yaml
with resources.open_text('social_ES', 'collections.yaml') as inp_file:
    data = yload(inp_file)

def available_collections(output=True):
    """
    Retorna una lista de todas las colecciones disponibles.

    :param output: Si es True, imprime las colecciones.
    :return: Lista de colecciones disponibles.
    """
    collections = [collection for source in data.keys() for collection in data[source].keys()]
    if output:
        print(','.join(collections))
    return collections

def info_collections(collections=None):
    """
    Imprime información sobre las colecciones especificadas.

    :param collections: Lista de colecciones para mostrar información. Si es None, muestra todas.
    """
    if collections is None:
        collections = available_collections(output=False)
        
    for source in data.keys():
        for collection in data[source].keys():
            if collection in collections:
                for item, info in data[source][collection].items():
                    print(f"\t- {item}: {info}")

def download(wd='data', collections=None, years=None, municip=None, update=False):
    """
    Descarga los datos para las colecciones especificadas.

    :param wd: Directorio de trabajo donde se guardarán los datos.
    :param collections: Lista de colecciones a descargar.
    :param years: Lista de años para los cuales se descargarán los datos.
    :param municip: Lista de códigos de municipios.
    :param update: Si es True, actualiza los datos existentes.
    :return: Lista de resultados de la descarga.
    """
    if collections is None:
        collections = available_collections(output=False)

    results = [None] * len(collections)
    for idx, collec in enumerate(collections):
        path = os.path.join(wd, collec)
        if update:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass

        os.makedirs(path, exist_ok=True)
        func = getattr(utils_INE, collec)
        try:
            results[idx] = func(path=path, municipality_code=municip, years=years)
        except Exception as e:
            print(f"Error al descargar la colección {collec}: {e}")
    
    return results

# Ejemplos de uso:
# collections = available_collections()
# res = download(collections=collections, municip=['02003'], years=[2021, 2019], update=False)
# res[0]['Sections'].to_csv("test0_munic.csv", index=False)  # Sections
# res[1]['Sections'].to_csv("test1_munic.csv", index=False)  # INEPopulationAnualCensus
# res[2]['Province'].to_csv("test2_munic.csv", index=False)
# res[3]['Districts'].to_csv("test3_munic.csv", index=False)
# res[4]['Municipality'].to_csv("test4_munic.csv", index=False)  # OK districts and Year
# res[5]['National'].to_csv("test5_munic.csv", index=False)  # OK National and Year
# res[6]['Sections'].to_csv("test6_munic.csv", index=False)

# res = download(collections=['INEPopulationAnualCensus'], municip=['02003'], years=['2022', '2019'], update=True)
