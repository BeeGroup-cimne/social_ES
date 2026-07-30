# `HouseholdIncomeDistributionAtlas`

**Household income distribution**

The income atlas, built from tax records rather than from a survey, and published down to the census tract. It carries average and median income per person and per household, the distribution within each area (percentiles, the Gini index, the ratio between the top and bottom deciles), the sources income comes from (wages, pensions, unemployment benefit, other benefits), and the demographic breakdowns INE publishes alongside them — by sex, by age band, and by country of birth.

**Source:** [Atlas de Distribución de Renta de los Hogares (INE)](https://www.ine.es/dyngs/INEbase/en/operacion.htm?c=Estadistica_C&cid=1254736177088&menu=ultiDatos&idp=1254735976608)

```python
INE.HouseholdIncomeDistributionAtlas(wd, municipality_code=None, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Municipality` | 72,890 | 192 | 2015–2023 |
| `Districts` | 94,253 | 193 | 2015–2023 |
| `Census tracts` | 331,743 | 194 | 2015–2023 |

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

- Income is nominal, in euros of the year it belongs to. Comparing years means deflating them yourself; `ConsumerPriceIndex` is in the library for that.
- `Household income group` is an inflation-adjusted band that matches the bands `TimeUseSurvey` uses, so the two datasets join on it directly without any further work.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

atlas = INE.HouseholdIncomeDistributionAtlas(wd=wd, municipality_code="08019")
atlas["Census tracts"][["Year", "Census tract code", "Average net income per person"]]
```

## Reference

The levels hold the same variables, differing only in the codes that key them. `Census tracts` is the widest, at 194 columns:

<details><summary>Columns (194)</summary>

- `Municipality name`
- `Municipality code`
- `District code`
- `Census tract code`
- `Year`
- `Average household income`
- `Average household net income`
- `Average income by unit of consumption`
- `Average net income per person`
- `Average per person gross income`
- `Median income by unit of consumption`
- `Source of income: other benefits`
- `Source of income: other income`
- `Source of income: pensions`
- `Source of income: unemployment benefits`
- `Source of income: wages`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Males`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Females`
- `Percentage of the population with income per consumption unit of under 5,000 euros `
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Males`
- `Percentage of the population with income per consumption unit of under 7,500 euros `
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Females`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Males`
- `Percentage of the population with income per consumption unit of under 10,000 euros `
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Females`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Males ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Males ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Males ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Females ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Males ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Males ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Females ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Males ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Females ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Females ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Sex:Males ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 5,000 euros  ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Males ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Sex:Females ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 7,500 euros  ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Males ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 10,000 euros  ~ Sex:Females ~ Nationality:Foreign`
- `Population with per consumption unit income above 200% of the median`
- `Population with per consumption unit income above 200% of the median ~ Sex:Males`
- `Population with per consumption unit income above 160% of the median ~ Sex:Females`
- `Population with per consumption unit income above 200% of the median ~ Sex:Females`
- `Population with per consumption unit income above 160% of the median`
- `Population with per consumption unit income above 160% of the median ~ Sex:Males`
- `Population with per consumption unit income above 140% of the median ~ Sex:Females`
- `Population with per consumption unit income above 140% of the median ~ Sex:Males`
- `Population with per consumption unit income above 140% of the median`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Males`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Males`
- `Percentage of the population with income per consumption unit of under 40% of the median `
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Females`
- `Percentage of the population with income per consumption unit of under 50% of the median `
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Males`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Females`
- `Percentage of the population with income per consumption unit of under 60% of the median `
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Females`
- `Population with per consumption unit income above 200% of the median ~ Sex:Males ~ Age:<18`
- `Population with per consumption unit income above 200% of the median ~ Age:<18`
- `Population with per consumption unit income above 200% of the median ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Males ~ Age:>64`
- `Population with per consumption unit income above 200% of the median ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Males ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Age:>64`
- `Population with per consumption unit income above 200% of the median ~ Sex:Males ~ Age:>64`
- `Population with per consumption unit income above 200% of the median ~ Age:>64`
- `Population with per consumption unit income above 160% of the median ~ Sex:Males ~ Age:>64`
- `Population with per consumption unit income above 200% of the median ~ Sex:Females ~ Age:18-64`
- `Population with per consumption unit income above 160% of the median ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Females ~ Age:>64`
- `Population with per consumption unit income above 160% of the median ~ Age:<18`
- `Population with per consumption unit income above 160% of the median ~ Sex:Females ~ Age:<18`
- `Population with per consumption unit income above 140% of the median ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Age:>64`
- `Population with per consumption unit income above 160% of the median ~ Age:>64`
- `Population with per consumption unit income above 200% of the median ~ Age:18-64`
- `Population with per consumption unit income above 200% of the median ~ Sex:Males ~ Age:18-64`
- `Population with per consumption unit income above 160% of the median ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Males ~ Age:>64`
- `Population with per consumption unit income above 140% of the median ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Males ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Females ~ Age:18-64`
- `Population with per consumption unit income above 140% of the median ~ Sex:Females ~ Age:>64`
- `Population with per consumption unit income above 140% of the median ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Age:<18`
- `Population with per consumption unit income above 140% of the median ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Males ~ Age:18-64`
- `Population with per consumption unit income above 160% of the median ~ Sex:Females ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Age:>64`
- `Population with per consumption unit income above 140% of the median ~ Sex:Males ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Age:18-64`
- `Population with per consumption unit income above 160% of the median ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Males ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Females ~ Age:18-64`
- `Population with per consumption unit income above 160% of the median ~ Sex:Males ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Males ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Females ~ Age:>64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Females ~ Age:<18`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Males ~ Age:<18`
- `Population with per consumption unit income above 140% of the median ~ Sex:Females ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Females ~ Age:18-64`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Age:<18`
- `Population with per consumption unit income above 140% of the median ~ Age:18-64`
- `Population with per consumption unit income above 140% of the median ~ Sex:Males ~ Age:18-64`
- `Population with per consumption unit income above 200% of the median ~ Sex:Females ~ Nationality:Foreign`
- `Population with per consumption unit income above 200% of the median ~ Sex:Males ~ Nationality:Foreign`
- `Population with per consumption unit income above 200% of the median ~ Nationality:Foreign`
- `Population with per consumption unit income above 160% of the median ~ Sex:Males ~ Nationality:Foreign`
- `Population with per consumption unit income above 160% of the median ~ Nationality:Foreign`
- `Population with per consumption unit income above 160% of the median ~ Sex:Females ~ Nationality:Foreign`
- `Population with per consumption unit income above 140% of the median ~ Sex:Males ~ Nationality:Foreign`
- `Population with per consumption unit income above 140% of the median ~ Nationality:Foreign`
- `Population with per consumption unit income above 140% of the median ~ Sex:Females ~ Nationality:Foreign`
- `Population with per consumption unit income above 200% of the median ~ Sex:Males ~ Nationality:Spanish`
- `Population with per consumption unit income above 200% of the median ~ Nationality:Spanish`
- `Population with per consumption unit income above 200% of the median ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Nationality:Spanish`
- `Population with per consumption unit income above 160% of the median ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Females ~ Nationality:Spanish`
- `Population with per consumption unit income above 160% of the median ~ Nationality:Spanish`
- `Population with per consumption unit income above 160% of the median ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Nationality:Spanish`
- `Population with per consumption unit income above 140% of the median ~ Sex:Females ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Females ~ Nationality:Spanish`
- `Population with per consumption unit income above 140% of the median ~ Nationality:Spanish`
- `Population with per consumption unit income above 140% of the median ~ Sex:Males ~ Nationality:Spanish`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Males ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Sex:Females ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 40% of the median  ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Females ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Sex:Males ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 50% of the median  ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Females ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Nationality:Foreign`
- `Percentage of the population with income per consumption unit of under 60% of the median  ~ Sex:Males ~ Nationality:Foreign`
- `Gini Index`
- `Income distribution P80/P20`
- `Average age of the population`
- `Average size of the household`
- `Percentage of Spanish population`
- `Percentage of single-person households`
- `Percentage of the population over the age of 65`
- `Percentage of the population under the age of 18`
- `Population`
- `Country code`
- `Province code`
- `Autonomous community code`
- `Autonomous community name`
- `Average household net income (2010 EUR)`
- `Household income group`
- `Household income group label`

</details>

`Municipality` drops `District code`, `Census tract code`.

`Districts` drops `Census tract code`.


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
