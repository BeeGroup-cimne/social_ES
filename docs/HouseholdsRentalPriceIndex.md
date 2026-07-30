# `HouseholdsRentalPriceIndex`

**Rental price index**

Annual rental price index at municipal and district level, tracking how the cost of renting moved in each area.

**Source:** [Índice de Precios de la Vivienda en Alquiler, experimental (INE)](https://www.ine.es/en/experimental/ipva/experimental_precios_vivienda_alquiler_en.htm)

```python
INE.HouseholdsRentalPriceIndex(wd, municipality_code=None, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Municipality` | 672 | 5 | 2011–2024 |
| `Districts` | 5,698 | 6 | 2011–2024 |

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

- An **experimental** statistic in INE's own terms, published outside the official series and built from tax records.
- Coverage is limited to the municipalities INE publishes it for, which is far short of all 8,131.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

rents = INE.HouseholdsRentalPriceIndex(wd=wd)
rents["Districts"][rents["Districts"]["Municipality code"] == "08019"]
```

## Reference

The levels hold the same variables, differing only in the codes that key them. `Districts` is the widest, at 6 columns:

<details><summary>Columns (6)</summary>

- `Municipality code`
- `Year`
- `District code`
- `Household rental index`
- `Country code`
- `Province code`

</details>

`Municipality` drops `District code`.


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
