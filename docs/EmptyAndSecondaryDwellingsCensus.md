# `EmptyAndSecondaryDwellingsCensus`

**Empty and secondary dwellings (2001, 2011, 2021)**

Empty, secondary and non-main dwellings across three censuses, in one table, per municipality, province and autonomous community. The 2021 census dropped the classification the two earlier ones used, so **two classifications are returned side by side rather than merged**, with a third that bridges them.

**Source:** [Censos de Población y Viviendas 2001, 2011 y 2021 (INE)](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177108&menu=resultados&idp=1254735572981)

```python
INE.EmptyAndSecondaryDwellingsCensus(wd, municipality_code=None, years=None, predict=False)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Autonomous community` | 57 | 29 | 2001–2021 |
| `Province` | 156 | 31 | 2001–2021 |
| `Municipality` | 24,355 | 31 | 2001–2021 |

## Parameters

```
wd : str
    Working directory the downloaded data is cached under.
municipality_code : str or list of str, optional
    Restrict the result to these municipality code(s). Only filters the
    ``"Municipality"`` table; the coarser ones are returned whole.
years : list, optional
    Restrict the result to these census years (2001, 2011 and/or 2021).
predict : bool, default False
    Fill in the municipal figures INE withholds — the 2011 secondary/empty split
    below 2,000 inhabitants, the 2021 electricity classification below 1,000 — with
    modelled ones, and mark the rows in ``Predicted``. Left alone, those figures
    stay ``NaN``, which is what the censuses actually say.

    The models are gradient-boosted trees over what INE does publish everywhere:
    the dwelling counts of all three censuses, the 2001 split (the only one that
    exists for every municipality), and the 2021 census indicators describing the
    place. They predict how a total divides, never the total itself — 2011's
    non-main count and 2021's dwelling count are published for every municipality —
    and each share is then scaled so that its province adds up to the figure INE
    publishes for it, exactly. Summing the municipal table therefore reproduces the
    regional ones, which with the gaps left as they come it does not.

    Held out five ways, the shares are predicted at R² 0.72 (2011 secondary) and
    0.76 (2021 empty), against 0.00 for giving every municipality the national rate.
    The result is still an estimate, and a municipality of forty dwellings is
    estimated no better than that; use ``Predicted`` to leave those rows out of
    anything that turns on a single municipality.
```

## Notes

- `Dwellings ~ Dwelling type:*` is the field-census classification, where an agent visiting the building sorted each dwelling into main, secondary or empty. `Main` and `Non-main` exist in all three censuses; `Secondary` and `Empty` only in 2001 and 2011.
- 2001 additionally publishes an *otro tipo* residual, which is counted in `Secondary` — as INE itself does in its 2001-2011 comparison (3,360,631 + 292,332 = 3,652,963) — so that the 2001 secondary count means the same thing as the 2011 one.
- `Dwellings ~ Electricity use:*` is what 2021 publishes instead, derived from each dwelling's yearly electricity consumption: `Empty` (no supply contract, or less than the equivalent of 15 days a year), `Very low consumption` (up to 250 kWh), `Sporadic use` (251-750 kWh) and `Regular use`.
- `Dwellings ~ Comparable use:*` aligns the two into one series readable across all three censuses, as integer counts of dwellings. 2021's `Very low consumption` counts as *secondary* rather than empty: a dwelling used a month a year is what the earlier censuses recorded as a second home.
- **This is a bridge, not an identity.** The 2021 figures come from electricity meters and the earlier ones from a census agent's judgement at the door, so a change between 2011 and 2021 along any of these lines mixes a real change in use with the change of instrument — most visibly in tourist municipalities, where a second home occupied for a full summer consumes well over 750 kWh and lands in `Main`.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

dwellings = INE.EmptyAndSecondaryDwellingsCensus(wd=wd, predict=True)
dwellings["Municipality"][["Year", "Predicted",
                           "Percentage of dwellings ~ Comparable use:Secondary"]]
```

## Reference

The levels hold the same variables, differing only in the codes that key them. `Province` is the widest, at 31 columns:

<details><summary>Columns (31)</summary>

- `Country code`
- `Autonomous community code`
- `Autonomous community name`
- `Province code`
- `Province name`
- `Year`
- `Predicted`
- `Dwellings`
- `Dwellings ~ Dwelling type:Main`
- `Dwellings ~ Dwelling type:Non-main`
- `Dwellings ~ Dwelling type:Secondary`
- `Dwellings ~ Dwelling type:Empty`
- `Dwellings ~ Electricity use:Empty`
- `Dwellings ~ Electricity use:Very low consumption`
- `Dwellings ~ Electricity use:Sporadic use`
- `Dwellings ~ Electricity use:Regular use`
- `Dwellings ~ Comparable use:Main`
- `Dwellings ~ Comparable use:Secondary`
- `Dwellings ~ Comparable use:Empty`
- `Percentage of dwellings ~ Dwelling type:Main`
- `Percentage of dwellings ~ Dwelling type:Non-main`
- `Percentage of dwellings ~ Dwelling type:Secondary`
- `Percentage of dwellings ~ Dwelling type:Empty`
- `Percentage of dwellings ~ Electricity use:Empty`
- `Percentage of dwellings ~ Electricity use:Very low consumption`
- `Percentage of dwellings ~ Electricity use:Sporadic use`
- `Percentage of dwellings ~ Electricity use:Regular use`
- `Percentage of dwellings ~ Comparable use:Main`
- `Percentage of dwellings ~ Comparable use:Secondary`
- `Percentage of dwellings ~ Comparable use:Empty`
- `Median annual electricity consumption (kWh)`

</details>

`Autonomous community` drops `Province code`, `Province name`.

`Municipality` drops `Province name`.


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
