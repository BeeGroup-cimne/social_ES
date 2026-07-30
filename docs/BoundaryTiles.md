# `BoundaryTiles`

**Vector tile archives**

Builds and caches the PMTiles vector-tile archive of a geographic level, which is what lets `MapVariable(tiles=True)` draw all 36,462 census tracts of the country at full detail. One archive per level and year, reused by every later map of them.

```python
INE.BoundaryTiles(wd, year=None, level='Census tracts')
```

## Parameters

```
wd : str
    Working directory the cartography is cached under.
year : int, optional
    Year of the boundaries. Defaults to the most recent one INE publishes.
level : str, default "Census tracts"
    One of the five levels `AdministrativeBoundaries` returns.
```

## Notes

- Building is slow — around 4 minutes for the census tracts — and happens once. The archive is then read in place by the page, a byte range at a time.
- Archives are versioned in their filename. One written by an older version of `social_ES` is rebuilt rather than read, so the first tiled map after an upgrade pays for the build again.
- Tiles are written from zoom 3 to zoom 12, the top level on a finer grid than the rest because it is the one every closer view is drawn from.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

archive = INE.BoundaryTiles(wd=wd, year=2023, level="Census tracts")
```

---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
