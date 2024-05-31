import argparse
from utils_INE import *
from utils_OpenDataBCN import *

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-mc','--municipality_code', help='Provide the municipality code you want to obtain data',
                        default=None)
    parser.add_argument('-fg','--forcegather', help='Force the online gathering process without considering '
                                                    'already downloaded datasets')
    args = parser.parse_args()

    # Gather the INE datasets
    rental_dist = INERentalDistributionAtlas(municipality_code=args.municipalitycode)

