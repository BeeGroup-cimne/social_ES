import datetime
from geopandas import gpd
import pytz
from utils_ import *

# Define the ingestors

ingestors = {
    "OpenDataBCN": {
        "BaseURL": "https://opendata-ajuntament.barcelona.cat/data/api/action/",
        "Token": "14c6d53db904d7ded31e5243f95fa2b3d4c2972857c67e0a6fe961bb9ac68e7c"
    },
    "INERentalDistributionAtlas": {
        "DataFrame": INERentalDistributionAtlas(municipality_code="08019")
    },
    "INEHouseholdsRentalPriceIndex": {
        "https://www.ine.es/jaxiT3/files/t/es/csv_bd/59061.csv?nocab=1"
    },
    # "INEEssentialCharacteristicsOfPopulationAndHouseholds": {
    #     "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177092&menu=resultados&idp=1254735572981#!tabs-1254736195788"
    # },
    "INEIndexOfPrices": {
        "https://www.ine.es/jaxiT3/files/t/es/csv_bd/23708.csv?nocab=1"
    }
}


# Read the possible datasets available in Open Data Barcelona

ODBCN = requests.get(url=f"{ingestors['OpenDataBCN']['BaseURL']}/package_search?rows=1000",
                        headers = {'Authorization': f"TOK:{ingestors['OpenDataBCN']['Token']}"})
ingestors["OpenDataBCN"]["AllDatasets"] = ODBCN.json()["result"]["results"]

# Relate the neighborhood with section code in the INE Rental Distribution Atlas
ds_meta = [ds for ds in ingestors["OpenDataBCN"]["AllDatasets"]
           if ds['title_translated']['en'] == "Administrative units of the city of Barcelona"]
div_hash = [item["id"] for item in ds_meta[0]["resources"] if item["format"]=="JSON" and "SeccionsCensals" in item["name"]][0]
sections = requests.get(
    url=f"https://opendata-ajuntament.barcelona.cat/data/dataset/{ds_meta[0]['id']}/resource/{div_hash}/download",
    headers={"Authorization": f"TOK:{ingestors['OpenDataBCN']['Token']}"}).json()
sections_gpd = gpd.GeoDataFrame(sections)
sections_gpd.columns = ["District code", "Section code", "District name", "Geometry ETRS89", "Geometry WGS84", "Neighborhood name",
                        "AEB code", "Neighborhood code"]
pd.merge(ingestors["INERentalDistributionAtlas"]["DataFrame"]["District"], sections_gpd, )


# Define the gathering and harmonisation operations
ops = {
    "Population": [
        {
            "Ingestor": "OpenDataBCN",
            "Title": "Population by sex and age",
            "DiscreteColumnsToDimensions": {
                "Title": "Dimensions of the data sets of the Municipal Register of inhabitants of the city of Barcelona",
                "Column": "Desc_Dimensio",
                "Code": "Codi_Dimensio",
                "Dimension": "Desc_Valor_EN",
                "ColumnsToTransform": ["SEXE", "EDAT_1"]
            },
            "ColumnsRenameAndConcat": {
                "District code": ["Codi_Districte"],
                "Neighborhood code": ["Codi_Barri"],
                "Sex":  ["SEXE"],
                "DateStart": ["Data_Referencia"],
                "NumberOfPeople": ["Valor"],
                "Age": ["EDAT_1"]
            },
            "Transformation": {
                "DistrictId": {lambda x: f"{int(x):02}"},
                "NeighborhoodId": {lambda x: f"{int(x):02}"},
                "NumberOfPeople": {lambda x: int(x)},
                "DateStart": {lambda x: pytz.timezone("Europe/Madrid").localize(
                  datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%S")).astimezone(pytz.utc)}
            },
            "RowsConcatWithAggregatedResults": [
                {
                    "GroupBy": ["DistrictId","Sex","Age"],
                    "ValueFunc": [("NumberOfPeople","sum")]
                }
            ]
        }
    ]
}