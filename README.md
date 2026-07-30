# social_ES

A Python library to ingest, clean, and transform up-to-date Spanish demographic, socioeconomic, and other social-related
datasets from multiple data source entities. At this moment, only **INE** (Instituto Nacional de Estadística — Spanish
National Statistics Institute) is supported.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-EUPL%20v1.2-blue.svg)](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
[![Version](https://img.shields.io/badge/version-1.0.3-green.svg)](https://github.com/BeeGroup-cimne/social_ES)

## 🎯 Overview

**social_ES** automates the discovery, download, and cleaning of official Spanish statistics from INE's data portal.
Instead of manually navigating INE's website and wrangling raw CSV/TSV exports, each function in the library scrapes the
relevant dataset, normalizes column names and geographic codes (autonomous community, province, municipality, district,
census tract), and returns a dictionary of `pandas.DataFrame`s keyed by geographic level (e.g. `"Census tracts"`,
`"Districts"`, `"Municipality"`, `"Province"`, `"National"`), with the level(s) available depending on the dataset.

Downloaded and processed data is cached locally in your working directory, so subsequent calls reuse the cached files
instead of re-downloading from INE.

### Key Features

- 📥 **Automated INE Scraping**: Discovers and downloads the latest published data directly from INE's dissemination
  portal, no manual exports needed
- 🧹 **Cleaning & Normalization**: Consistent column naming, locale-aware numeric parsing (INE publishes the same table
  in Spanish `24.900` and English `24,900` formats depending on the province), and geographic code harmonization
- 🗂️ **Local Caching**: Results are persisted as `.tsv`/`.parquet` files under your working directory to avoid redundant
  downloads
- 🌍 **Multi-level Geography**: Data available at autonomous community, province, municipality, district, or
  census-tract level depending on the dataset
- 🔎 **Filtering**: Most functions support filtering by `municipality_code` and `years`
- 🔗 **hypercadaster_ES Integration**: `EssentialCharacteristicsOfPopulationAndHouseholds` links Census 2021 indicators
  to building-level data exported from [hypercadaster_ES](https://github.com/BeeGroup-cimne/hypercadaster_ES)
- 🏚️ **Historical Census Series**: `EmptyAndSecondaryDwellingsCensus` puts the 2001, 2011 and 2021 dwelling-use counts
  in one table, keeping the field-census and the 2021 electricity-based classifications apart rather than pretending
  they are the same variable
- 🧩 **Cross-dataset Join Keys**: `HouseholdIncomeDistributionAtlas` carries an inflation-adjusted
  `Household income group` that matches the bands of `TimeUseSurvey`, so income and time-use data join directly
- 🗺️ **Boundaries & Maps**: `AdministrativeBoundaries` downloads INE's census-tract cartography for any published
  year and dissolves it into districts, municipalities, provinces and autonomous communities; `MapVariable` joins any
  variable of any dataset to it and writes a standalone interactive HTML choropleth

## 🚀 Installation

Install from PyPI:

```bash
pip install social_ES

# with the boundaries and mapping functions, which need geopandas
pip install "social_ES[geo]"
```

Or, for development from source:

```bash
git clone https://github.com/BeeGroup-cimne/social_ES.git
cd social_ES
pip install .
```

## 📖 Quick Start

```python
from social_ES import INE

# Define a working directory where downloaded/processed data will be cached
wd = "/path/to/your/data"

# Household income distribution at census-tract level (returns dict with "Census tracts", "Districts", "Municipality")
atlas = INE.HouseholdIncomeDistributionAtlas(wd=wd)
atlas_sections = atlas["Census tracts"]  # census-tract level data

# Population census, filtered to a specific municipality and years (returns dict with "Census tracts", "Districts", "Municipality")
population = INE.PopulationCensus(wd=wd, municipality_code="08019", years=[2021, 2022])
population_sections = population["Census tracts"]  # census-tract level data

# Education and employment census (relative shares; returns dict with "Census tracts", "Districts", "Municipality")
education = INE.EducationAndEmploymentCensus(wd=wd, mode="relative")  # mode defaults to "relative"
education_sections = education["Census tracts"]

# Population and dwellings census 2021 (returns dict with "Census tracts", "Districts", "Municipality")
census_2021 = INE.DwellingsAndPopulationCensus(wd=wd)
census_2021_sections = census_2021["Census tracts"]

# Empty and secondary dwellings across the 2001, 2011 and 2021 censuses
# (returns dict with "Municipality", "Province", "Autonomous community")
dwelling_use = INE.EmptyAndSecondaryDwellingsCensus(wd=wd, municipality_code="08019")
dwelling_use["Municipality"][["Year", "Percentage of dwellings ~ Comparable use:Main",
                              "Percentage of dwellings ~ Comparable use:Secondary",
                              "Percentage of dwellings ~ Comparable use:Empty"]]  # one series across the 3 censuses
dwelling_use["Autonomous community"]  # regional figures — complete, unlike summing the municipal table

# Consumer Price Index by category (returns dict with "National")
cpi = INE.ConsumerPriceIndex(wd=wd)
cpi_national = cpi["National"]

# Join income data to time-use profiles: both datasets share the same income banding
time_use = INE.TimeUseSurvey(wd=wd)
weekly_by_tract = atlas["Census tracts"].query("Year == 2021").merge(
    time_use["WeeklySchedule"], on=["Autonomous community code", "Household income group"])
```

**[Full documentation](docs/README.md)** — one page per function, with the levels it returns, its parameters and
its columns.

See [examples/get_ine.ipynb](examples/get_ine.ipynb) for a full worked example, including the output format of each
function.

## 📊 Available Datasets

| Function                                                                                 | Description                                                                          | Geographic level                | Key arguments                     |
|------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------|-----------------------------------|
| `RelationAutonomousCommunityAndProvince()`                                               | Static lookup table mapping autonomous community codes/names to province codes/names | Province                        | —                                 |
| `MunicipalityNamesToMunicipalityCodes()`                                                 | Official INE dictionary of municipality names and codes                              | Municipality                    | —                                 |
| `HouseholdIncomeDistributionAtlas(wd, municipality_code, years)`                         | Household income distribution (Atlas de Distribución de Renta de los Hogares)        | Census tract / district / municipality | `municipality_code`, `years`      |
| `PopulationCensus(wd, municipality_code, years)`                                         | Population census counts                                                             | Census tract / district / municipality | `municipality_code`, `years`      |
| `EducationAndEmploymentCensus(wd, municipality_code, years, mode)`                       | Education level and employment status                                                | Census tract / district / municipality | `mode="relative"\|"absolute"`     |
| `DwellingsAndPopulationCensus(wd, municipality_code, years)`                             | Population and dwellings census 2021: population profile (sex, age, nationality, education, labour force status, marital status) and dwelling, tenure and household size counts | Census tract / district / municipality | `municipality_code`, `years` (fixed to 2021) |
| `EmptyAndSecondaryDwellingsCensus(wd, municipality_code, years, predict)`                          | Empty, secondary and non-main dwellings in the 2001, 2011 and 2021 censuses, as counts and as shares of the area's dwellings | Municipality / province / autonomous community | `municipality_code`, `years` (2001, 2011, 2021) |
| `HouseholdsPriceIndex(wd, municipality_code, years)`                                     | Housing price index (whole, new, and second-hand market)                             | Province (derived from autonomous community), quarterly | `municipality_code`, `years`      |
| `HouseholdsRentalPriceIndex(wd, municipality_code, years)`                               | Housing rental price index                                                           | Municipality / district         | `municipality_code`, `years`      |
| `AggregatedElectricityConsumption(wd, municipality_code, years)`                         | Aggregated electricity consumption percentiles (2021)                                | District (municipality code retained) | `municipality_code`, `years`      |
| `ConsumerPriceIndex(wd, years)`                                                          | Consumer Price Index (CPI) broken down by COICOP category                            | National                        | `years`                           |
| `EssentialCharacteristicsOfPopulationAndHouseholds(wd, hypercadaster_ES_input_pkl_file, hypercadaster_ES_input_gdf)` | Census 2021 population and household characteristics, linked to building-level data  | Building (via hypercadaster_ES) | `hypercadaster_ES_input_pkl_file`, `hypercadaster_ES_input_gdf` |
| `TimeUseSurvey(wd, municipality_code, years, reference_year)`                            | Time Use Survey (EET 2009-2010): weekly hourly activity shares + yearly daily holiday schedule, linked to census tracts via autonomous community + household income band | Census tract (matched to autonomous community + income band) | `municipality_code`, `reference_year` (note: `years` accepted but ignored — survey fixed to 2009-2010) |

> Most functions accept `municipality_code` as either a single code (`str`) or a list of codes, and `years` as a list of
> years to filter to. When omitted, the full dataset is returned.

**2021 census indicators**: `DwellingsAndPopulationCensus` reads INE's single
[`C2021_Indicadores.csv`](https://www.ine.es/censos2021/C2021_Indicadores.csv) file, published at census-tract level
only; the `"Districts"` and `"Municipality"` tables are aggregated by `social_ES`, summing the counts and averaging each
share weighting by the population it is a share of (total population, population aged 16 and over, or active
population, depending on the indicator), so that all three levels are read the same way. Shares are returned as
percentages (0-100) rather than the proportions of the source file, and `Average age` is left in years. INE suppresses
the indicators of the smallest census tracts for statistical confidentiality: those rows keep their `Population` and
are `NaN` elsewhere, and they are skipped when the coarser levels are built, so the totals fall slightly short of the
published national ones.

**Empty and secondary dwellings**: the 2021 census dropped the classification the 2001 and 2011 ones used, so
`EmptyAndSecondaryDwellingsCensus` returns two side by side and never mixes them.

`Dwellings ~ Dwelling type:*` is the field-census classification, where an agent visiting the building sorted each
dwelling into main, secondary (occasional use, e.g. holidays) or empty. `Main` and `Non-main` are published in all three
censuses; `Secondary` and `Empty` exist in 2001 and 2011 only, plus an `Other non-main` residual in 2001. The 2021
census is built from administrative registers alone, with nobody to ask whether a dwelling is a second home, so it
publishes only main/non-main and both are `NaN`.

`Dwellings ~ Electricity use:*` is what INE publishes in its place for 2021, derived from the yearly electricity
consumption of each dwelling: `Empty` (no supply contract, or less than the equivalent of 15 days a year for that
municipality), `Very low consumption` (up to 250 kWh), `Sporadic use` (251-750 kWh, roughly one to three months a year)
and `Regular use`. The four partition the total.

`Dwellings ~ Comparable use:*` aligns the two into a single series that can be read across the three censuses, filled
from whichever classification each census published:

| Comparable use | 2001 / 2011 (field census) | 2021 (electricity) |
|---|---|---|
| `Main` | `Dwelling type:Main` | `Electricity use:Regular use` |
| `Secondary` | `Dwelling type:Secondary` (+ `Other non-main`, in 2001) | `Electricity use:Very low consumption` + `Sporadic use` |
| `Empty` | `Dwelling type:Empty` | `Electricity use:Empty` |

The three classes partition the total in every census, so their shares always add to 100, and they are returned as
integer counts of dwellings. One choice is worth spelling out: 2021's `Very low consumption` (up to 250 kWh, about a
month of use) counts as **secondary**, not empty — a dwelling used a month a year is what the earlier censuses recorded
as a second home, and reading `Sporadic use` alone would understate it. A row takes all three classes from one
classification or from none, so the series is never half-filled from one census and half from another.

2001 is the only census that splits an "otro tipo" residual out of the non-main dwellings, and it is counted in
`Dwelling type:Secondary` rather than returned on its own — which is what INE itself does in its published 2001–2011
comparison (3,360,631 + 292,332 = 3,652,963). Keeping it apart would make the 2001 secondary count read lower than the
later ones for no reason other than the questionnaire.

**Filling the gaps INE leaves** (`predict=True`): the 2011 split is published only for municipalities over 2,000
inhabitants and the 2021 electricity classification only for those over 1,000, so most municipalities carry `NaN`.
What is missing is never the whole picture, though — the total each missing piece belongs to *is* published for the
municipality (2011 gives every non-main count, 2021 every dwelling count), the province total of every missing column
is published too, and the municipal counts of those totals add up to their province exactly in all 52 provinces. So a
model only has to say how a known quantity divides, and gradient-boosted trees do that from what INE publishes
everywhere: the dwelling counts of all three censuses, the 2001 split (the only one that exists for every
municipality), and the 2021 census indicators describing the place. Each predicted share is then scaled until its
province adds up to the published figure **exactly**, so summing the municipal table reproduces the regional one —
which, with the gaps left as they come, it does not.

Held out five ways, the shares are predicted at R² 0.72 (2011 secondary) and 0.76 (2021 empty), against 0.00 for
giving every municipality the national rate. It is still an estimate: a municipality of forty dwellings is estimated
no better than that. The `Predicted` column says of every row whether any of its figures were modelled, `MapVariable`
turns it into a show/hide control on the map, and without `predict=True` nothing is filled in at all.

> ⚠️ **This is a bridge, not an identity.** The 2021 numbers come from electricity meters, the earlier ones from a
> census agent's judgement at the door, so any movement between 2011 and 2021 along these lines mixes a real change in
> use with the change of instrument. It bites hardest in tourist municipalities, where a second home occupied for a
> full summer consumes well over 750 kWh and is classified as `Main`. When the published figures are what matter, use
> `Dwelling type:*` and `Electricity use:*`, which are always one column away.

Nationally the harmonised series reads:

| Comparable use | 2001 | 2011 | 2021 |
|---|---|---|---|
| `Main` | 14,187,169 | 18,083,693 | 19,336,136 |
| `Secondary` | 3,652,963 | 3,681,566 | 3,459,265 |
| `Empty` | 3,106,422 | 3,443,365 | 3,828,307 |
| **Total** | **20,946,554** | **25,208,624** | **26,623,708** |

Municipal coverage follows each census's methodology and is deliberately left as `NaN` where INE publishes nothing:

| Census | `Dwellings`, `Main`, `Non-main` | `Secondary` / `Empty` | `Electricity use:*` | `Comparable use:*` |
|--------|-----------------------------------|-------------------------|-----------------------|----------------------|
| 2001   | 8,108 municipalities (all)        | 8,108 (all)             | —                     | 8,108 (all)          |
| 2011   | 8,116 municipalities (all)        | 2,308 (over 2,000 inhabitants) | —              | 2,308                |
| 2021   | 8,131 municipalities (all)        | —                       | 3,139 (over 1,000 inhabitants, ~97% of the population) | 3,139 |

The municipalities left out are only released aggregated per province, under pseudo-codes like
`01999 Resto de Araba/Álava`, which are dropped since they are not municipalities.

> ⚠️ **Do not sum the municipal table to get regional figures.** For the partially-published columns it falls short by
> construction — nationally it recovers only 85.9% of the 2021 empty dwellings, and as little as 48% in Castilla y León
> and 50% in Aragón, whose parks are concentrated in small municipalities. Use the `"Province"` and
> `"Autonomous community"` tables, which read those columns from INE's own regional tables and are complete.

The `"Province"` and `"Autonomous community"` tables reproduce INE's published regional figures exactly (verified
against every autonomous community for the three censuses and against the four Catalan provinces): 2001 to the unit,
2021 to the unit, and 2011 to within the ±1 of INE's own rounding of its sample-based estimates.

Every count is echoed as `Percentage of dwellings ~ ...`, its share of the area's `Dwellings`, in percent (0-100).
Municipality codes are the ones each census was published with, so municipalities created, merged or renamed between
2001 and 2021 do not line up across years — see [INE's list of alterations](https://www.ine.es/intercensal/).

One more comparability trap: INE's own 2001–2011 series counts the 2001 `Other non-main` residual as secondary, so
reproducing it means adding `Secondary` + `Other non-main` (3,360,631 + 292,332 = 3,652,963 nationally). They are kept
apart here because 2001 published them apart.

**Joining income data**: `HouseholdIncomeDistributionAtlas` adds a `Household income group` column (plus its
`Household income group label` and the `Average household net income (2010 EUR)` it is derived from). Each row's
nominal average net household income is deflated to 2010 prices with the general CPI (`ConsumerPriceIndex`) and then
bucketed into the four bands the Time Use Survey respondents answered in — `1,200 € or less`, `1,201 to 2,000 €`,
`2,001 to 3,000 €`, `More than 3,000 €` — so Atlas rows of any year can be joined straight onto the `TimeUseSurvey`
schedules on `["Autonomous community code", "Household income group"]`.

Deflating matters: a tract whose income grows only with inflation keeps the same group across years, instead of
drifting upwards. In 2023 nominal terms the band edges sit at roughly 1,529 €, 2,549 € and 3,823 € per month.

> ℹ️ The EET microdata are anonymised with Ceuta and Melilla merged into a single community, so their joint time-use
> profile is published under both standard codes (`18` and `19`). Melilla tracts join like any other; just note that
> their schedules are shared with Ceuta rather than measured separately.

## 🗺️ Boundaries and Maps

Two functions turn the tables above into geography. They need geopandas, which the base install deliberately leaves
out: `pip install "social_ES[geo]"`.

| Function                                                                       | Description                                                                       |
|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `AvailableBoundaryYears()`                                                     | The years INE publishes cartography for (2001, and 2003 onwards), and the file of each |
| `AdministrativeBoundaries(wd, year, level, municipality_code, province_code, autonomous_community_code)` | A `GeoDataFrame` of boundaries in WGS84, at any of the five levels |
| `MapVariable(data, variable, wd, ...)`                                         | Writes an interactive HTML choropleth of a dataset — one variable, or every one of them behind a picker |
| `BoundaryTiles(wd, year, level)`                                               | Builds and caches the PMTiles vector-tile archive of a level, for `MapVariable(tiles=True)` |
| `ServeMaps(wd, port)`                                                          | Serves the written maps and their tile archives over HTTP, byte ranges included    |

```python
from social_ES import INE

wd = "/path/to/your/data"

# The 2021 census tracts of Barcelona, ready to join any census-tract table onto
tracts = INE.AdministrativeBoundaries(wd=wd, year=2021, level="Census tracts", municipality_code="08019")

# A map of one variable, straight from what a dataset function returned
census = INE.DwellingsAndPopulationCensus(wd=wd, municipality_code="08019")
INE.MapVariable(census, "Percentage of population aged 16 and over ~ Educational level:Tertiary education",
                wd=wd, title="Tertiary education, Barcelona")

# Leave the variable out and every one of them goes into the page, behind a picker
INE.MapVariable(census, wd=wd)

# Several years become a slider, with the classes computed over all of them at once
dwellings = INE.EmptyAndSecondaryDwellingsCensus(wd=wd)
INE.MapVariable(dwellings, "Percentage of dwellings ~ Comparable use:Empty",
                wd=wd, level="Autonomous community")

# A value read against a reference rather than as a magnitude
INE.MapVariable(dwellings, "Percentage of dwellings ~ Comparable use:Empty", wd=wd,
                level="Municipality", year=2021, palette="diverging", center=15)
```

**Where the boundaries come from**: INE publishes the georeferenced contours of every census tract of the country, one
national file per year, at [its open data portal](https://www.ine.es/dyngs/DAB/index.htm?cid=1389) — for 2001 and for
every year from 2003 to the current one. **Only census tracts are published**: districts, municipalities, provinces and
autonomous communities are exact unions of tracts, and `social_ES` builds them by dissolving, so every level nests
inside the coarser ones without slivers or mismatched coastlines. The 2021 file yields 36,333 tracts, 10,479 districts,
8,131 municipalities, 52 provinces and 19 autonomous communities.

The published files come in two layouts, both normalised to the column names the dataset functions use and reprojected
to WGS84 (EPSG:4326): from 2011 on, a single national shapefile in ETRS89 / UTM 30N carrying the codes and the
community, province and municipality names; before that, two shapefiles in different UTM zones (peninsula plus
Balearics, and the Canaries) carrying the codes alone, whose names are filled in from the library's own lookups.

> ⚠️ **Boundaries are redrawn every year.** Tracts are split as population grows and municipalities merge or are
> renamed, so a code only means the same area within a year or two of its cartography. `AdministrativeBoundaries` takes
> the year rather than choosing one, and `MapVariable` defaults it to the most recent year being mapped. Areas of the
> data with no boundary in that year are reported and left off the map.

**What the map is**: a single self-contained HTML file — the geometry is embedded, so nothing but the basemap tiles and
MapLibre itself is fetched when it is opened. The areas are drawn as vectors on the GPU, so they stay sharp at any
zoom and the zoom itself is continuous rather than a ladder of whole levels. Hovering an area gives its name, code and value; several years become a
slider, with the classes computed over every year at once so the colours mean the same thing at each stop; and the
values are also written out as a table, since a colour is not a readable number. The polygons use a single-hue blue
ramp for a magnitude (`palette="sequential"`, the default), blue-to-red around a midpoint for a value read against a
reference (`"diverging"`, with `center`), and a fixed categorical order for a non-numeric variable, which is detected
and switched to automatically. `"greens"`, `"oranges"` and `"purples"` are the same ramp in another hue — the lightness
steps are shared, so only the colour changes and never how far apart two classes look — and `"viridis"` runs the other
way, dark to light, stopping short of its yellows, which are the part of it a light basemap swallows.

A diverging map mirrors its classes around `center`, which defaults to the **median** of the values. Zero is the
midpoint of a change or a difference, but of nothing that is only ever positive: centred on zero, a percentage spends
half its classes below the smallest value there is, and the legend reads in negative numbers. Pass `center=0` for the
variables whose midpoint really is zero. The mirror reaches only as far as the shorter side of the data allows, and the
two outer classes carry whatever lies past it.

**Opacity, borders and the tooltip** are page controls too. `opacity` sets how solid the areas are drawn (areas with no
value stay fainter, at the same ratio); `borders` draws the white hairline between areas, and defaults to off on a
tiled map, where every area is cut at the tile boundaries and outlining the pieces would draw the tile grid across the
map; the tooltip that follows the pointer can be switched off from the legend.

**Changing the map without rewriting the file**: the legend carries the classification itself — the palette, the number
of classes, and whether they are cut at quantiles or at equal intervals — plus the opacity, the borders and the
tooltip, and the page cuts the values again as those change. `palette`, `bins` and `classification` set where the controls start rather than settling the
matter, so trying six classes instead of four, or linear instead of quantiles, costs a click rather than another call.
Class boundaries passed in by hand (`classification=[0, 100, 1000]`) are offered as `Custom` and are what the map opens
on; asking for any other cut replaces them. A non-numeric variable has no boundaries to move, so the controls are
hidden for it.

A table carrying a `Predicted` column — `EmptyAndSecondaryDwellingsCensus(predict=True)` — gets one more: a checkbox
that drops the modelled areas from the map and from the table, so what INE actually published can be seen on its own.
The tooltip says so on the area itself. The button in the map's top corner folds the panels away entirely, and
`panels=False` opens the page with them already folded.

**Size and detail**: past 200 KB the payload is gzipped and base64'd into the page, and unpacked in the browser with
`DecompressionStream` (Chrome/Edge 80+, Firefox 113+, Safari 16.4+); below that it stays plain JSON, readable in an
editor. Because compression pays for detail, boundaries are simplified by how much geometry there is rather than by how
much of the country is on screen: anything inside the vertex budget keeps a 1 m tolerance, which is a pixel at zoom 17
and invisible, and only what overruns is coarsened. Census tracts of a city and provinces are drawn at 1 m and 5.5 m;
the 8,131 municipalities of the country, four million vertices of coastline, at 77 m. Pass `simplify_tolerance=0` for
exactly what INE published. The result is both finer and smaller than reading the geometry uncompressed:

| Page | Before | Now | Tolerance |
|---|---|---|---|
| Barcelona census tracts, one variable | 0.41 MB | **0.14 MB** | 5 m → 1 m |
| Barcelona census tracts, all 36 variables | 0.76 MB | **0.26 MB** | 5 m → 1 m |
| Autonomous communities, all variables, 3 years | 0.86 MB | 2.60 MB | 100 m → 4.4 m |
| Spain municipalities, one variable | 9.29 MB | **4.95 MB** | 100 m → 77 m |

The areas are one GPU layer rather than one element each, and the data reaches them as feature state — the class each
area falls in — with the colours following from a paint expression. Changing the palette, the number of classes or the
year rewrites that expression instead of restyling thousands of shapes, and never touches the geometry.

### Vector tiles, for the maps that don't fit

A page can only carry so much geometry. The 36,333 census tracts of the country are close to seven million vertices, and
coarsening them enough to embed would need a tolerance of 222 m against areas whose median extent is 822 m — which
flattens a census tract into a blob. `MapVariable` refuses that rather than drawing it, and points here.

`tiles=True` cuts the geometry into vector tiles the browser fetches as it draws them, so what a page holds stops
depending on how much of the country it covers:

```python
census = INE.DwellingsAndPopulationCensus(wd=wd)

# Builds {wd}/INE/AdministrativeBoundaries/census_tracts_2021.pmtiles the first time,
# then reuses it for every later map of that level and year
INE.MapVariable(census, wd=wd, level="Census tracts", tiles=True)

server = INE.ServeMaps(wd=wd)          # http://127.0.0.1:8000/Maps/
# ... open the printed URL ...
server.shutdown()
```

The archive is built **over the whole country**, whatever the map that asked for it draws, so one archive serves every
map of its level and year — a map of one city and a map of all of Spain read the same file. It is cached beside the
cartography it comes from and rebuilt only if deleted. Values stay in the page and are joined to the tiles by the area
code each tile feature carries, which is what lets one archive serve maps of different variables, years and datasets.

> ⚠️ **A tiled map has to be served.** A page opened from a `file://` URL is not allowed to fetch anything, tiles
> included — so `tiles=True` maps are opened through `ServeMaps` (or any server that answers byte-range requests), not
> by double-clicking. Maps without `tiles=True` stay self-contained files. The page reads the PMTiles archive in place,
> asking for the ranges holding the header, the directory and the tiles it draws, so the level stays the one cached
> file it was built as and nothing has to unpack it on the way out.

| Level (2021, whole country) | Areas | Embedded page | Tiled page | Archive, built once |
|---|---|---|---|---|
| Districts, one variable | 10,479 | ~10 MB | **0.16 MB** | 21.7 MB, 13,201 tiles, 121 s |
| Census tracts, all 36 variables | 36,333 | refused | **3.85 MB** | 29.9 MB, 13,201 tiles, 205 s |

(Both archives hold the same 13,201 tiles: the tiles are the ones covering Spain, and only what is inside them
differs.) The archive is built to zoom 12, where a tile unit is about 2 m; past that the browser scales the tiles it
has, so zooming to street level costs nothing further.

**Leaving `variable` out** puts *every* mappable column of the table into the page, behind a picker, so the map can be
read without deciding beforehand which variable was the interesting one — the heading, the legend, the colours, the
tooltips and the table all follow it. Each variable is classified on its own, so a count and a percentage each get
their own classes, and a text column is drawn as categories while its neighbours are drawn as magnitudes. Columns that
identify the area (codes, names, `Year`) are left out, as are columns that hold nothing and text columns with more than
50 distinct values. `variable` also takes a list, to offer a chosen few. Geometry dominates the file size, so the
picker is close to free: the 1,068 census tracts of Barcelona are 140 KB with one variable and 260 KB with all 36.

`MapVariable` accepts either the whole dictionary a dataset function returned — picking the table by `level`, or the
finest one it holds — or a single DataFrame, whose level it reads off the code columns. It refuses to write more than
`max_areas` (25,000) areas, or more than `max_cells` (500,000) areas × variables × years, into one page — a browser
would struggle to open either; filter the data, or name the variables you want.

**Return format**: Most functions return a dictionary with keys like `"Census tracts"`, `"Districts"`, `"Municipality"`, `"Province"`, or `"National"` holding the corresponding `pandas.DataFrame`. The exception is `EssentialCharacteristicsOfPopulationAndHouseholds`, which returns a dictionary, sorted by key, where each key is an English snake_case topic name (e.g. `"main_dwellings_heating_type"`) and each value is a building-level DataFrame whose columns append the class after a `~` (e.g. `"main_dwellings_heating_type~individual"`). ECEPOV publishes a few dwelling attributes twice, once counting households and once counting main dwellings; only the `main_dwellings_*` variant is returned, since it carries the same information (this drops `households_n_rooms` and `households_floor_area`).

## 💾 Caching Behavior

On first call, each function downloads the relevant data from INE and stores a processed copy under:

```
{wd}/INE/{FunctionName}/
```

Depending on the function, cached files may be `.tsv`, `.parquet`, or `.pkl` (for metadata dictionaries). Subsequent calls with the same `wd` read from this cache instead of hitting INE again. To force a refresh, delete the corresponding cache file/folder.

**Cartography is the big one**: the first call to `AdministrativeBoundaries` for a year downloads a ~60 MB shapefile and
writes one GeoParquet per level under `{wd}/INE/AdministrativeBoundaries/`, about 345 MB per year in total, in exchange
for every later call being a local read. Maps are written to `{wd}/INE/Maps/` unless `output_file` says otherwise.

**Cache versions**: some cache files carry a `_v2`/`_v3` suffix. When a parsing fix makes previously cached data wrong,
the suffix is bumped so the next call rebuilds it instead of silently reusing bad values; the superseded file is left in
place and can be deleted by hand.

- `HouseholdIncomeDistributionAtlas/df_v3.tsv` supersedes `df_v2.tsv`. INE serves this dataset in two number formats
  depending on the province — Spanish (`24.900`) and English (`24,900`) — and the earlier parser read the English ones
  as a thousandth of their value (Córdoba, Guadalajara, Lleida and Asturias were almost entirely affected), besides
  truncating values whose trailing digits were zeros. Expect a one-time full re-download on the first call after
  upgrading.
- `EssentialCharacteristicsOfPopulationAndHouseholds/*_v2.pkl` supersedes the unsuffixed metadata caches, which were
  built with a variable-splitting bug.
- `TimeUseSurvey/*.tsv` hold the profiles exactly as the microdata support them, so they contain no community `19`:
  Melilla is filled in from Ceuta when the files are read, and no rebuild is needed.

## 🎯 Key Applications

- **Urban & Regional Analysis**: Combine income, population, and housing indicators at municipality or census-tract
  level
- **Building-level Socioeconomic Profiling**: Join Census 2021 household characteristics to cadastral building data via
  hypercadaster_ES
- **Energy & Social Studies**: Cross-reference aggregated electricity consumption with income and demographic indicators

## 📄 License

This project is licensed under the **EUPL v1.2**. See
the [license](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) for details.

## Authors

- Jose Manuel Broto - jmbroto@cimne.upc.edu
- Gerard Mor - gmor@cimne.upc.edu

Copyright (c) 2025 Jose Manuel Broto, Gerard Mor
