# socioeconomic_ES

This is a Python library to ingest the most updated Spanish socioeconomic data regarding [these](./social_ES/collections.yaml) domains.

## How to install the library?
1. Download the repository in your own system: git clone

2. Create library: python setup.py sdist

3. Install library: pip install dist/social_es-1.0.0.tar.gz

## How to use it?
```python
import social_ES.utils_INE as sc
wd = "/home/gmor/Nextcloud2/Beegroup/data/social_ES"

essential_characteristics = sc.INEEssentialCharacteristicsOfPopulationAndHouseholds(wd)
population = sc.INEPopulationAnualCensus(wd)
atlas = sc.INERentalDistributionAtlas(wd)
```

## For developers
All the gathering functions should have the input parameters: `path`, `years` and `municipality codes`.


## Authors
- Jose Manuel Broto - jmbroto@cimne.upc.edu
- Gerard Mor - gmor@cimne.upc.edu
- Míriam Méndez - miriam.mendez.serrano@estudiantat.upc.edu

Copyright (c) 2024 Jose Manuel Broto, Gerard Mor, Míriam Méndez
