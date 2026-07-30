# `AdministrativeBoundaries`

**Administrative boundaries**

INE's census-tract cartography for any published year, dissolved into whichever level is asked for: census tracts, districts, municipalities, provinces or autonomous communities. This is the geometry `MapVariable` draws on.

**Source:** [Cartografía de secciones censales (INE)](https://www.ine.es/dyngs/DAB/index.htm?cid=1389)

```python
INE.AdministrativeBoundaries(wd, year=None, level='Census tracts', municipality_code=None, province_code=None, autonomous_community_code=None)
```

## What it returns

A single DataFrame: **52 rows, 6 columns**.

## Parameters

```
wd : str
    Working directory the cartography is cached under.
year : int, optional
    Year of the boundaries. Defaults to the most recent one INE publishes.
level : str, default "Census tracts"
    One of ``"Census tracts"``, ``"Districts"``, ``"Municipality"``,
    ``"Province"`` or ``"Autonomous community"``.
municipality_code : str or list of str, optional
    Restrict the result to these municipality code(s).
province_code : str or list of str, optional
    Restrict the result to these province code(s).
autonomous_community_code : str or list of str, optional
    Restrict the result to these autonomous community code(s).
```

## Notes

- Needs geopandas, which the base install does not pull in: `pip install "social_ES[geo]"`.
- `AvailableBoundaryYears()` lists the years INE publishes, and the file of each.
- Boundaries change from year to year. Joining data of one year to the cartography of another leaves areas unmatched, which `MapVariable` reports rather than dropping quietly.
- The download is a ~60 MB file per year, cached after the first call.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

boundaries = INE.AdministrativeBoundaries(wd=wd, year=2023, level="Municipality",
                                          province_code="08")
boundaries.plot()
```

## Reference

<details><summary>Columns (6)</summary>

- `Country code`
- `Autonomous community code`
- `Autonomous community name`
- `Province code`
- `Province name`
- `geometry`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
