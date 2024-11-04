from social_ES.utils_INE import *
from social_ES.utils_OpenDataBCN import *
from social_ES.utils import *

def get_colections():
    return """
        INERentalDistributionAtlas: https://www.ine.es/dyngs/INEbase/en/operacion.htm?c=Estadistica_C&cid=1254736177088&menu=ultiDatos&idp=1254735976608
        INEPopulationAnualCensus: https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176992&menu=resultados&idp=1254735572981
        INEHouseholdsPriceIndex: 
        INEAggregatedElectricityConsumption:
        INEHouseholdsRentalPriceIndex:
        INEConsumerPriceIndex
        INECensus2021
"""
    
def download(wd='.',collections=['all'],start=-1,end=-1,municip=['all'],fg=False):
    if fg:
        try:
            os.removedirs(wd)
        except FileNotFoundError:
            pass
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-mc','--municipality_code', help='Provide the municipality code you want to obtain data',
                        default=None)
    parser.add_argument('-fg','--forcegather', help='Force the online gathering process without considering '
                                                    'already downloaded datasets')
    args = parser.parse_args()

    # Gather the INE datasets
    rental_dist = INERentalDistributionAtlas(municipality_code=args.municipalitycode)

