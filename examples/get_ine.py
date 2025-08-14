from social_ES import INE

wd = "/home/gmor/Nextcloud2/Beegroup/data/social_ES"

atlas_df = INE.HouseholdIncomeDistributionAtlas(wd=wd)
population_df = INE.PopulationCensus(wd=wd)
population_education_and_labour_df = INE.EducationAndEmploymentCensus(wd=wd, mode="relative")
cpi_df = INE.ConsumerPriceIndex(wd=wd)
elec_df = INE.AggregatedElectricityConsumption(wd=wd)
housing_market_df = INE.HouseholdsPriceIndex(wd=wd)
housing_rental_df = INE.HouseholdsRentalPriceIndex(wd=wd)
characteristics_buildings = INE.EssentialCharacteristicsOfPopulationAndHouseholds(
    wd=wd,
    hypercadaster_ES_input_pkl_file=f"{wd}/FromHypercadaster/08900.pkl")