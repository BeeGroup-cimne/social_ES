# socioeconomic_ES

This is a Python library to ingest, clean and transform the most updated Spanish demographics, socioeconomic and other social-related datasets from multiple potential data source entities. At this moment, only INE (Spanish National Statistics Institute) is used.

## How to install the library?
1. Download the repository in your own system: git clone

2. Create library: python setup.py sdist

3. Install library: pip install dist/social_es-1.0.0.tar.gz

## How to use it?
```python
from social_ES import INE
# Define a working data directory
wd = "/home/gmor/Nextcloud2/Beegroup/data/social_ES"
# Fed the data using the functions
atlas_df = INE.HouseholdIncomeDistributionAtlas(wd=wd)
```
In [this notebook](examples/get_ine.ipynb) you will find the examples and the output format of the results.

## Authors
- Jose Manuel Broto - jmbroto@cimne.upc.edu
- Gerard Mor - gmor@cimne.upc.edu

Copyright (c) 2025 Jose Manuel Broto, Gerard Mor
