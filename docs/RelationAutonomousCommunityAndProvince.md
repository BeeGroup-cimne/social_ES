# `RelationAutonomousCommunityAndProvince`

**Autonomous community and province lookup**

The static lookup between province codes and the autonomous community each belongs to, with the official name of both. Every other function in the library uses it to attach community codes and names to province-coded data.

**Source:** [Códigos de comunidades autónomas y provincias (INE)](https://www.ine.es/daco/daco42/codmun/cod_ccaa_provincia.htm)

```python
INE.RelationAutonomousCommunityAndProvince()
```

## What it returns

A single DataFrame: **52 rows, 4 columns**.

## Notes

- Static: it takes no working directory and downloads nothing.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

INE.RelationAutonomousCommunityAndProvince().head()
```

## Reference

<details><summary>Columns (4)</summary>

- `Autonomous community code`
- `Autonomous community name`
- `Province code`
- `Province name`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
