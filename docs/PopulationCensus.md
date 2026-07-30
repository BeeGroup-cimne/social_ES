# `PopulationCensus`

**Population census**

The annual population census: how many people live in each census tract, broken down by sex, by five-year age band, by nationality, by country of birth, and by where in Spain they were born (same municipality, same province, same autonomous community, or elsewhere). Published every year since 2021, which makes it the finest-grained population series INE keeps.

**Source:** [Cifras de Población / Censo anual de población (INE)](https://www.ine.es/dynt3/inebase/en/index.htm?padre=11555&capsel=11100)

```python
INE.PopulationCensus(wd, municipality_code=None, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Municipality` | 40,915 | 220 | 2021–2025 |
| `Districts` | 52,405 | 221 | 2021–2025 |
| `Census tracts` | 184,460 | 222 | 2021–2025 |

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

- Counts are of people registered as resident on 1 January of the reference year.
- The census tract table is the one INE publishes; the district and municipality tables are aggregated from it by `social_ES`.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

population = INE.PopulationCensus(wd=wd, municipality_code="08019", years=[2024])
population["Census tracts"].head()
```

## Reference

The levels hold the same variables, differing only in the codes that key them. `Census tracts` is the widest, at 222 columns:

<details><summary>Columns (222)</summary>

- `Country code`
- `Province code`
- `Municipality code`
- `District code`
- `Year`
- `Census tract code`
- `Population`
- `Population ~ Nationality:Spanish`
- `Population ~ Nationality:Foreign`
- `Population ~ Sex:Males`
- `Population ~ Sex:Males ~ Nationality:Spanish`
- `Population ~ Sex:Males ~ Nationality:Foreign`
- `Population ~ Sex:Females`
- `Population ~ Sex:Females ~ Nationality:Spanish`
- `Population ~ Sex:Females ~ Nationality:Foreign`
- `Population ~ Birth origin:Spain`
- `Population ~ Birth origin:Extranjero`
- `Population ~ Sex:Males ~ Birth origin:Spain`
- `Population ~ Sex:Males ~ Birth origin:Extranjero`
- `Population ~ Sex:Females ~ Birth origin:Spain`
- `Population ~ Sex:Females ~ Birth origin:Extranjero`
- `Population ~ Nationality:España`
- `Population ~ Nationality:French`
- `Population ~ Nationality:British`
- `Population ~ Nationality:Romanian`
- `Population ~ Nationality:Ukrainian`
- `Population ~ Nationality:Other European nationalities`
- `Population ~ Nationality:Moroccan`
- `Population ~ Nationality:Other African nationalities`
- `Population ~ Nationality:Cuban`
- `Population ~ Nationality:Dominican`
- `Population ~ Nationality:Argentinian`
- `Population ~ Nationality:Bolivian`
- `Population ~ Nationality:Colombian`
- `Population ~ Nationality:Ecuadorian`
- `Population ~ Nationality:Peruvian`
- `Population ~ Nationality:Venezuelan`
- `Population ~ Nationality:Other American nationalities`
- `Population ~ Nationality:Chinese`
- `Population ~ Nationality:Other Asian nationalities`
- `Population ~ Nationality:Oceanian`
- `Population ~ Nationality:Stateless`
- `Population ~ Sex:Males ~ Nationality:España`
- `Population ~ Sex:Males ~ Nationality:French`
- `Population ~ Sex:Males ~ Nationality:British`
- `Population ~ Sex:Males ~ Nationality:Romanian`
- `Population ~ Sex:Males ~ Nationality:Ukrainian`
- `Population ~ Sex:Males ~ Nationality:Other European nationalities`
- `Population ~ Sex:Males ~ Nationality:Moroccan`
- `Population ~ Sex:Males ~ Nationality:Other African nationalities`
- `Population ~ Sex:Males ~ Nationality:Cuban`
- `Population ~ Sex:Males ~ Nationality:Dominican`
- `Population ~ Sex:Males ~ Nationality:Argentinian`
- `Population ~ Sex:Males ~ Nationality:Bolivian`
- `Population ~ Sex:Males ~ Nationality:Colombian`
- `Population ~ Sex:Males ~ Nationality:Ecuadorian`
- `Population ~ Sex:Males ~ Nationality:Peruvian`
- `Population ~ Sex:Males ~ Nationality:Venezuelan`
- `Population ~ Sex:Males ~ Nationality:Other American nationalities`
- `Population ~ Sex:Males ~ Nationality:Chinese`
- `Population ~ Sex:Males ~ Nationality:Other Asian nationalities`
- `Population ~ Sex:Males ~ Nationality:Oceanian`
- `Population ~ Sex:Males ~ Nationality:Stateless`
- `Population ~ Sex:Females ~ Nationality:España`
- `Population ~ Sex:Females ~ Nationality:French`
- `Population ~ Sex:Females ~ Nationality:British`
- `Population ~ Sex:Females ~ Nationality:Romanian`
- `Population ~ Sex:Females ~ Nationality:Ukrainian`
- `Population ~ Sex:Females ~ Nationality:Other European nationalities`
- `Population ~ Sex:Females ~ Nationality:Moroccan`
- `Population ~ Sex:Females ~ Nationality:Other African nationalities`
- `Population ~ Sex:Females ~ Nationality:Cuban`
- `Population ~ Sex:Females ~ Nationality:Dominican`
- `Population ~ Sex:Females ~ Nationality:Argentinian`
- `Population ~ Sex:Females ~ Nationality:Bolivian`
- `Population ~ Sex:Females ~ Nationality:Colombian`
- `Population ~ Sex:Females ~ Nationality:Ecuadorian`
- `Population ~ Sex:Females ~ Nationality:Peruvian`
- `Population ~ Sex:Females ~ Nationality:Venezuelan`
- `Population ~ Sex:Females ~ Nationality:Other American nationalities`
- `Population ~ Sex:Females ~ Nationality:Chinese`
- `Population ~ Sex:Females ~ Nationality:Other Asian nationalities`
- `Population ~ Sex:Females ~ Nationality:Oceanian`
- `Population ~ Sex:Females ~ Nationality:Stateless`
- `Population ~ Birth country:Spain`
- `Population ~ Birth country:France`
- `Population ~ Birth country:United Kingdom`
- `Population ~ Birth country:Romania`
- `Population ~ Birth country:Ukraine`
- `Population ~ Birth country:Other European countries`
- `Population ~ Birth country:Morocco`
- `Population ~ Birth country:Other African countries`
- `Population ~ Birth country:Cuba`
- `Population ~ Birth country:Dominican Republic`
- `Population ~ Birth country:Argentina`
- `Population ~ Birth country:Bolivia`
- `Population ~ Birth country:Colombia`
- `Population ~ Birth country:Ecuador`
- `Population ~ Birth country:Peru`
- `Population ~ Birth country:Venezuela`
- `Population ~ Birth country:Other American countries`
- `Population ~ Birth country:China`
- `Population ~ Birth country:Other Asian countries`
- `Population ~ Birth country:Oceania`
- `Population ~ Sex:Males ~ Birth country:Spain`
- `Population ~ Sex:Males ~ Birth country:France`
- `Population ~ Sex:Males ~ Birth country:United Kingdom`
- `Population ~ Sex:Males ~ Birth country:Romania`
- `Population ~ Sex:Males ~ Birth country:Ukraine`
- `Population ~ Sex:Males ~ Birth country:Other European countries`
- `Population ~ Sex:Males ~ Birth country:Morocco`
- `Population ~ Sex:Males ~ Birth country:Other African countries`
- `Population ~ Sex:Males ~ Birth country:Cuba`
- `Population ~ Sex:Males ~ Birth country:Dominican Republic`
- `Population ~ Sex:Males ~ Birth country:Argentina`
- `Population ~ Sex:Males ~ Birth country:Bolivia`
- `Population ~ Sex:Males ~ Birth country:Colombia`
- `Population ~ Sex:Males ~ Birth country:Ecuador`
- `Population ~ Sex:Males ~ Birth country:Peru`
- `Population ~ Sex:Males ~ Birth country:Venezuela`
- `Population ~ Sex:Males ~ Birth country:Other American countries`
- `Population ~ Sex:Males ~ Birth country:China`
- `Population ~ Sex:Males ~ Birth country:Other Asian countries`
- `Population ~ Sex:Males ~ Birth country:Oceania`
- `Population ~ Sex:Females ~ Birth country:Spain`
- `Population ~ Sex:Females ~ Birth country:France`
- `Population ~ Sex:Females ~ Birth country:United Kingdom`
- `Population ~ Sex:Females ~ Birth country:Romania`
- `Population ~ Sex:Females ~ Birth country:Ukraine`
- `Population ~ Sex:Females ~ Birth country:Other European countries`
- `Population ~ Sex:Females ~ Birth country:Morocco`
- `Population ~ Sex:Females ~ Birth country:Other African countries`
- `Population ~ Sex:Females ~ Birth country:Cuba`
- `Population ~ Sex:Females ~ Birth country:Dominican Republic`
- `Population ~ Sex:Females ~ Birth country:Argentina`
- `Population ~ Sex:Females ~ Birth country:Bolivia`
- `Population ~ Sex:Females ~ Birth country:Colombia`
- `Population ~ Sex:Females ~ Birth country:Ecuador`
- `Population ~ Sex:Females ~ Birth country:Peru`
- `Population ~ Sex:Females ~ Birth country:Venezuela`
- `Population ~ Sex:Females ~ Birth country:Other American countries`
- `Population ~ Sex:Females ~ Birth country:China`
- `Population ~ Sex:Females ~ Birth country:Other Asian countries`
- `Population ~ Sex:Females ~ Birth country:Oceania`
- `Population ~ Birth origin in Spain:Born in the same municipality`
- `Population ~ Birth origin in Spain:Born in a municipality of the same province`
- `Population ~ Birth origin in Spain:Born in a municipality of the same autonomous community`
- `Population ~ Birth origin in Spain:Born in a municipality of another autonomous community`
- `Population ~ Birth origin in Spain:Nacido en el extranjero o en antiguos territorios españoles`
- `Population ~ Sex:Males ~ Birth origin in Spain:Born in the same municipality`
- `Population ~ Sex:Males ~ Birth origin in Spain:Born in a municipality of the same province`
- `Population ~ Sex:Males ~ Birth origin in Spain:Born in a municipality of the same autonomous community`
- `Population ~ Sex:Males ~ Birth origin in Spain:Born in a municipality of another autonomous community`
- `Population ~ Sex:Males ~ Birth origin in Spain:Nacido en el extranjero o en antiguos territorios españoles`
- `Population ~ Sex:Females ~ Birth origin in Spain:Born in the same municipality`
- `Population ~ Sex:Females ~ Birth origin in Spain:Born in a municipality of the same province`
- `Population ~ Sex:Females ~ Birth origin in Spain:Born in a municipality of the same autonomous community`
- `Population ~ Sex:Females ~ Birth origin in Spain:Born in a municipality of another autonomous community`
- `Population ~ Sex:Females ~ Birth origin in Spain:Nacido en el extranjero o en antiguos territorios españoles`
- `Population ~ Age:0-4`
- `Population ~ Age:5-9`
- `Population ~ Age:10-14`
- `Population ~ Age:15-19`
- `Population ~ Age:20-24`
- `Population ~ Age:25-29`
- `Population ~ Age:30-34`
- `Population ~ Age:35-39`
- `Population ~ Age:40-44`
- `Population ~ Age:45-49`
- `Population ~ Age:50-54`
- `Population ~ Age:55-59`
- `Population ~ Age:60-64`
- `Population ~ Age:65-69`
- `Population ~ Age:70-74`
- `Population ~ Age:75-79`
- `Population ~ Age:80-84`
- `Population ~ Age:85-89`
- `Population ~ Age:90-94`
- `Population ~ Age:95-99`
- `Population ~ Age:>99`
- `Population ~ Sex:Males ~ Age:0-4`
- `Population ~ Sex:Males ~ Age:5-9`
- `Population ~ Sex:Males ~ Age:10-14`
- `Population ~ Sex:Males ~ Age:15-19`
- `Population ~ Sex:Males ~ Age:20-24`
- `Population ~ Sex:Males ~ Age:25-29`
- `Population ~ Sex:Males ~ Age:30-34`
- `Population ~ Sex:Males ~ Age:35-39`
- `Population ~ Sex:Males ~ Age:40-44`
- `Population ~ Sex:Males ~ Age:45-49`
- `Population ~ Sex:Males ~ Age:50-54`
- `Population ~ Sex:Males ~ Age:55-59`
- `Population ~ Sex:Males ~ Age:60-64`
- `Population ~ Sex:Males ~ Age:65-69`
- `Population ~ Sex:Males ~ Age:70-74`
- `Population ~ Sex:Males ~ Age:75-79`
- `Population ~ Sex:Males ~ Age:80-84`
- `Population ~ Sex:Males ~ Age:85-89`
- `Population ~ Sex:Males ~ Age:90-94`
- `Population ~ Sex:Males ~ Age:95-99`
- `Population ~ Sex:Males ~ Age:>99`
- `Population ~ Sex:Females ~ Age:0-4`
- `Population ~ Sex:Females ~ Age:5-9`
- `Population ~ Sex:Females ~ Age:10-14`
- `Population ~ Sex:Females ~ Age:15-19`
- `Population ~ Sex:Females ~ Age:20-24`
- `Population ~ Sex:Females ~ Age:25-29`
- `Population ~ Sex:Females ~ Age:30-34`
- `Population ~ Sex:Females ~ Age:35-39`
- `Population ~ Sex:Females ~ Age:40-44`
- `Population ~ Sex:Females ~ Age:45-49`
- `Population ~ Sex:Females ~ Age:50-54`
- `Population ~ Sex:Females ~ Age:55-59`
- `Population ~ Sex:Females ~ Age:60-64`
- `Population ~ Sex:Females ~ Age:65-69`
- `Population ~ Sex:Females ~ Age:70-74`
- `Population ~ Sex:Females ~ Age:75-79`
- `Population ~ Sex:Females ~ Age:80-84`
- `Population ~ Sex:Females ~ Age:85-89`
- `Population ~ Sex:Females ~ Age:90-94`
- `Population ~ Sex:Females ~ Age:95-99`
- `Population ~ Sex:Females ~ Age:>99`

</details>

`Municipality` drops `District code`, `Census tract code`.

`Districts` drops `Census tract code`.


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
