# `MapVariable`

**Interactive choropleth maps**

Takes what any dataset function returned, joins a variable of it to the INE boundaries of the matching year, and writes a standalone interactive HTML map. Leaving `variable` out puts **every** mappable column in the page behind a picker, so the map can be read without deciding beforehand which variable was the interesting one.

```python
INE.MapVariable(data, variable=None, wd=None, level=None, year=None, boundaries_year=None, output_file=None, classification='quantiles', bins=6, palette='sequential', center=None, title=None, subtitle=None, basemap=True, tiles=False, opacity=0.82, borders=None, panels=True, simplify_tolerance=None, max_areas=25000, max_cells=10000000)
```

## Parameters

```
data : dict or pandas.DataFrame
    What a dataset function returned, or one of its tables.
variable : str or list of str, optional
    The column(s) to map. Defaults to every column of the table that describes
    an area rather than identifying it, offered in the page behind a picker.
wd : str
    Working directory the cartography is cached under.
level : str, optional
    Geographic level to map. Defaults to the finest table of `data`, or to the
    level the given DataFrame is at.
year : int or list of int, optional
    Restrict the map to these years. Defaults to every year in the data, with
    a slider when there is more than one.
boundaries_year : int, optional
    Year of the boundaries. Defaults to the most recent year mapped, falling
    back to the closest year INE publishes cartography for.
output_file : str, optional
    Where to write the page. Defaults to a file under ``{wd}/INE/Maps``.
classification : {"quantiles", "equal_interval"} or list, default "quantiles"
    How to cut the numeric range into classes, or the class boundaries
    themselves. Applies to every variable in the page. Ignored for a
    non-numeric variable, whose values are the classes. This is where the
    page's ``Method`` control starts; boundaries given as a list are offered
    there as ``Custom``, and are lost once another cut is asked for.
bins : int, default 6
    Number of classes, and where the page's ``Classes`` control starts.
palette : {"sequential", "greens", "oranges", "purples", "viridis",
           "diverging", "categorical"}, default "sequential"
    A sequential ramp for a magnitude — ``"sequential"`` is the blue one, also
    reachable as ``"blues"`` — ``"diverging"`` for a value read against a
    midpoint (a change, a difference from an average), ``"categorical"`` for
    classes with no order. A non-numeric variable is always categorical. This
    is where the page's ``Palette`` control starts. ``"viridis"`` runs dark to
    light rather than light to dark, and stops short of its yellows, which are
    the part of it a light basemap swallows.
center : float, optional
    The midpoint of a diverging map. Defaults to the median of the values,
    which is the only midpoint that means anything for a variable that is
    never negative — pass ``center=0`` for a change or a difference, whose
    midpoint really is zero.
opacity : float, default 0.82
    How solid the areas are drawn, between 0 and 1, and where the page's
    ``Opacity`` slider starts. Areas with no value are drawn fainter still,
    at the same ratio whatever this is set to.
borders : bool, optional
    Draw the white hairline between areas. Defaults to ``True``, except on a
    tiled map, where every area is cut at the tile boundaries and outlining
    the pieces draws the tile grid across the map. The page's ``Borders``
    checkbox overrides it either way.
panels : bool, default True
    Open the page with the legend and the year slider showing. The button in
    the map's top corner folds them away and back either way, for when what is
    wanted is the map and not the apparatus.
title, subtitle : str, optional
    Override the generated heading. Without a title, the heading names the
    variable being shown, and follows the picker.
basemap : bool, default True
    Draw the areas over a street basemap, which needs the page to be opened
    online. The polygons themselves are embedded in the file and always show.
tiles : bool, default False
    Serve the geometry as vector tiles rather than carrying it in the page. The
    boundaries of the whole level are built once into a PMTiles archive beside the
    cartography (see `BoundaryTiles`) and reused by every later map of that level
    and year, and the page reads only the byte ranges of it that it draws — which
    is what makes the 36,333 census tracts of the country mappable at full detail.
    The page then has to be served rather than opened from disk, by something that
    answers range requests: see `ServeMaps`. An archive written by an older version
    of social_ES is rebuilt rather than read, so the first tiled map after an
    upgrade pays for the build again.
simplify_tolerance : float, optional
    Tolerance in metres the boundaries are simplified with, to keep the page
    small. Defaults to how much geometry there is: a metre, which is invisible,
    for anything that fits the vertex budget, and coarser only for what
    overruns it — 77 m for the 8,131 municipalities of the country, against 1 m
    for the census tracts of a city. Pass 0 for the published detail.
max_areas : int, default 25000
    Refuse to write a page with more areas than this, which the browser would
    struggle with. Filter the data first, or raise this deliberately.
max_cells : int, default 500000
    The same limit on areas × variables × years, which is what a page carrying
    every variable of a large table runs into first. Pass `variable` to map
    fewer of them, or raise this deliberately.
```

## Notes

- Drawn with MapLibre: the areas are vectors on the GPU, so they stay sharp at any zoom and the zoom itself is continuous.
- The legend carries the classification — palette, number of classes, quantiles or linear — plus opacity, borders and the tooltip, and the page re-cuts the values as they change. The `palette`, `bins` and `classification` arguments set where those controls start rather than settling the matter.
- Palettes: `sequential` (blue, the default), `greens`, `oranges`, `purples`, `viridis`, `diverging` and `categorical`. A diverging map centres on the **median** unless `center` says otherwise — zero is the midpoint of a change, but of nothing that is only ever positive.
- A table carrying a `Predicted` column gets a control that drops the modelled areas from the map and the table, so what INE published can be seen on its own.
- Several years become a slider, with the classes cut over every year at once so a colour means the same thing at each stop.
- `tiles=True` serves the geometry from a PMTiles archive instead of embedding it; see `BoundaryTiles` and `ServeMaps`.
- Needs geopandas: `pip install "social_ES[geo]"`.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

atlas = INE.HouseholdIncomeDistributionAtlas(wd=wd, municipality_code="08019")
INE.MapVariable(atlas, "Average net income per person", wd=wd, year=2021)

# every variable, every census tract in the country, served from vector tiles
census = INE.PopulationCensus(wd=wd)
INE.MapVariable(census, wd=wd, level="Census tracts", year=2024, tiles=True)
```

---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
