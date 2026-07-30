# `EssentialCharacteristicsOfPopulationAndHouseholds`

**Essential characteristics of population and households, by building**

The 2021 census survey of living conditions, extrapolated to the individual building. It covers commuting and transport, domestic work and caring, digital access and online shopping, household composition, dwelling size, rooms, tenure, rent and mortgage costs, second homes, vehicles, waste separation, heating and cooling and their fuels, appliances, lighting, renewable installations, and the condition, accessibility and surroundings of the building itself.

**Source:** [Características esenciales de la población y los viviendas, Censos 2021 (INE)](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177092&menu=resultados&idp=1254735572981#_tabs-1254736195788)

```python
INE.EssentialCharacteristicsOfPopulationAndHouseholds(wd, hypercadaster_ES_input_pkl_file=None, hypercadaster_ES_input_gdf=None)
```

## What it returns

A dict of **70 DataFrames**, one per topic. Every one of them holds 9,837 rows — one per building — and is keyed by the building reference.

<details><summary>The topics</summary>

- `cohabiting_couples_couple_nationality` — 3 columns
- `cohabiting_couples_genres` — 2 columns
- `cohabiting_couples_n_children` — 4 columns
- `households_building_type` — 2 columns
- `households_n_children` — 2 columns
- `households_owned_monthly_mortgage` — 5 columns
- `households_rented_monthly_rent` — 4 columns
- `households_second_home_ownership` — 2 columns
- `households_secondary_second_home_occupancy` — 4 columns
- `households_secondary_second_home_place` — 4 columns
- `households_single_person_age` — 7 columns
- `households_single_person_education_level` — 4 columns
- `households_single_person_employment_status` — 3 columns
- `households_single_person_marital_status` — 4 columns
- `households_single_person_nationality` — 2 columns
- `households_single_person_net_incomes` — 5 columns
- `households_tenure` — 5 columns
- `households_vehicles_eco` — 2 columns
- `households_vehicles_number` — 4 columns
- `households_waste_separation` — 2 columns
- `households_waste_type` — 4 columns
- `households_with_paid_domestic_service` — 2 columns
- `households_with_unpaid_external_help` — 3 columns
- `main_dwellings_accessibility_status` — 2 columns
- `main_dwellings_adapted_to_elderly` — 2 columns
- `main_dwellings_conservation_status` — 6 columns
- `main_dwellings_domestic_appliances_type` — 6 columns
- `main_dwellings_floor_area` — 7 columns
- `main_dwellings_has_cooling` — 2 columns
- `main_dwellings_heating_fuel` — 4 columns
- `main_dwellings_heating_type` — 4 columns
- `main_dwellings_infrastructure_service` — 5 columns
- `main_dwellings_installations` — 5 columns
- `main_dwellings_insulation_issues` — 2 columns
- `main_dwellings_internet_connection` — 4 columns
- `main_dwellings_kitchen_sized_4m2plus` — 2 columns
- `main_dwellings_lighting_type` — 3 columns
- `main_dwellings_n_bathrooms` — 2 columns
- `main_dwellings_n_garages_places` — 6 columns
- `main_dwellings_n_rooms` — 4 columns
- `main_dwellings_renewable_device` — 3 columns
- `main_dwellings_surroundings_issues` — 7 columns
- `main_dwellings_toilet_bath` — 2 columns
- `main_dwellings_water_supply` — 2 columns
- `people16plus_cohabiting_in_house_daycare_involvement` — 5 columns
- `people16plus_has_smartphone` — 2 columns
- `people16plus_has_social_networks` — 2 columns
- `people16plus_has_social_support` — 2 columns
- `people16plus_housework_involvement` — 4 columns
- `people16plus_internet_access` — 2 columns
- `people16plus_living_alone_with_helpers_relationship_type` — 6 columns
- `people16plus_living_alone_with_helpers_residence_place` — 3 columns
- `people16plus_online_selling` — 2 columns
- `people16plus_online_shopping` — 2 columns
- `people16plus_out_house_daycare_involvement` — 5 columns
- `people16plus_parents_education` — 3 columns
- `people16plus_transport_daily_time` — 5 columns
- `people16plus_transport_daily_trips` — 3 columns
- `people16plus_transport_mode` — 4 columns
- `people16plus_transport_satisfaction` — 3 columns
- `people16plus_transport_type` — 4 columns
- `people16plus_work_or_study_place` — 5 columns
- `people_16plus_in_house_daycare_daily_care_hours` — 3 columns
- `people_16plus_in_house_daycare_dependency_type` — 4 columns
- `people_16plus_out_house_daycare_daily_care_hours` — 3 columns
- `people_16plus_out_house_daycare_dependency_type` — 4 columns
- `people_born_foreign_parents_birthplace` — 2 columns
- `people_born_in_spain_parents_birthplace` — 5 columns
- `people_parents_nationality` — 2 columns
- `people_parents_residence` — 6 columns

</details>

## Parameters

```
wd : str
    Working directory the downloaded data is cached under. The first call
    downloads from INE, later ones read the local copy.
hypercadaster_ES_input_pkl_file : str, optional
    Path to a pickled hypercadaster_ES building layer.
hypercadaster_ES_input_gdf : geopandas.GeoDataFrame, optional
    The building layer itself, instead of a path to it. One of the two is required.
```

## Notes

- Returned as a **dictionary of topics** rather than as a few tables by geographic level: one DataFrame per question, each indexed by building.
- Needs a building layer to extrapolate onto, from [hypercadaster_ES](https://github.com/BeeGroup-cimne/hypercadaster_ES) — pass either `hypercadaster_ES_input_pkl_file` or `hypercadaster_ES_input_gdf`. Since 1.0.1 a GeoDataFrame can be passed directly.
- The survey samples; the building-level figures are an extrapolation of it, not a census of each building.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

characteristics = INE.EssentialCharacteristicsOfPopulationAndHouseholds(
    wd=wd, hypercadaster_ES_input_pkl_file=f"{wd}/FromHypercadaster/25900_complete_inference.pkl")
characteristics["main_dwellings_conservation_status"].head()
```

---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
