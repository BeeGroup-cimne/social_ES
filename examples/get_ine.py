from social_ES import utils_INE

wd = "/Users/gmor-air/Nextcloud/Beegroup/data/social_ES"

atlas_df = utils_INE.INERentalDistributionAtlas(wd = wd)
population_df = utils_INE.INEPopulationAnualCensus(wd = wd)
cpi_df = utils_INE.INEConsumerPriceIndex(wd)
elec_df = utils_INE.INEAggregatedElectricityConsumption(wd=wd)
housing_market_df = utils_INE.INEHouseholdsPriceIndex(wd)
housing_rental_df = utils_INE.INEHouseholdsRentalPriceIndex(wd)
characteristics_buildings = (
    utils_INE.INEEssentialCharacteristicsOfPopulationAndHouseholds(wd))