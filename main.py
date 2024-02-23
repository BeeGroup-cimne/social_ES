import pandas as pd
import geopandas as gpd
import json
import config
import requests


if __name__ == "__main__":

    for gr in config.ops.keys():
        for op in config.ops[gr]:
            if op["Ingestor"] == "OpenDataBCN":
                name_ds = "Population by sex and age"
                ds_meta = [ds for ds in config.ingestors["OpenDataBCN"]["AllDatasets"]
                           if ds['title_translated']['en'] == op["Title"]][0]
                hashes = [item["id"] for item in ds_meta["resources"]]
                url = [requests.get(
                    url=f"https://opendata-ajuntament.barcelona.cat/data/api/action/datastore_search?resource_id={hash}",
                    headers={"Authorization": f"TOK:{config['OpenDataBCN']['Token']}"}).json() for hash in hashes]

                r = requests.get(
                    url='https://opendata-ajuntament.barcelona.cat/data/api/action/datastore_search?resource_id=b00be3f8-9328-4175-8689-24a25bc0907c',
                    headers={'Authorization': f"TOK:{config['OpenDataBCN']['Token']}"}).json()

            elif op["Ingestor"] == "INERentalDistributionAtlas":
                config.ingestors["INERentalDistributionAtlas"]["DataFrame"]

            #
