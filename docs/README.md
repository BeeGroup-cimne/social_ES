# social_ES documentation

One page per function. Every table below was read out of the functions themselves against a full cache, so the row and column counts are what you will actually get.

## Datasets

| Function | What it is | Levels |
|---|---|---|
| [`HouseholdIncomeDistributionAtlas`](HouseholdIncomeDistributionAtlas.md) | Household income distribution | `Municipality`, `Districts`, `Census tracts` |
| [`PopulationCensus`](PopulationCensus.md) | Population census | `Municipality`, `Districts`, `Census tracts` |
| [`EducationAndEmploymentCensus`](EducationAndEmploymentCensus.md) | Education and employment census | `Municipality`, `Districts`, `Census tracts` |
| [`DwellingsAndPopulationCensus`](DwellingsAndPopulationCensus.md) | Population and dwellings census 2021 | `Municipality`, `Districts`, `Census tracts` |
| [`EmptyAndSecondaryDwellingsCensus`](EmptyAndSecondaryDwellingsCensus.md) | Empty and secondary dwellings (2001, 2011, 2021) | `Autonomous community`, `Province`, `Municipality` |
| [`ConsumerPriceIndex`](ConsumerPriceIndex.md) | Consumer price index (2015 base) | `National` |
| [`AggregatedElectricityConsumption`](AggregatedElectricityConsumption.md) | Household electricity consumption | `Districts` |
| [`HouseholdsPriceIndex`](HouseholdsPriceIndex.md) | Housing price index | `Province` |
| [`HouseholdsRentalPriceIndex`](HouseholdsRentalPriceIndex.md) | Rental price index | `Municipality`, `Districts` |
| [`EssentialCharacteristicsOfPopulationAndHouseholds`](EssentialCharacteristicsOfPopulationAndHouseholds.md) | Essential characteristics of population and households, by building | 70 topics, by building |
| [`TimeUseSurvey`](TimeUseSurvey.md) | Time use survey (EET 2009-2010) | `Census tracts`, `WeeklySchedule`, `HolidaySchedule`, `WeeklyScheduleHouseholdOccupancy`, `WeeklyScheduleHouseholdOccupancyValue` |
| [`RelationAutonomousCommunityAndProvince`](RelationAutonomousCommunityAndProvince.md) | Autonomous community and province lookup | one table |
| [`MunicipalityNamesToMunicipalityCodes`](MunicipalityNamesToMunicipalityCodes.md) | Municipality name and code dictionary | one table |

## Boundaries and maps

| Function | What it is | Levels |
|---|---|---|
| [`AdministrativeBoundaries`](AdministrativeBoundaries.md) | Administrative boundaries | one table |
| [`BoundaryTiles`](BoundaryTiles.md) | Vector tile archives | — |
| [`ServeMaps`](ServeMaps.md) | Serving the maps | — |
| [`MapVariable`](MapVariable.md) | Interactive choropleth maps | — |

## Getting started

```python
from social_ES import INE

# every dataset caches under `wd`; the first call downloads, later ones read
wd = "/path/to/your/data"

atlas = INE.HouseholdIncomeDistributionAtlas(wd=wd)
```

Install with `pip install social_ES`, or `pip install "social_ES[geo]"` for the boundaries and mapping functions, which need geopandas.

See also the [worked example notebook](https://github.com/BeeGroup-cimne/social_ES/blob/master/examples/get_ine.ipynb) and the [README](https://github.com/BeeGroup-cimne/social_ES#readme).
