# `EducationAndEmploymentCensus`

**Education and employment census**

Educational attainment and labour-force status of the population, by census tract and year. Attainment is in four levels (primary or below, lower secondary, upper secondary and post-secondary non-tertiary, tertiary); labour-force status covers employed, unemployed, recipients of a disability or retirement pension, other inactive situations, and students. Both are crossed with sex and with place of birth.

**Source:** [Censo anual de población: nivel de formación y relación con la actividad (INE)](https://www.ine.es/dynt3/inebase/en/index.htm?padre=10608&capsel=10613)

```python
INE.EducationAndEmploymentCensus(wd, municipality_code=None, years=None, mode='relative')
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `Municipality` | 32,736 | 49 | 2021–2024 |
| `Districts` | 41,924 | 50 | 2021–2024 |
| `Census tracts` | 146,940 | 51 | 2021–2024 |

## Parameters

```
wd : str
    Working directory the downloaded data is cached under. The first call
    downloads from INE, later ones read the local copy.
municipality_code : str or list of str, optional
    Restrict the result to these municipality code(s).
years : list of int, optional
    Restrict the result to these years.
mode : {"relative", "absolute"}, default "relative"
    ``"relative"`` returns shares in percent (0-100), each of the population it
    actually describes — attainment of those aged 16 and over, unemployment of the
    active population, not of everybody. ``"absolute"`` returns head counts.
```

## Notes

- `mode="relative"` (the default) returns shares of the relevant population; `mode="absolute"` returns head counts instead.
- Shares are percentages (0-100), and each family of them is a share of the population it actually describes — attainment of those aged 16 and over, unemployment of the active population, not of everybody.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

education = INE.EducationAndEmploymentCensus(wd=wd, mode="relative")
education["Census tracts"].filter(like="Educational level").head()
```

## Reference

The levels hold the same variables, differing only in the codes that key them. `Census tracts` is the widest, at 51 columns:

<details><summary>Columns (51)</summary>

- `Country code`
- `Province code`
- `Municipality code`
- `District code`
- `Year`
- `Census tract code`
- `Population ~ Educational level:Primary education or below`
- `Population ~ Educational level:Lower secondary education or equivalent`
- `Population ~ Educational level:Upper secondary and post-secondary non-tertiary education`
- `Population ~ Educational level:Tertiary education`
- `Population ~ Sex:Males ~ Educational level:Primary education or below`
- `Population ~ Sex:Males ~ Educational level:Lower secondary education or equivalent`
- `Population ~ Sex:Males ~ Educational level:Upper secondary and post-secondary non-tertiary education`
- `Population ~ Sex:Males ~ Educational level:Tertiary education`
- `Population ~ Sex:Females ~ Educational level:Primary education or below`
- `Population ~ Sex:Females ~ Educational level:Lower secondary education or equivalent`
- `Population ~ Sex:Females ~ Educational level:Upper secondary and post-secondary non-tertiary education`
- `Population ~ Sex:Females ~ Educational level:Tertiary education`
- `Population ~ Birth origin:Spain ~ Educational level:Primary education or below`
- `Population ~ Birth origin:Spain ~ Educational level:Lower secondary education or equivalent`
- `Population ~ Birth origin:Spain ~ Educational level:Upper secondary and post-secondary non-tertiary education`
- `Population ~ Birth origin:Spain ~ Educational level:Tertiary education`
- `Population ~ Birth origin:Extranjero ~ Educational level:Primary education or below`
- `Population ~ Birth origin:Extranjero ~ Educational level:Lower secondary education or equivalent`
- `Population ~ Birth origin:Extranjero ~ Educational level:Upper secondary and post-secondary non-tertiary education`
- `Population ~ Birth origin:Extranjero ~ Educational level:Tertiary education`
- `Population ~ Labour force status:Employed`
- `Population ~ Labour force status:Unemployed`
- `Population ~ Labour force status:Recipient of disability, retirement, or early retirement pension`
- `Population ~ Labour force status:Other inactive situation`
- `Population ~ Labour force status:Student`
- `Population ~ Sex:Males ~ Labour force status:Employed`
- `Population ~ Sex:Males ~ Labour force status:Unemployed`
- `Population ~ Sex:Males ~ Labour force status:Recipient of disability, retirement, or early retirement pension`
- `Population ~ Sex:Males ~ Labour force status:Other inactive situation`
- `Population ~ Sex:Males ~ Labour force status:Student`
- `Population ~ Sex:Females ~ Labour force status:Employed`
- `Population ~ Sex:Females ~ Labour force status:Unemployed`
- `Population ~ Sex:Females ~ Labour force status:Recipient of disability, retirement, or early retirement pension`
- `Population ~ Sex:Females ~ Labour force status:Other inactive situation`
- `Population ~ Sex:Females ~ Labour force status:Student`
- `Population ~ Birth origin:Spain ~ Labour force status:Employed`
- `Population ~ Birth origin:Spain ~ Labour force status:Unemployed`
- `Population ~ Birth origin:Spain ~ Labour force status:Recipient of disability, retirement, or early retirement pension`
- `Population ~ Birth origin:Spain ~ Labour force status:Other inactive situation`
- `Population ~ Birth origin:Spain ~ Labour force status:Student`
- `Population ~ Birth origin:Extranjero ~ Labour force status:Employed`
- `Population ~ Birth origin:Extranjero ~ Labour force status:Unemployed`
- `Population ~ Birth origin:Extranjero ~ Labour force status:Recipient of disability, retirement, or early retirement pension`
- `Population ~ Birth origin:Extranjero ~ Labour force status:Other inactive situation`
- `Population ~ Birth origin:Extranjero ~ Labour force status:Student`

</details>

`Municipality` drops `District code`, `Census tract code`.

`Districts` drops `Census tract code`.


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
