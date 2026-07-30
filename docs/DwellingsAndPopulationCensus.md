# `DwellingsAndPopulationCensus`

**Population and dwellings census 2021**

The fixed set of indicators the 2021 census publishes for every census tract: population (sex, average age, age groups, foreign nationality and birth origin, current and attained education, labour-force status, marital status), dwellings (total, main and non-main, and the tenure of the main ones), and households (total, and by household size).

**Source:** [Censos de Población y Viviendas 2021 — indicadores (INE)](https://www.ine.es/censos2021/C2021_Indicadores.csv)

```python
INE.DwellingsAndPopulationCensus(wd, municipality_code=None, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Municipality` | 8,131 | 42 | 2021 |
| `Districts` | 10,479 | 43 | 2021 |
| `Census tracts` | 36,333 | 44 | 2021 |

## Parameters

```
wd : str
    Working directory the downloaded data is cached under.
municipality_code : str or list of str, optional
    Restrict the result to these municipality code(s).
years : list, optional
    Restrict the result to these years.
```

## Notes

- INE publishes this at census-tract level only. The district and municipality tables are aggregated by `social_ES`: counts are summed, and each share is averaged weighting by the population it is a share of.
- Shares are returned as percentages (0-100) rather than the proportions of the source file.
- INE suppresses the indicators of the smallest census tracts for statistical confidentiality. Those rows keep their population and are missing elsewhere.
- This is the table `EmptyAndSecondaryDwellingsCensus(predict=True)` draws its predictors from.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

census = INE.DwellingsAndPopulationCensus(wd=wd)
census["Municipality"][["Municipality code", "Dwellings", "Dwellings ~ Dwelling type:Non-main"]]
```

## Reference

The levels hold the same variables, differing only in the codes that key them. `Census tracts` is the widest, at 44 columns:

<details><summary>Columns (44)</summary>

- `Country code`
- `Autonomous community code`
- `Autonomous community name`
- `Province code`
- `Municipality code`
- `District code`
- `Census tract code`
- `Year`
- `Population`
- `Percentage of population ~ Sex:Females`
- `Percentage of population ~ Sex:Males`
- `Average age`
- `Percentage of population ~ Age:<16`
- `Percentage of population ~ Age:16-64`
- `Percentage of population ~ Age:>64`
- `Percentage of population ~ Nationality:Foreign`
- `Percentage of population ~ Birth origin:Foreign country`
- `Percentage of population aged 16 and over ~ Current studies:Higher education`
- `Percentage of population aged 16 and over ~ Current studies:University education`
- `Percentage of population aged 16 and over ~ Educational level:Tertiary education`
- `Percentage of active population ~ Labour force status:Unemployed`
- `Percentage of population aged 16 and over ~ Labour force status:Employed`
- `Percentage of population aged 16 and over ~ Labour force status:Active`
- `Percentage of population aged 16 and over ~ Labour force status:Recipient of disability pension`
- `Percentage of population aged 16 and over ~ Labour force status:Recipient of retirement pension`
- `Percentage of population aged 16 and over ~ Labour force status:Other inactive situation`
- `Percentage of population aged 16 and over ~ Labour force status:Student`
- `Percentage of population ~ Marital status:Single`
- `Percentage of population ~ Marital status:Married`
- `Percentage of population ~ Marital status:Widowed`
- `Percentage of population ~ Marital status:Not stated`
- `Percentage of population ~ Marital status:Legally separated or divorced`
- `Dwellings`
- `Dwellings ~ Dwelling type:Main`
- `Dwellings ~ Dwelling type:Non-main`
- `Main dwellings ~ Tenure:Owned`
- `Main dwellings ~ Tenure:Rented`
- `Main dwellings ~ Tenure:Other tenure`
- `Households`
- `Households ~ Household size:1 person`
- `Households ~ Household size:2 persons`
- `Households ~ Household size:3 persons`
- `Households ~ Household size:4 persons`
- `Households ~ Household size:5 or more persons`

</details>

`Municipality` drops `District code`, `Census tract code`.

`Districts` drops `Census tract code`.


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
