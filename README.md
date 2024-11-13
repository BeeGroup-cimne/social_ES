# socioeconomic_ES

This is a Python library to ingest the most updated Spanish socioeconomic data regarding ....bla bla bla. 

## How to install the library?
1- Download the repository in your own system: git clone
2- Create library: python setup.py sdist
2- Install library: pip install dist/socioeconomic_ES-0.0.1.tar.gz

## How to use it?
```python
import social_ES as sc

path = "data"
# Return the available collections.
sc.available_collections() 

# Downloading all socioeconomic data from all available collections is the default option, but the parameters can be changed.
sc.download()

# Download socioeconomic data in the `path: str` from the specified `collections: list`, `years: list`, and `municipality codes: list`. Decide whether to `update`: bool` (True =  Do not take into account that datasets have already been downloaded). 
# Return an array with the results of its respective collection.
res = sc.download(path,['INEcensus2021'], list(range(2021,2024+1)), ['08001','08002'], False) 

res[0]['Sections'].to_csv("test.csv",index=False)
```

## Sample script
Downloads all scocioeconomic data of `02003` municipality of 2021 and 2019.

```python
import socioeconomic_ES as sc

collections = sc.available_collections()
res = sc.download(collections=collections,municip=['02003'],years=[2021,2019],update=False)
res[0]['Sections'].to_csv("test0_munic.csv",index=False) 
res[1]['Sections'].to_csv("test1_munic.csv",index=False) 
res[2]['Province'].to_csv("test2_munic.csv",index=False)
res[3]['Districts'].to_csv("test3_munic.csv",index=False)
res[4]['Municipality'].to_csv("test4_munic.csv",index=False)
res[5]['National'].to_csv("test5_munic.csv",index=False)
res[6]['Sections'].to_csv("test6_munic.csv",index=False)
```


## For developers
All the gathering functions should have the input parameters: `path`, `years` and `municipality codes`.


## Authors
- Jose Manuel Broto - jmbroto@cimne.upc.edu
- Gerard Mor - gmor@cimne.upc.edu
- Míriam Méndez - miriam.mendez.serrano@estudiantat.upc.edu

Copyright (c) 2024 Jose Manuel Broto, Gerard Mor, Míriam Méndez
