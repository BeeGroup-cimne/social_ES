import utils_INE
# from utils_OpenDataBCN import *
from yaml import safe_load as yload
import os


with open(f'collections.yaml','r') as f:
    data = yload(f)


def available_collections():
    collections = [collection for source in data.keys() for collection in data[source].keys()]
    for collection in collections:
        print(collection)

    return collections


def retrieve_data(collection, years, municip):
    
    return dfs


def download(wd='data',collections=None,years=None,municip=None,fg=False):
    if collections == None:
        collections = available_collections()

    for collec in collections:
        path = f"{wd}/{collec}/"
        if fg:
            try:
                os.removedirs(path)
            except FileNotFoundError:
                pass

        os.makedirs(path,exist_ok=True)
        func = getattr(utils_INE,collec)
        df = func(path=path,municipality_code=municip,years=years)
        with open(f'output2.txt', 'w',) as f :
            f.write(json.dumps(df))
        print(df)


download(collections=['INEPopulationAnualCensus'])