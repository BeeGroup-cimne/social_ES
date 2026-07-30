from social_ES import INE

wd = "/mnt/data2/social_ES"

atlas_df = INE.HouseholdIncomeDistributionAtlas(wd=wd)
population_df = INE.PopulationCensus(wd=wd)
population_education_and_labour_df = INE.EducationAndEmploymentCensus(wd=wd, mode="relative")
dwellings_and_population_df = INE.DwellingsAndPopulationCensus(wd=wd)
empty_and_secondary_dwellings_df = INE.EmptyAndSecondaryDwellingsCensus(wd=wd)
cpi_df = INE.ConsumerPriceIndex(wd=wd)
elec_df = INE.AggregatedElectricityConsumption(wd=wd)
housing_market_df = INE.HouseholdsPriceIndex(wd=wd)
housing_rental_df = INE.HouseholdsRentalPriceIndex(wd=wd)
time_use_df = INE.TimeUseSurvey(wd=wd)
characteristics_buildings = INE.EssentialCharacteristicsOfPopulationAndHouseholds(
    wd=wd,
    hypercadaster_ES_input_pkl_file=f"{wd}/FromHypercadaster/08900.pkl")

# Boundaries and maps. These need geopandas: pip install "social_ES[geo]"

# The boundaries of any level, for any year INE publishes cartography for
barcelona_tracts = INE.AdministrativeBoundaries(wd=wd, year=2021, level="Census tracts",
                                                municipality_code="08019")

# A map of one variable of one dataset, written as a standalone HTML page
barcelona_census = INE.DwellingsAndPopulationCensus(wd=wd, municipality_code="08019")
INE.MapVariable(barcelona_census,
                "Percentage of population aged 16 and over ~ Educational level:Tertiary education",
                wd=wd, title="Tertiary education, Barcelona")

# Without a variable, every one of them goes into the page and is picked from there
INE.MapVariable(barcelona_census, wd=wd)

# Three censuses in one page: the years become a slider
INE.MapVariable(empty_and_secondary_dwellings_df, "Percentage of dwellings ~ Comparable use:Empty",
                wd=wd, level="Autonomous community")

# Read against a reference rather than as a magnitude
INE.MapVariable(empty_and_secondary_dwellings_df, "Percentage of dwellings ~ Comparable use:Empty",
                wd=wd, level="Municipality", year=2021, palette="diverging", center=15)

# More geometry than a page can carry — the census tracts of the whole country — is
# served as vector tiles instead. The archive is built once and reused by every later
# map of that level and year, and the page has to be served rather than opened.
INE.MapVariable(dwellings_and_population_df, wd=wd, level="Census tracts", tiles=True)

server = INE.ServeMaps(wd=wd)          # open the printed URL, then:
# server.shutdown()