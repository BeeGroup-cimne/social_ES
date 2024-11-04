import os 

def create_dirs(data_dir):
    os.makedirs(census_tracts_dir(data_dir), exist_ok=True)
    os.makedirs(districts_dir(data_dir), exist_ok=True)
    os.makedirs(cadaster_dir(data_dir), exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/buildings", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/buildings/zip", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/buildings/unzip", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/address", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/address/zip", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/address/unzip", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/parcels", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/parcels/zip", exist_ok=True)
    os.makedirs(f"{cadaster_dir(data_dir)}/parcels/unzip", exist_ok=True)
    os.makedirs(results_dir(data_dir), exist_ok=True)
    os.makedirs(DEM_raster_dir(data_dir), exist_ok=True)
    os.makedirs(f"{DEM_raster_dir(data_dir)}/raw", exist_ok=True)
    os.makedirs(f"{DEM_raster_dir(data_dir)}/uncompressed", exist_ok=True)
    os.makedirs(neighborhoods_dir(data_dir), exist_ok=True)
    os.makedirs(postal_codes_dir(data_dir), exist_ok=True)
    os.makedirs(f"{postal_codes_dir(data_dir)}/raw", exist_ok=True)
    os.makedirs(open_data_dir(data_dir), exist_ok=True)

