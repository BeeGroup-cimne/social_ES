# social_ES

A Python library to ingest, clean, and transform up-to-date Spanish demographic, socioeconomic, and other social-related
datasets from multiple data source entities. At this moment, only **INE** (Instituto Nacional de Estadística — Spanish
National Statistics Institute) is supported.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-EUPL%20v1.2-blue.svg)](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/BeeGroup-cimne/social_ES)

## 🎯 Overview

**social_ES** automates the discovery, download, and cleaning of official Spanish statistics from INE's data portal.
Instead of manually navigating INE's website and wrangling raw CSV/TSV exports, each function in the library scrapes the
relevant dataset, normalizes column names and geographic codes (autonomous community, province, municipality, district,
census section), and returns a ready-to-use `pandas.DataFrame`.

Downloaded and processed data is cached locally in your working directory, so subsequent calls reuse the cached files
instead of re-downloading from INE.

### Key Features

- 📥 **Automated INE Scraping**: Discovers and downloads the latest published data directly from INE's dissemination
  portal, no manual exports needed
- 🧹 **Cleaning & Normalization**: Consistent column naming, numeric parsing (Spanish decimal format), and geographic
  code harmonization
- 🗂️ **Local Caching**: Results are persisted as `.tsv`/`.parquet` files under your working directory to avoid redundant
  downloads
- 🌍 **Multi-level Geography**: Data available at autonomous community, province, municipality, district, or
  census-section level depending on the dataset
- 🔎 **Filtering**: Most functions support filtering by `municipality_code` and `years`
- 🔗 **hypercadaster_ES Integration**: `EssentialCharacteristicsOfPopulationAndHouseholds` links Census 2021 indicators
  to building-level data exported from [hypercadaster_ES](https://github.com/BeeGroup-cimne/hypercadaster_ES)

## 🚀 Installation

Install from PyPI:

```bash
pip install social_ES
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

# Household income distribution at census-section level
atlas_df = INE.HouseholdIncomeDistributionAtlas(wd=wd)

# Population census, filtered to a specific municipality and years
population_df = INE.PopulationCensus(wd=wd, municipality_code="08900", years=[2021, 2022])

# Education and employment census (relative shares)
education_df = INE.EducationAndEmploymentCensus(wd=wd, mode="relative")

# Consumer Price Index by category
cpi_df = INE.ConsumerPriceIndex(wd=wd)
```

See [examples/get_ine.ipynb](examples/get_ine.ipynb) for a full worked example, including the output format of each
function.

## 📊 Available Datasets

| Function                                                                                 | Description                                                                          | Geographic level                | Key arguments                     |
|------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------|-----------------------------------|
| `RelationAutonomousCommunityAndProvince()`                                               | Static lookup table mapping autonomous community codes/names to province codes/names | Province                        | —                                 |
| `MunicipalityNamesToMunicipalityCodes()`                                                 | Official INE dictionary of municipality names and codes                              | Municipality                    | —                                 |
| `HouseholdIncomeDistributionAtlas(wd, municipality_code, years)`                         | Household income distribution (Atlas de Distribución de Renta de los Hogares)        | Census section                  | `municipality_code`, `years`      |
| `PopulationCensus(wd, municipality_code, years)`                                         | Population census counts                                                             | Province / municipality         | `municipality_code`, `years`      |
| `EducationAndEmploymentCensus(wd, municipality_code, years, mode)`                       | Education level and employment status                                                | Province / municipality         | `mode="relative"\|"absolute"`     |
| `HouseholdsPriceIndex(wd, municipality_code, years)`                                     | Housing price index (whole, new, and second-hand market)                             | Autonomous community, quarterly | `municipality_code`, `years`      |
| `HouseholdsRentalPriceIndex(wd, municipality_code, years)`                               | Housing rental price index                                                           | Municipality / district         | `municipality_code`, `years`      |
| `AggregatedElectricityConsumption(wd, municipality_code, years)`                         | Aggregated electricity consumption percentiles (2021)                                | Municipality / district         | `municipality_code`, `years`      |
| `ConsumerPriceIndex(wd, years)`                                                          | Consumer Price Index (CPI) broken down by COICOP category                            | National                        | `years`                           |
| `EssentialCharacteristicsOfPopulationAndHouseholds(wd, hypercadaster_ES_input_pkl_file)` | Census 2021 population and household characteristics, linked to building-level data  | Building (via hypercadaster_ES) | `hypercadaster_ES_input_pkl_file` |

> Most functions accept `municipality_code` as either a single code (`str`) or a list of codes, and `years` as a list of
> years to filter to. When omitted, the full dataset is returned.

## 💾 Caching Behavior

On first call, each function downloads the relevant data from INE and stores a processed copy under:

```
{wd}/INE/{FunctionName}/
```

Subsequent calls with the same `wd` read from this cache instead of hitting INE again. To force a refresh, delete the
corresponding cache file/folder.

## 🎯 Key Applications

- **Urban & Regional Analysis**: Combine income, population, and housing indicators at municipality or census-section
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
