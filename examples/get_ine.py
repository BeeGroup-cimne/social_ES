from social_ES import utils_INE

wd = "/home/gmor/Nextcloud2/Beegroup/data/social_ES"

atlas_df = utils_INE.INERentalDistributionAtlas(wd = wd)
population_df = utils_INE.INEPopulationAnualCensus(wd = wd)
cpi_df = utils_INE.INEConsumerPriceIndex(wd)
elec_df = utils_INE.INEAggregatedElectricityConsumption(wd=wd)
housing_market_df = utils_INE.INEHouseholdsPriceIndex(wd)
housing_rental_df = utils_INE.INEHouseholdsRentalPriceIndex(wd)
# utils_INE.INEEssentialCharacteristicsOfPopulationAndHouseholds(wd)