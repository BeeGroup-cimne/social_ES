# `AggregatedElectricityConsumption`

**Household electricity consumption**

Yearly household electricity consumption in kWh, per district, summarised as percentiles of the distribution — the 10th, 25th, 50th, 75th and 90th — so that the spread within an area is visible rather than just its average.

**Source:** [Consumo eléctrico de los hogares, Censos 2021 (INE)](https://www.ine.es/dynt3/inebase/index.htm?padre=8959&capsel=9844)

```python
INE.AggregatedElectricityConsumption(wd, municipality_code=None, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Districts` | 5,077 | 9 | 2021 |

## Parameters

```
wd : str
    Working directory the downloaded data is cached under. The first call
    downloads from INE, later ones read the local copy.
municipality_code : str or list of str, optional
    Restrict the result to these municipality code(s).
years : list of int, optional
    Restrict the result to these years.
```

## Notes

- Part of the 2021 census, and published for 2021 only.
- Percentiles rather than a mean, because household consumption is skewed: a handful of very high consumers would carry an average away from what most households in the area actually use.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

electricity = INE.AggregatedElectricityConsumption(wd=wd)
electricity["Districts"][electricity["Districts"]["Municipality code"] == "08019"]
```

## Reference

<details><summary>Columns of `Districts` (9)</summary>

- `Municipality code`
- `District code`
- `Municipality name`
- `Percentile 10 of electricity consumption in kwh`
- `Percentile 25 of electricity consumption in kwh`
- `Percentile 50 of electricity consumption in kwh`
- `Percentile 75 of electricity consumption in kwh`
- `Percentile 90 of electricity consumption in kwh`
- `Year`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
