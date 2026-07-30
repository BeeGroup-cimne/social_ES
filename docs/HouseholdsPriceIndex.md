# `HouseholdsPriceIndex`

**Housing price index**

Quarterly housing price index by province — each row also carrying the autonomous community it belongs to — split into the first-hand market (new dwellings), the second-hand market, and the two together.

**Source:** [Índice de Precios de la Vivienda (INE)](https://www.ine.es/dyngs/INEbase/en/operacion.htm?c=Estadistica_C&cid=1254736152838&menu=ultiDatos&idp=1254735976607)

```python
INE.HouseholdsPriceIndex(wd, municipality_code=None, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Province` | 4,028 | 9 | 2007–2025 |

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

- An index, not a price: it measures how prices moved relative to the base period, and says nothing about what a dwelling costs in one province against another.
- Rows are one per area, year and quarter.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

prices = INE.HouseholdsPriceIndex(wd=wd, years=[2024])
prices["Province"].head()
```

## Reference

<details><summary>Columns of `Province` (9)</summary>

- `Autonomous community code`
- `Autonomous community name`
- `Province code`
- `Province name`
- `Year`
- `Quarter`
- `First-hand housing market`
- `Second-hand housing market`
- `Whole housing market`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
