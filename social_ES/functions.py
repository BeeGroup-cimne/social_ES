import utils_INE
# from utils_OpenDataBCN import *
from yaml import safe_load as yload
import shutil, os


with open(f'collections.yaml','r') as f:
    data = yload(f)


def available_collections():
    collections = [collection for source in data.keys() for collection in data[source].keys()]
    print(','.join(collections))

    return collections


def info_collections(collections=None):
    if collections == None:
        collections = available_collections()
        
    for source in data.keys():
        for collection in data[source].keys():
            if collection in collections:
                print(collection)
                for item, info in data[source][collection].items():
                    print(f"\t- {item}: {info}")
    

def download(wd='data',collections=None,years=None,municip=None,fg=False):
    if collections == None:
        collections = available_collections()

    results = [None] * len(collections)
    for idx, collec in enumerate(collections):
        path = f"{wd}/{collec}/"
        if fg:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass

        os.makedirs(path,exist_ok=True)
        func = getattr(utils_INE,collec)
        results[idx] = func(path=path,municipality_code=municip,years=years)
    
    return results


available_collections()
info_collections(collections=['INERentalDistributionAtlas'])
res = download(collections=['INERentalDistributionAtlas'],years=['2021'],fg=False)
res[0]['Sections'].to_csv("test0_munic.csv",index=False)
