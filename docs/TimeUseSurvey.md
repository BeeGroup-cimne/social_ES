# `TimeUseSurvey`

**Time use survey (EET 2009-2010)**

Weekly hourly activity profiles and daily holiday probabilities, built from the Spanish time use survey microdata and attached to census tracts. Ten activity groups that sum to 100% within each combination of autonomous community, income group, weekday and hour — which is what makes this usable as an occupancy schedule.

**Source:** [Encuesta de Empleo del Tiempo 2009-2010, microdatos (INE)](https://www.ine.es/ftp/microdatos/emptiem/datos_emptiem0910.zip)

```python
INE.TimeUseSurvey(wd, municipality_code=None, reference_year=2010)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Census tracts` | 34,090 | 11 | — |
| `WeeklySchedule` | 12,696 | 20 | — |
| `HolidaySchedule` | 27,740 | 7 | — |
| `WeeklyScheduleHouseholdOccupancy` | 76 | 170 | — |
| `WeeklyScheduleHouseholdOccupancyValue` | — | — | a `dict` |

## Parameters

```
wd : str
    Working directory. The survey profiles are cached under
    ``{wd}/INE/TimeUseSurvey/`` on first use.
municipality_code : str or list, optional
    Restrict ``"Census tracts"`` to these municipality code(s).
reference_year : int, default 2010
    Calendar year the daily holiday schedule is expanded over.
```

## Notes

- The microdata are anonymised to the autonomous-community level, so a census tract inherits the profile of its community and income band rather than one of its own.
- Census tracts are assigned an income band from `HouseholdIncomeDistributionAtlas`, using bands that match it directly.
- The survey is from 2009-2010 and has not been repeated at this resolution; `reference_year` only sets which calendar the holiday schedule is laid on.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

time_use = INE.TimeUseSurvey(wd=wd)
time_use["WeeklySchedule"].head(24)
```

## Reference

<details><summary>Columns of `Census tracts` (11)</summary>

- `Municipality code`
- `District code`
- `Census tract code`
- `Census tract full code`
- `Autonomous community code`
- `Average net household income (annual, EUR)`
- `Average net household income (monthly, EUR)`
- `Average net household income (monthly, 2010 EUR)`
- `Household income group`
- `Household income group label`
- `Autonomous community name`

</details>

<details><summary>Columns of `WeeklySchedule` (20)</summary>

- `Autonomous community code`
- `Household income group`
- `Day of week number`
- `Day of week`
- `Hour`
- `Hobbies and computing`
- `Household and family care`
- `Mass media`
- `Paid work`
- `Personal care`
- `Social life and entertainment`
- `Sports and outdoor activities`
- `Study`
- `Travel and unspecified`
- `Volunteer work and meetings`
- `occupancy`
- `Sleeping_share`
- `WithActivity_share`
- `NonOccupied_share`
- `Hour of week`

</details>

<details><summary>Columns of `HolidaySchedule` (7)</summary>

- `Autonomous community code`
- `Household income group`
- `Date`
- `Quarter`
- `Day of week number`
- `Day of week`
- `Free or holiday day probability (%)`

</details>

<details><summary>Columns of `WeeklyScheduleHouseholdOccupancy` (170)</summary>

- `Autonomous community code`
- `Household income group`
- `0`
- `1`
- `2`
- `3`
- `4`
- `5`
- `6`
- `7`
- `8`
- `9`
- `10`
- `11`
- `12`
- `13`
- `14`
- `15`
- `16`
- `17`
- `18`
- `19`
- `20`
- `21`
- `22`
- `23`
- `24`
- `25`
- `26`
- `27`
- `28`
- `29`
- `30`
- `31`
- `32`
- `33`
- `34`
- `35`
- `36`
- `37`
- `38`
- `39`
- `40`
- `41`
- `42`
- `43`
- `44`
- `45`
- `46`
- `47`
- `48`
- `49`
- `50`
- `51`
- `52`
- `53`
- `54`
- `55`
- `56`
- `57`
- `58`
- `59`
- `60`
- `61`
- `62`
- `63`
- `64`
- `65`
- `66`
- `67`
- `68`
- `69`
- `70`
- `71`
- `72`
- `73`
- `74`
- `75`
- `76`
- `77`
- `78`
- `79`
- `80`
- `81`
- `82`
- `83`
- `84`
- `85`
- `86`
- `87`
- `88`
- `89`
- `90`
- `91`
- `92`
- `93`
- `94`
- `95`
- `96`
- `97`
- `98`
- `99`
- `100`
- `101`
- `102`
- `103`
- `104`
- `105`
- `106`
- `107`
- `108`
- `109`
- `110`
- `111`
- `112`
- `113`
- `114`
- `115`
- `116`
- `117`
- `118`
- `119`
- `120`
- `121`
- `122`
- `123`
- `124`
- `125`
- `126`
- `127`
- `128`
- `129`
- `130`
- `131`
- `132`
- `133`
- `134`
- `135`
- `136`
- `137`
- `138`
- `139`
- `140`
- `141`
- `142`
- `143`
- `144`
- `145`
- `146`
- `147`
- `148`
- `149`
- `150`
- `151`
- `152`
- `153`
- `154`
- `155`
- `156`
- `157`
- `158`
- `159`
- `160`
- `161`
- `162`
- `163`
- `164`
- `165`
- `166`
- `167`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
