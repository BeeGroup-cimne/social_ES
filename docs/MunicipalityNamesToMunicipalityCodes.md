# `MunicipalityNamesToMunicipalityCodes`

**Municipality name and code dictionary**

INE's official dictionary of municipality names and their five-digit codes — the join key nearly every other dataset here is published against.

**Source:** [Relación de municipios y códigos por provincias (INE)](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031)

```python
INE.MunicipalityNamesToMunicipalityCodes()
```

## What it returns

A single DataFrame: **8,132 rows, 2 columns**.

## Notes

- Municipality codes are five digits, the first two being the province. They are strings, not numbers: dropping the leading zero of Álava (01) breaks the join.
- Municipalities merge and split, and codes change with them, which is why a map of one year's data against another year's boundaries leaves areas out.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

INE.MunicipalityNamesToMunicipalityCodes().head()
```

## Reference

<details><summary>Columns (2)</summary>

- `Municipality name`
- `Municipality code`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
