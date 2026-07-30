import pandas as pd
from io import StringIO
import io
import os
import json
import gzip
import base64
import zipfile
import requests
import re
from html import escape as _html_escape
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import time
import numpy as np
import pickle
import unicodedata
import math
from scipy.interpolate import interp1d
import ast

# Generic utils
def get_links_that_contain(regexp, html):

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile(regexp)}):
        links.append(link.get('href'))

    return (links)


def extract_titles_and_ids(html):
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    for a_tag in soup.find_all("a", href=re.compile(r"/jaxi/dlgExport\.htm\?tpx=\d+")):
        match = re.search(r"tpx=(\d+)", a_tag["href"])
        if match:
            tpx_id = int(match.group(1))

            # Go to the parent <div class="additional"> or <li> and find the next <a class="titulo">
            parent_li = a_tag.find_parent("li")
            if parent_li:
                title_tag = parent_li.find("a", class_="titulo")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    data[title] = tpx_id

    return data

def is_number(s):
    if s is None or isinstance(s, float) and s != s:  # Check for None or NaN
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def request_with_retries(url, headers=None, tries=5, backoff=2.0, timeout=120, expect_csv=False):
    """
    GET a URL, retrying the transient failures the INE servers return every now and then
    (HTTP 5xx pages, throttling, dropped connections). When expect_csv is set, an HTML
    body served with a 200 status is also treated as a failed attempt, so that an error
    page never reaches pd.read_csv.
    """
    last_error = None
    for attempt in range(tries):
        if attempt > 0:
            time.sleep(backoff * (2 ** (attempt - 1)))
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            last_error = f"{type(e).__name__}: {e}"
            continue
        if r.status_code >= 500 or r.status_code == 429:
            last_error = f"HTTP {r.status_code}"
            continue
        if expect_csv and "html" in r.headers.get("Content-Type", "").lower():
            last_error = f"HTML response instead of CSV (HTTP {r.status_code})"
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f"Could not download {url} after {tries} attempts ({last_error})")


def fetch_data(url,separation=";",type=None):
    r = request_with_retries(url, expect_csv=True)
    r.encoding = 'utf-8'
    return pd.read_csv(StringIO(r.text), sep=separation, encoding="utf-8",thousands='.', decimal=',',dtype=type)


def aggregate(df,operations):
    for key in operations:
        df[key] = operations[key](df)
    return df


def rename(df, cols):
    return  df.rename(columns=cols,inplace=True)


operation_dict = {
    'aggregate': aggregate,
    'rename': rename
}


def RelationAutonomousCommunityAndProvince():
    df = pd.DataFrame([
        ("01", "Andalucía","04","Almería"),
        ("01", "Andalucía", "11", "Cádiz"),
        ("01", "Andalucía", "14", "Córdoba"),
        ("01", "Andalucía", "18", "Granada"),
        ("01", "Andalucía", "21", "Huelva"),
        ("01", "Andalucía", "23", "Jaén"),
        ("01", "Andalucía", "29", "Málaga"),
        ("01", "Andalucía", "41", "Sevilla"),
        ("02", "Aragón", "22", "Huesca"),
        ("02", "Aragón", "44", "Teruel"),
        ("02", "Aragón", "50", "Zaragoza"),
        ("03", "Asturias, Principado de", "33", "Asturias"),
        ("04", "Balears, Illes", "07", "Balears, Illes"),
        ("05", "Canarias", "35", "Palmas, Las"),
        ("05", "Canarias", "38", "Santa Cruz de Tenerife"),
        ("06", "Cantabria", "39", "Cantabria"),
        ("07", "Castilla y León", "05", "Ávila"),
        ("07", "Castilla y León", "09", "Burgos"),
        ("07", "Castilla y León", "24", "León"),
        ("07", "Castilla y León", "34", "Palencia"),
        ("07", "Castilla y León", "37", "Salamanca"),
        ("07", "Castilla y León", "40", "Segovia"),
        ("07", "Castilla y León", "42", "Soria"),
        ("07", "Castilla y León", "47", "Valladolid"),
        ("07", "Castilla y León", "49", "Zamora"),
        ("08", "Castilla-La Mancha", "02", "Albacete"),
        ("08", "Castilla-La Mancha", "13", "Ciudad Real"),
        ("08", "Castilla-La Mancha", "16", "Cuenca"),
        ("08", "Castilla-La Mancha", "19", "Guadalajara"),
        ("08", "Castilla-La Mancha", "45", "Toledo"),
        ("09", "Cataluña", "08", "Barcelona"),
        ("09", "Cataluña", "17", "Girona"),
        ("09", "Cataluña", "25", "Lleida"),
        ("09", "Cataluña", "43", "Tarragona"),
        ("10", "Comunitat Valenciana", "03", "Alicante/Alacant"),
        ("10", "Comunitat Valenciana", "12", "Castellón/Castelló"),
        ("10", "Comunitat Valenciana", "46", "Valencia/València"),
        ("11", "Extremadura", "06", "Badajoz"),
        ("11", "Extremadura", "10", "Cáceres"),
        ("12", "Galicia", "15", "Coruña, A"),
        ("12", "Galicia", "27", "Lugo"),
        ("12", "Galicia", "32", "Ourense"),
        ("12", "Galicia", "36", "Pontevedra"),
        ("13", "Madrid, Comunidad de", "28", "Madrid"),
        ("14", "Murcia, Región de", "30", "Murcia"),
        ("15", "Navarra, Comunidad Foral de", "31", "Navarra"),
        ("16", "País Vasco", "01", "Araba/Álava"),
        ("16", "País Vasco", "48", "Bizkaia"),
        ("16", "País Vasco", "20", "Gipuzkoa"),
        ("17", "Rioja, La", "26", "Rioja, La"),
        ("18", "Ceuta", "51", "Ceuta"),
        ("19", "Melilla", "52", "Melilla")
    ])
    df.columns = ["Autonomous community code", "Autonomous community name", "Province code", "Province name"]

    return df


def _parse_ine_number(values, spanish=True):
    """Parse INE numeric strings, which carry a locale-dependent thousands separator.

    The same table is served in two locales depending on the province: Spanish
    files write ``24.900`` (``.`` groups thousands, ``,`` is decimal) and English
    ones ``24,900`` (the other way round), so applying one convention to both
    silently divides the English values by a thousand.

    ``values`` must hold the raw text — a column pandas has already parsed as
    float has lost the information (``24.900`` becomes ``24.9``, whose string form
    no longer shows the dropped trailing digits). Unparseable entries, including
    INE's ``.`` and ``..`` suppression markers, become ``NaN``.
    """
    s = values.astype(str).str.strip()
    if spanish:
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    else:
        s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


# Gather functions for Spanish National Statistics datasets

def HouseholdIncomeDistributionAtlas(wd, municipality_code=None, years=None):
    """Household income distribution (Atlas de Distribución de Renta de los Hogares).

    Returns a dict with the ``"Census tracts"``, ``"Districts"`` and
    ``"Municipality"`` DataFrames, each holding one row per area and year with
    INE's income indicators (average/median income per person, per household and
    per consumption unit, income sources, and the share of the population below or
    above several fractions of the median).

    Besides the published indicators, every row carries an income band comparable
    across years and joinable with ``TimeUseSurvey``:

    - ``"Average household net income (2010 EUR)"``: the nominal average net
      household income deflated to the prices of _EET_INCOME_REFERENCE_YEAR (2010)
      with the annual mean of the general CPI (see ``ConsumerPriceIndex``).
    - ``"Household income group"`` / ``"Household income group label"``: that
      deflated income, monthly, bucketed into the four bands the Time Use Survey
      respondents answered in. Deflating first keeps a tract in the same group
      when its income only tracks inflation.

    Merging a tract onto its time-use schedules therefore needs no extra work::

        atlas = HouseholdIncomeDistributionAtlas(wd)["Census tracts"]
        weekly = TimeUseSurvey(wd)["WeeklySchedule"]
        atlas.merge(weekly, on=["Autonomous community code", "Household income group"])

    Parameters
    ----------
    wd : str
        Working directory the downloaded data is cached under.
    municipality_code : str or list of str, optional
        Restrict the result to these municipality code(s).
    years : list, optional
        Restrict the result to these years.
    """
    path = "INE/HouseholdIncomeDistributionAtlas"
    path = path_creator(path, wd)
    # _v3: caches built before the locale-aware parsing below hold income values
    # that are a thousand times too small for the provinces INE serves in English
    # (14, 19, 25 and 33), plus scattered truncated ones elsewhere, so they must
    # be rebuilt rather than reused.
    filename = f"{path}/df_v3.tsv"

    if not os.path.exists(filename):

        print("Reading the metadata to gather the INE Household Income Distribution Atlas", file=sys.stdout)
        req = request_with_retries('https://www.ine.es/dynt3/inebase/en/index.htm?padre=7132',
                                   headers={'User-Agent': 'Mozilla/5.0'})
        urls = get_links_that_contain("capsel", req.text)
        g_ids = []

        for url in urls:
            req = request_with_retries(f'https://www.ine.es/dynt3/inebase/en/index.htm{url}',
                                       headers={'User-Agent': 'Mozilla/5.0'})
            x = [re.search(r'(t=)(?P<x>\w+)(&L)', link).group('x') for link in
                 get_links_that_contain("Export", req.text)]
            g_ids.append(x)

        g_urls = [[f"https://www.ine.es/jaxiT3/files/t/en/csv_bd/{id}.csv?nocab=1" for id in ids] for ids in g_ids]
        g_df = pd.DataFrame()

        for urls in tqdm(g_urls, desc="Downloading files from INE by provinces..."):
            df = pd.DataFrame()
            for url in urls:
                r = request_with_retries(url, expect_csv=True)
                r.encoding = 'utf-8'
                # "Total" must be read as text: INE writes thousands separators, and
                # letting pandas infer the dtype turns '24.900' (24,900 €) into the
                # float 24.9, whose string form has already lost the trailing digits.
                df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", low_memory=False,
                                  dtype={"Total": str})
                df_["Municipality name"] = df_["Municipalities"].astype(str).str[6:]
                df_["Municipality code"] = df_["Municipalities"].astype(str).str[:5]
                df_["District code"] = df_["Districts"].astype(str).str[5:7]
                df_["Census tract code"] = df_["Sections"].astype(str).str[7:10]
                try:
                    time = "Periodo"
                    df_["Year"] = df_[time]

                except KeyError:
                    time = "Period"
                    df_["Year"] = df_[time]

                # The period column also identifies the locale of the file: INE serves
                # some provinces in Spanish ("Periodo", 24.900) and others in English
                # ("Period", 24,900), so the separators must be read accordingly.
                df_["Value"] = _parse_ine_number(df_["Total"], spanish=(time == "Periodo"))
                df_ = df_.sort_values(by='Value', na_position='last')

                df_ = df_.drop(columns=["Municipalities","Districts","Sections",time,"Total"])
                df_ = df_.drop_duplicates([col for col in df_.columns if col not in 'Value'])
                if "Nationality" in df_.columns:
                    df_["Nationality"] = df_["Nationality"].replace({"Extranjera":"Foreign"})
                if "Age ranges" in df_.columns:
                    df_["Age"] = df_["Age ranges"].replace({
                        "From 18 to 64 years old": "18-64",
                        "65 and over": ">64",
                        "Less than 18 years": "<18"
                    })
                    df_ = df_.drop(columns=["Age ranges"])
                df_ = pd.pivot(df_,
                         index=[col for col in df_.columns if col in
                                    ['Municipality name', 'Municipality code', 'District code', 'Census tract code', 'Year']],
                         columns= [col for col in df_.columns if col not in
                                    ['Municipality name', 'Municipality code', 'District code', 'Census tract code', 'Year', 'Value']],
                         values = "Value")
                df_ = df_.reset_index()
                df_.rename(columns={
                    "Tamaño medio del hogar": "Average size of households",
                    "Fuente de ingreso: otras prestaciones": "Source:Other benefits ~ Average per person gross income",
                    "Fuente de ingreso: otros ingresos": "Source:Other incomes ~ Average per person gross income",
                    "Fuente de ingreso: pensiones": "Source:Pension ~ Average per person gross income",
                    "Fuente de ingreso: prestaciones por desempleo": "Source:Unemployment benefits ~ Average per person gross income",
                    "Fuente de ingreso: salario": "Source:Salary ~ Average per person gross income",
                    "Porcentaje de hogares unipersonales": "Percentage of single-person households"
                })
                if isinstance(df_.columns, pd.MultiIndex):
                    subgroups = ["Nationality","Age","Sex"]
                    allcols = df_.columns.names
                    maincol = [col for col in allcols if col not in subgroups]
                    maincol.extend([col for col in allcols if col in subgroups])
                    df_.columns = df_.columns.reorder_levels(order=maincol)
                    df_.columns = [" ~ ".join([f"{level}:{value}" if level in subgroups else value
                                               for level, value in zip(df_.columns.names, cols)])
                                   if cols[0] !='' else cols[1] for cols in df_.columns.to_flat_index()]
                df_.columns = [cols.strip() for cols in df_.columns]

                df_.columns = [re.sub(" ~ Sex:Total","", cols) for cols in df_.columns]

                if len(df) == 0:
                    df = df_
                else:
                    merge_on = ['Municipality name', 'Municipality code', 'District code', 'Census tract code', 'Year']
                    df = pd.merge(
                        df,
                        df_[[col for col in df_.columns if ((col not in df.columns) or (col in merge_on))]],
                        on = merge_on)
                del(df_)

            g_df = pd.concat([g_df,df])
            del(df)

        g_df.to_csv(filename, sep="\t", index=False)

    else:
        g_df = pd.read_csv(filename, sep="\t", dtype={0:'str',1:'str',2:'str',3:'str'})
    if years != None:
        g_df = g_df[g_df['Year'].isin(years)]
    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    # Defragment g_df before adding columns: it is built from repeated
    # pd.concat calls in the download loop, which leaves it highly fragmented and
    # would trigger a PerformanceWarning on each column insert below. .copy()
    # rebuilds a single contiguous block.
    g_df = g_df.copy()
    g_df["Country code"] = "ES"
    g_df["Province code"] = g_df["Municipality code"].str[:2]
    _rel = RelationAutonomousCommunityAndProvince()
    _prov2caut = dict(zip(_rel["Province code"], _rel["Autonomous community code"]))
    _prov2cauname = dict(zip(_rel["Province code"], _rel["Autonomous community name"]))
    g_df["Autonomous community code"] = g_df["Province code"].map(_prov2caut)
    g_df["Autonomous community name"] = g_df["Province code"].map(_prov2cauname)

    # --- Household income group: join key with TimeUseSurvey -----------------
    # The EET income bands (_EET_INCOME_LABELS, defined with the Time Use Survey
    # below) are expressed in the euros of the survey, 2009-2010, whereas the
    # Atlas reports nominal income for each of its years. Each row's average net
    # household income is therefore deflated to _EET_INCOME_REFERENCE_YEAR prices
    # with the annual mean of the general CPI before being bucketed, so that a
    # tract is not pushed into a higher band by inflation alone and the resulting
    # group can be joined directly onto the TimeUseSurvey schedule tables.
    _cpi_by_year = (ConsumerPriceIndex(wd=wd)["National"]
                    .groupby("Year")["CPI 2015 base ~ Class:General"].mean())
    _base_cpi = _cpi_by_year.get(_EET_INCOME_REFERENCE_YEAR, np.nan)
    _income_at_reference_year = (
        pd.to_numeric(g_df["Average household net income"], errors="coerce") * _base_cpi /
        pd.to_numeric(g_df["Year"], errors="coerce").map(_cpi_by_year))
    g_df[f"Average household net income ({_EET_INCOME_REFERENCE_YEAR} EUR)"] = (
        _income_at_reference_year.round(2))
    g_df["Household income group"] = (
        (_income_at_reference_year / 12).map(_eet_income_band_from_monthly).astype("Int64"))
    g_df["Household income group label"] = g_df["Household income group"].map(_EET_INCOME_LABELS)

    municipality = g_df[pd.isna(g_df["District code"]) & pd.isna(g_df["Census tract code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["District code"]) & pd.isna(g_df["Census tract code"])]
    districts = districts[districts.columns[districts.notna().any()]]
    sections = g_df[-pd.isna(g_df["District code"]) & -pd.isna(g_df["Census tract code"])]
    sections = sections[sections.columns[sections.notna().any()]]

    return ({
        "Municipality": municipality,
        "Districts": districts,
        "Census tracts": sections
    })

def EducationAndEmploymentCensus(wd, municipality_code=None, years=None, mode="relative"):

    path = "INE/EducationAndEmploymentCensus"
    path = path_creator(path, wd)

    g_df = pd.DataFrame()
    province_codes = [i + 1 for i in list(range(52))]

    print("Reading the metadata to gather the INE education and employment census", file=sys.stdout)
    base_link = "https://www.ine.es/dynt3/inebase/es/index.htm"
    sections_link = "?padre=10613&capsel=10614"
    req = request_with_retries(f"{base_link}{sections_link}", headers={'User-Agent': 'Chrome/51.0.2704.103'})
    sections_link = get_links_that_contain("capsel", req.text)[-1]
    req = request_with_retries(f"{base_link}{sections_link}", headers={'User-Agent': 'Chrome/51.0.2704.103'})
    urls = get_links_that_contain("capsel", req.text)
    urls = urls[urls.index(sections_link) + 1:]
    g_ids = []

    for url in urls:
        req = request_with_retries(f'{base_link}{url}', headers={'User-Agent': 'Mozilla/5'})
        x = [re.search(r'(t=)(?P<x>\w+)(&L)', link).group('x') for link in
             get_links_that_contain("Export", req.text)]
        if x != []:
            g_ids.append(x)

    g_urls = [[f"https://www.ine.es/jaxi/files/t/es/csv_bd/{id}.csv?nocab=1" for id in ids] for ids in g_ids]

    for pc in tqdm(province_codes, desc="Downloading data from INE..."):
        filename = f"{path}/{pc-1}_{mode}_v2.parquet"

        if not os.path.exists(filename):
            # g_df = pd.DataFrame()
            # for urls in tqdm(g_urls, desc="Downloading files from INE..."):

            df = pd.DataFrame()

            urls = g_urls[pc-1]
            for url in urls:
                #url=urls[0]
                r = request_with_retries(url, expect_csv=True)
                r.encoding = 'utf-8'
                df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", dtype={3:'str',6:'str'})
                cols = df_.columns
                if all([col in cols for col in ['Provincias', 'Municipios', 'Secciones']]):
                    df_['Municipios'] = df_['Municipios'].fillna(df_['Provincias'])
                    df_['Sección censal'] = df_['Secciones'].str[0:10].fillna(df_['Municipios'])
                    df_ = df_.drop(columns=['Secciones', 'Provincias', 'Municipios'])
                    cols = df_.columns

                allcols = {
                    "Sección censal": "Location",
                    "Sexo": "Sex",
                    "Total": "Value",
                    "Periodo": "Year",
                    "Period": "Year",
                    "Nivel de formación alcanzado": "Educational level",
                    "País de nacimiento": "Birth origin",
                    "Relación con la actividad": "Labour force status"
                }

                df_ = df_.rename(columns={col: allcols[col] for col in cols})
                cols = df_.columns
                if "Sex" in cols:
                    df_["Sex"] = df_["Sex"].replace({
                        "Hombres": "Males",
                        "Mujeres": "Females",
                        "Total": "Total"
                    })

                if "Educational level" in df_.columns:
                    df_["Educational level"] = df_["Educational level"].replace({
                        "Total": "Total",
                        "Educación primaria e inferior": "Primary education or below",
                        "Primera etapa de Educación Secundaria y similar": "Lower secondary education or equivalent",
                        "Segunda etapa de Educación Secundaria y Educación Postsecundaria no Superior": "Upper secondary and post-secondary non-tertiary education",
                        "Educación superior": "Tertiary education"
                    })
                    df_ = df_[df_["Educational level"] != "Total"]

                if "Birth origin" in cols:
                    df_["Birth origin"] = df_["Birth origin"].replace({
                        "Total": "Total",
                        "España": "Spain",
                        "Extranjera": "Foreign country"
                    })
                    df_ = df_[df_["Birth origin"] != "Total"]

                if "Labour force status" in cols:
                    df_["Labour force status"] = df_["Labour force status"].replace({
                        "Total": "Total",
                        "Ocupado/a": "Employed",
                        "Parado/a": "Unemployed",
                        "Perceptor/a pensión de incapacidad, jubilación, prejubilación": "Recipient of disability, retirement, or early retirement pension",
                        "Otra situación de inactividad": "Other inactive situation",
                        "Estudiante": "Student"
                    })
                    if len(df_["Labour force status"].unique()) > 5:
                        df_ = df_[df_["Labour force status"] != "Total"]

                df_["Value name"] = "Population"
                df_["Value"] = pd.to_numeric(df_["Value"].astype(str).str.replace(',', '').str.replace('.', ''),
                                             errors="coerce")

                df_ = pd.pivot(df_,
                               index=[col for col in df_.columns if col in
                                      ['Location', 'Year']],
                               columns=[col for col in df_.columns if col not in
                                        ['Location', 'Year', 'Value']],
                               values="Value")
                subgroups = ["Sex", "Educational level", "Sex", "Birth origin", "Labour force status"]
                if isinstance(df_.columns, pd.MultiIndex):
                    allcols = df_.columns.names
                    maincol = [col for col in allcols if col not in subgroups]
                    maincol.extend([col for col in allcols if col in subgroups])
                    df_.columns = df_.columns.reorder_levels(order=maincol)
                    df_.columns = [" ~ ".join([f"{level}:{value}" if level in subgroups else f"{value}"
                                               for level, value in zip(df_.columns.names, cols)])
                                   if cols[1] != '' else cols[0] for cols in df_.columns.to_flat_index()]
                df_.columns = [cols.strip() for cols in df_.columns]

                for subgroup in subgroups:
                    df_.columns = [re.sub(f" ~ {subgroup}:Total", "", cols) for cols in df_.columns]

                if mode=="relative":
                    cols_vars = [",".join([col__.split(":")[0] for col__ in col_.split("~")]) for col_ in df_.columns]
                    df__ = []
                    for cols_vars_ in list(set(cols_vars)):
                        df__.append(df_[[x for x, y in zip(df_.columns, cols_vars) if y == cols_vars_]].div(
                            df_[[x for x, y in zip(df_.columns, cols_vars) if y == cols_vars_]].sum(axis=1), axis=0) * 100)
                    df_ = pd.concat(df__, axis=1)

                df_ = df_.reset_index()

                if len(df) > 0:
                    df = pd.merge(df, df_[
                        [col for col in df_.columns if col not in df.columns or col == "Location" or col == "Year"]],
                                  on=["Location", "Year"])
                else:
                    df = df_

                del df_

                # if len(g_df)>0:
                #     g_df = pd.concat([g_df,df])
                # else:
                #     g_df = df
                # del df

            df["Country code"] = "ES"
            df["Location"] = df["Location"].replace({"Total Nacional": ""})
            df["Province code"] = np.where(df["Location"].str[0].apply(is_number), df["Location"].str[0:2], np.nan)
            df["Municipality code"] = np.where(df["Location"].str[2].apply(is_number), df["Location"].str[0:5], np.nan)
            df["District code"] = np.where(df["Location"].str[5].apply(is_number), df["Location"].str[5:7], np.nan)
            df["Census tract code"] = np.where(df["Location"].str[7].apply(is_number), df["Location"].str[7:10], np.nan)
            df = df.drop(columns=["Location"])

            agg_cols = [
                col for col in df.columns
                if col not in ["Country code", "Province code", "Municipality code", "District code", "Census tract code",
                               "Year"]
            ]

            if mode == "relative":
                # For percentages or relative values
                district = (
                    df.groupby(["Country code", "Province code", "Municipality code", "District code", "Year"])[
                        agg_cols]
                    .mean()
                )
            else:  # default to absolute counts
                district = (
                    df.groupby(["Country code", "Province code", "Municipality code", "District code", "Year"])[
                        agg_cols]
                    .sum()
                )

            district["Census tract code"] = np.nan
            district = district.set_index("Census tract code", append=True)
            district = district.reset_index()
            df = pd.concat([df[district.columns], district])

            df.to_parquet(filename)
            del df

        df = pd.read_parquet(filename)
        g_df = pd.concat([g_df, df])

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    g_df["Country code"] = "ES"
    g_df["Province code"] = g_df["Municipality code"].str[:2]
    if years != None:
        g_df = g_df[g_df['Year'].isin(years)]
    municipality = g_df[pd.isna(g_df["District code"]) & pd.isna(g_df["Census tract code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["District code"]) & pd.isna(g_df["Census tract code"])]
    districts = districts[districts.columns[districts.notna().any()]]
    sections = g_df[-pd.isna(g_df["District code"]) & -pd.isna(g_df["Census tract code"])]
    sections = sections[sections.columns[sections.notna().any()]]

    return ({
        "Municipality": municipality.reset_index(drop=True),
        "Districts": districts.reset_index(drop=True),
        "Census tracts": sections.reset_index(drop=True)
    })


def PopulationCensus(wd, municipality_code=None, years=None):

    path = "INE/PopulationCensus"
    path = path_creator(path, wd)

    g_df = pd.DataFrame()
    province_codes = [i + 1 for i in list(range(52))]

    print("Reading the metadata to gather the INE population census", file=sys.stdout)
    base_link = "https://www.ine.es/dynt3/inebase/es/index.htm"
    sections_link = "?padre=11100"
    req = request_with_retries(f"{base_link}{sections_link}", headers={'User-Agent': 'Chrome/51.0.2704.103'})
    sections_link = get_links_that_contain("capsel", req.text)[-1]
    req = request_with_retries(f"{base_link}{sections_link}", headers={'User-Agent': 'Chrome/51.0.2704.103'})
    urls = get_links_that_contain("capsel", req.text)
    urls = urls[urls.index(sections_link) + 1:]
    g_ids = []

    for url in urls:
        req = request_with_retries(f'{base_link}{url}', headers={'User-Agent': 'Mozilla/5'})
        x = [re.search(r'(t=)(?P<x>\w+)(&L)', link).group('x') for link in
             get_links_that_contain("Export", req.text)]
        if x != []:
            g_ids.append(x)

    g_urls = [[f"https://www.ine.es/jaxi/files/t/es/csv_bd/{id}.csv?nocab=1" for id in ids] for ids in g_ids]

    for pc in tqdm(province_codes, desc="Downloading data from INE..."):
        filename = f"{path}/{pc-1}_v2.parquet"

        if not os.path.exists(filename):
            # g_df = pd.DataFrame()
            # for urls in tqdm(g_urls, desc="Downloading files from INE..."):

            df = pd.DataFrame()

            urls = g_urls[pc-1]
            for url in urls:
                #url=urls[0]
                r = request_with_retries(url, expect_csv=True)
                r.encoding = 'utf-8'
                df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", dtype={3:'str',6:'str'})
                df_ = df_.rename(columns={"ï»¿Provincias": "Provincias"})
                cols = df_.columns
                if all([col in cols for col in ['Provincias', 'Municipios', 'Secciones']]):
                    df_['Municipios'] = df_['Municipios'].fillna(df_['Provincias'])
                    df_['Sección censal'] = df_['Secciones'].str[0:10].fillna(df_['Municipios'])
                    df_ = df_.drop(columns = ['Secciones', 'Provincias', 'Municipios'])
                    cols = df_.columns

                allcols = {
                    "Sección censal": "Location",
                    "Sexo": "Sex",
                    "Lugar de nacimiento": "Birth origin",
                    "País de nacimiento": "Birth country",
                    "Nacionalidad": "Nationality",
                    "País de nacionalidad": "Nationality",
                    "Relación entre lugar de nacimiento y lugar de residencia": "Birth origin in Spain",
                    "Total": "Value",
                    "Periodo": "Year",
                    "Edad": "Age"
                }

                df_ = df_.rename(columns={col:allcols[col] for col in cols})
                cols = df_.columns
                if "Sex" in cols:
                    df_["Sex"] = df_["Sex"].replace({
                        "Hombres": "Males",
                        "Mujeres": "Females",
                        "Total": "Total"
                    })

                if "Birth country" in df_.columns:
                    df_["Birth country"] = df_["Birth country"].replace({
                        "Total": "Total",
                        "España": "Spain",
                        "Francia": "France",
                        "Reino Unido": "United Kingdom",
                        "Rumanía": "Romania",
                        "Ucrania": "Ukraine",
                        "Otros países de Europa": "Other European countries",
                        "Marruecos": "Morocco",
                        "Otros países de África": "Other African countries",
                        "Cuba": "Cuba",
                        "República Dominicana": "Dominican Republic",
                        "Argentina": "Argentina",
                        "Bolivia": "Bolivia",
                        "Colombia": "Colombia",
                        "Ecuador": "Ecuador",
                        "Perú": "Peru",
                        "Venezuela": "Venezuela",
                        "Otros países de América": "Other American countries",
                        "China": "China",
                        "Otros países de Asia": "Other Asian countries",
                        "Oceanía": "Oceania"
                    })
                    df_ = df_[df_["Birth country"] != "Total"]

                if "Birth origin" in cols:
                    df_["Birth origin"] = df_["Birth origin"].replace({
                        "Total": "Total",
                        "España": "Spain",
                        "Extranjera": "Foreign country"
                    })
                    df_ = df_[df_["Birth origin"] != "Total"]

                if "Nationality" in cols:
                    df_["Nationality"] = df_["Nationality"].replace({
                        "Total": "Total",
                        "Española": "Spanish",
                        "Extranjera": "Foreign",
                        "Francia": "French",
                        "Reino Unido": "British",
                        "Rumanía": "Romanian",
                        "Ucrania": "Ukrainian",
                        "Otros países de Europa": "Other European nationalities",
                        "Marruecos": "Moroccan",
                        "Otros países de África": "Other African nationalities",
                        "Cuba": "Cuban",
                        "República Dominicana": "Dominican",
                        "Argentina": "Argentinian",
                        "Bolivia": "Bolivian",
                        "Colombia": "Colombian",
                        "Ecuador": "Ecuadorian",
                        "Perú": "Peruvian",
                        "Venezuela": "Venezuelan",
                        "Otros países de América": "Other American nationalities",
                        "China": "Chinese",
                        "Otros países de Asia": "Other Asian nationalities",
                        "Oceanía": "Oceanian",
                        "Apátridas": "Stateless"
                    })
                    if len(df_["Nationality"].unique())>5:
                        df_ = df_[df_["Nationality"]!="Total"]


                if "Birth origin in Spain" in cols:
                    df_["Birth origin in Spain"] = df_["Birth origin in Spain"].replace({
                        "Total": "Total",
                        "Mismo municipio al de residencia": "Born in the same municipality",
                        "Distinto municipio de la misma provincia": "Born in a municipality of the same province",
                        "Distinta provincia de la misma comunidad": "Born in a municipality of the same autonomous community",
                        "Distinta comunidad": "Born in a municipality of another autonomous community",
                        "Nacido en el extranjero": "Born in another country"
                    })
                    df_ = df_[df_["Birth origin in Spain"] != "Total"]

                if "Age" in cols:
                    df_["Age"] = df_["Age"].str.replace("Todas las edades","Total").\
                        str.replace("De ","").\
                        str.replace(" años","").\
                        str.replace(" a ","-").\
                        str.replace(" y más","").\
                        str.replace("100",">99")
                    df_ = df_[df_["Age"] != "Total"]

                df_["Value name"] = "Population"
                df_["Value"] = pd.to_numeric(df_["Value"].astype(str).str.replace(',', '').str.replace('.', ''), errors="coerce")

                df_ = pd.pivot(df_,
                               index=[col for col in df_.columns if col in
                                      ['Location', 'Year']],
                               columns=[col for col in df_.columns if col not in
                                        ['Location', 'Year', 'Value']],
                               values="Value")
                subgroups = ["Nationality", "Age", "Sex", "Birth country", "Birth origin", "Birth origin in Spain"]
                if isinstance(df_.columns, pd.MultiIndex):
                    allcols = df_.columns.names
                    maincol = [col for col in allcols if col not in subgroups]
                    maincol.extend([col for col in allcols if col in subgroups])
                    df_.columns = df_.columns.reorder_levels(order=maincol)
                    df_.columns = [" ~ ".join([f"{level}:{value}" if level in subgroups else f"{value}"
                                               for level, value in zip(df_.columns.names, cols)])
                                   if cols[1]!='' else cols[0] for cols in df_.columns.to_flat_index()]
                df_.columns = [cols.strip() for cols in df_.columns]

                for subgroup in subgroups:
                    df_.columns = [re.sub(f" ~ {subgroup}:Total","", cols) for cols in df_.columns]

                df_ = df_.reset_index()

                if len(df)>0:
                    df = pd.merge(df,df_[[col for col in df_.columns if col not in df.columns or col=="Location" or col=="Year"]],
                                  on=["Location","Year"])
                else:
                    df = df_

                del df_

            # if len(g_df)>0:
            #     g_df = pd.concat([g_df,df])
            # else:
            #     g_df = df
            # del df

            df["Country code"] = "ES"
            df["Location"] = df["Location"].replace({"Total Nacional":""})
            df["Province code"] = np.where(df["Location"].str[0].apply(is_number), df["Location"].str[0:2], np.nan)
            df["Municipality code"] = np.where(df["Location"].str[2].apply(is_number), df["Location"].str[0:5], np.nan)
            df["District code"] = np.where(df["Location"].str[5].apply(is_number), df["Location"].str[5:7], np.nan)
            df["Census tract code"] = np.where(df["Location"].str[7].apply(is_number), df["Location"].str[7:10], np.nan)
            df = df.drop(columns=["Location"])

            district = df.groupby(["Country code", "Province code", "Municipality code", "District code", "Year"])[
                [col for col in df.columns if col not in ["Country code", "Province code", "Municipality code", "District code","Census tract code","Year"]]
                ].sum()
            district["Census tract code"] = np.nan
            district = district.set_index("Census tract code", append=True)
            district = district.reset_index()
            df = pd.concat([df[district.columns], district])

            df.to_parquet(filename)
            del df

        df = pd.read_parquet(filename)
        g_df = pd.concat([g_df, df])

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    g_df["Country code"] = "ES"
    g_df["Province code"] = g_df["Municipality code"].str[:2]
    if years != None:
        g_df = g_df[g_df['Year'].isin(years)]
    municipality = g_df[pd.isna(g_df["District code"]) & pd.isna(g_df["Census tract code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["District code"]) & pd.isna(g_df["Census tract code"])]
    districts = districts[districts.columns[districts.notna().any()]]
    sections = g_df[-pd.isna(g_df["District code"]) & -pd.isna(g_df["Census tract code"])]
    sections = sections[sections.columns[sections.notna().any()]]

    return ({
        "Municipality": municipality.reset_index(drop=True),
        "Districts": districts.reset_index(drop=True),
        "Census tracts": sections.reset_index(drop=True)
    })


_C2021_INDICATORS_URL = "https://www.ine.es/censos2021/C2021_Indicadores.csv"

# Indicators published in C2021_Indicadores.csv, in the order INE writes them. Each
# entry holds the English column name, how the indicator aggregates from census tracts
# up to districts and municipalities, and the factor that turns the published value into
# the unit used here (INE writes the shares as proportions, the library as percentages).
#
# Counts are summed; the rest are rates, which must be averaged weighting by the
# population each is a share of. INE does not publish those denominators, so they are
# rebuilt from the indicators themselves: the population aged 16 and over is
# t1_1 * (t4_2 + t4_3) and the active population is that times t12_1.
_C2021_INDICATORS = {
    "t1_1": ("Population", "sum", 1),
    "t2_1": ("Percentage of population ~ Sex:Females", "population", 100),
    "t2_2": ("Percentage of population ~ Sex:Males", "population", 100),
    "t3_1": ("Average age", "population", 1),
    "t4_1": ("Percentage of population ~ Age:<16", "population", 100),
    "t4_2": ("Percentage of population ~ Age:16-64", "population", 100),
    "t4_3": ("Percentage of population ~ Age:>64", "population", 100),
    "t5_1": ("Percentage of population ~ Nationality:Foreign", "population", 100),
    "t6_1": ("Percentage of population ~ Birth origin:Foreign country", "population", 100),
    "t7_1": ("Percentage of population aged 16 and over ~ Current studies:Higher education",
             "population 16 and over", 100),
    "t8_1": ("Percentage of population aged 16 and over ~ Current studies:University education",
             "population 16 and over", 100),
    "t9_1": ("Percentage of population aged 16 and over ~ Educational level:Tertiary education",
             "population 16 and over", 100),
    "t10_1": ("Percentage of active population ~ Labour force status:Unemployed",
              "active population", 100),
    "t11_1": ("Percentage of population aged 16 and over ~ Labour force status:Employed",
              "population 16 and over", 100),
    "t12_1": ("Percentage of population aged 16 and over ~ Labour force status:Active",
              "population 16 and over", 100),
    "t13_1": ("Percentage of population aged 16 and over ~ Labour force status:Recipient of disability pension",
              "population 16 and over", 100),
    "t14_1": ("Percentage of population aged 16 and over ~ Labour force status:Recipient of retirement pension",
              "population 16 and over", 100),
    "t15_1": ("Percentage of population aged 16 and over ~ Labour force status:Other inactive situation",
              "population 16 and over", 100),
    "t16_1": ("Percentage of population aged 16 and over ~ Labour force status:Student",
              "population 16 and over", 100),
    "t17_1": ("Percentage of population ~ Marital status:Single", "population", 100),
    "t17_2": ("Percentage of population ~ Marital status:Married", "population", 100),
    "t17_3": ("Percentage of population ~ Marital status:Widowed", "population", 100),
    "t17_4": ("Percentage of population ~ Marital status:Not stated", "population", 100),
    "t17_5": ("Percentage of population ~ Marital status:Legally separated or divorced", "population", 100),
    "t18_1": ("Dwellings", "sum", 1),
    "t19_1": ("Dwellings ~ Dwelling type:Main", "sum", 1),
    "t19_2": ("Dwellings ~ Dwelling type:Non-main", "sum", 1),
    "t20_1": ("Main dwellings ~ Tenure:Owned", "sum", 1),
    "t20_2": ("Main dwellings ~ Tenure:Rented", "sum", 1),
    "t20_3": ("Main dwellings ~ Tenure:Other tenure", "sum", 1),
    "t21_1": ("Households", "sum", 1),
    "t22_1": ("Households ~ Household size:1 person", "sum", 1),
    "t22_2": ("Households ~ Household size:2 persons", "sum", 1),
    "t22_3": ("Households ~ Household size:3 persons", "sum", 1),
    "t22_4": ("Households ~ Household size:4 persons", "sum", 1),
    "t22_5": ("Households ~ Household size:5 or more persons", "sum", 1),
}

_C2021_LOCATION_COLUMNS = ["Country code", "Autonomous community code", "Autonomous community name",
                           "Province code", "Municipality code", "District code", "Census tract code", "Year"]


def _c2021_aggregate(df, group_columns):
    """Aggregate the 2021 census indicators from census tracts up to a coarser level.

    Counts are summed, and each rate is averaged over the tracts weighting by the
    population it is a share of, so that a district figure means the same thing as the
    tract figures it is built from. Tracts INE suppresses (see
    ``DwellingsAndPopulationCensus``) carry no indicators, so they are left out of both
    the numerator and the weight of every rate they are missing, and the aggregate is
    the one of the tracts that were published.
    """
    weights = pd.DataFrame(index=df.index)
    weights["population"] = df["Population"]
    weights["population 16 and over"] = df["Population"] * (
        df["Percentage of population ~ Age:16-64"] + df["Percentage of population ~ Age:>64"]) / 100
    weights["active population"] = weights["population 16 and over"] * \
        df["Percentage of population aged 16 and over ~ Labour force status:Active"] / 100

    names = [name for name, _, _ in _C2021_INDICATORS.values()]
    counts = [name for name, how, _ in _C2021_INDICATORS.values() if how == "sum"]
    groups = [df[col] for col in group_columns]

    agg = df.groupby(group_columns, dropna=False)[counts].sum(min_count=1)
    for name, how, _ in _C2021_INDICATORS.values():
        if how == "sum":
            continue
        weight = weights[how].where(df[name].notna())
        agg[name] = ((df[name] * weight).groupby(groups).sum(min_count=1) /
                     weight.groupby(groups).sum(min_count=1))

    agg = agg.reset_index()
    return agg[[col for col in group_columns] + names]


def DwellingsAndPopulationCensus(wd, municipality_code=None, years=None):
    """Population and dwellings census 2021 (Censos de Población y Viviendas 2021).

    Returns a dict with the ``"Census tracts"``, ``"Districts"`` and ``"Municipality"``
    DataFrames, each holding one row per area with the indicators INE publishes in
    ``C2021_Indicadores.csv``: population counts and its breakdown by sex, age,
    nationality, birth origin, education, labour force status and marital status,
    together with the dwelling, tenure and household size counts.

    Only the census-tract table is published by INE; the district and municipality ones
    are aggregated here. Counts are summed and shares are averaged weighting by the
    population each is a share of (see ``_c2021_aggregate``), so every level is read the
    same way.

    Shares are given as percentages (0-100), unlike the source file, which writes them
    as proportions, so that they match the rest of the library. ``"Average age"`` is
    left in years.

    INE suppresses the indicators of the smallest census tracts for statistical
    confidentiality: those rows keep their ``"Population"`` and have ``NaN`` everywhere
    else, and they are skipped when the district and municipality figures are built.

    The census is a single 2021 edition, so ``"Year"`` is always 2021; ``years`` is
    accepted for consistency with the rest of the library.

    Parameters
    ----------
    wd : str
        Working directory the downloaded data is cached under.
    municipality_code : str or list of str, optional
        Restrict the result to these municipality code(s).
    years : list, optional
        Restrict the result to these years.
    """
    path = "INE/DwellingsAndPopulationCensus"
    path = path_creator(path, wd)

    filename = f"{path}/df.parquet"

    if not os.path.exists(filename):

        print("Downloading the INE 2021 population and dwellings census", file=sys.stdout)
        r = request_with_retries(_C2021_INDICATORS_URL, headers={'User-Agent': 'Mozilla/5.0'}, expect_csv=True)
        r.encoding = 'utf-8'
        # The geographic codes are read as text: they are zero-padded, and INE writes the
        # municipality as province + municipality in two separate columns.
        df = pd.read_csv(StringIO(r.text), sep=",", encoding="utf-8",
                         dtype={"ccaa": 'str', "cpro": 'str', "cmun": 'str', "dist": 'str', "secc": 'str'})
        df = df.rename(columns=lambda col: col.strip().lstrip("﻿").lower())

        df["Country code"] = "ES"
        df["Autonomous community code"] = df["ccaa"]
        df["Province code"] = df["cpro"]
        df["Municipality code"] = df["cpro"] + df["cmun"]
        df["District code"] = df["dist"]
        df["Census tract code"] = df["secc"]
        df["Year"] = 2021

        for code, (name, _, scale) in _C2021_INDICATORS.items():
            df[name] = pd.to_numeric(df[code], errors="coerce") * scale

        df = df[[col for col in _C2021_LOCATION_COLUMNS if col != "Autonomous community name"] +
                [name for name, _, _ in _C2021_INDICATORS.values()]]

        df.to_parquet(filename, index=False)

    else:
        df = pd.read_parquet(filename)

    _rel = RelationAutonomousCommunityAndProvince()
    _caut2cauname = dict(zip(_rel["Autonomous community code"], _rel["Autonomous community name"]))
    df["Autonomous community name"] = df["Autonomous community code"].map(_caut2cauname)

    if years != None:
        df = df[df['Year'].isin(years)]
    if municipality_code is not None:
        if type(municipality_code) == str:
            df = df[(df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            df = df[df["Municipality code"].isin(municipality_code)]

    sections = df[_C2021_LOCATION_COLUMNS + [name for name, _, _ in _C2021_INDICATORS.values()]]
    districts = _c2021_aggregate(df, [col for col in _C2021_LOCATION_COLUMNS if col != "Census tract code"])
    municipality = _c2021_aggregate(df, [col for col in _C2021_LOCATION_COLUMNS
                                         if col not in ("District code", "Census tract code")])

    return ({
        "Municipality": municipality.reset_index(drop=True),
        "Districts": districts.reset_index(drop=True),
        "Census tracts": sections.reset_index(drop=True)
    })


# =============================================================================
# Empty and secondary dwellings (censuses 2001, 2011 and 2021)
# =============================================================================

# The three censuses do not classify unoccupied dwellings the same way, and the break
# is not a matter of wording: it changes what is being counted.
#
# 2001 and 2011 were field censuses. A census agent visited the building and sorted
# every family dwelling into main (somebody's usual residence), secondary (used
# occasionally, e.g. holidays) or empty (available but unused). 2001 adds a fourth
# residual class, "other type" of non-main dwelling, which 2011 drops.
#
# 2021 is built from administrative registers alone, so there is nobody to ask whether
# a dwelling is a second home. INE replaced that judgement with two independent
# classifications, and this function returns both:
#
#   * by type of use, from the residence register: main / non-main. "Non-main" merges
#     what used to be secondary and empty, and cannot be split back.
#   * by degree of use, from the yearly electricity consumption of the dwelling:
#     empty (no supply contract, or less than a local 15-days-a-year equivalent),
#     very low consumption (up to 250 kWh), sporadic use (251-750 kWh, roughly one to
#     three months a year, the closest thing to the old "secondary") and regular use
#     (the rest). The four classes partition the total.
#
# So "% empty" is comparable across the three censuses only in spirit, and the 2021
# "sporadic use" share is an electricity-based proxy for the old "secondary" share,
# not the same variable measured again. Both are returned under distinct column
# prefixes ("Dwelling type:" and "Electricity use:") to keep that visible.
#
# Municipal coverage differs too, and follows from the same methodology:
#   2001  every municipality (full field census).
#   2011  main dwellings for every municipality, but the secondary/empty split only
#         for municipalities over 2,000 inhabitants; below that the 2011 census was a
#         sample and INE does not publish the breakdown.
#   2021  main/non-main for every municipality, but the electricity classification
#         only for the 3,139 municipalities INE publishes it for (those over 1,000
#         inhabitants, ~97% of the population). The remainder is only released
#         aggregated per province, under codes like "01999 Resto de Araba/Álava",
#         which are dropped here because they are not municipalities.
#
# Municipality codes are the ones each census was published with, so the handful of
# municipalities created, merged or renamed between 2001 and 2021 do not line up
# across years; INE's https://www.ine.es/intercensal/ documents those alterations.

# 2001: single Excel file holding "Recuento de viviendas de cada clase" for every
# municipality, from the 2001 census results system (Resultados definitivos).
_DWELLING_USE_2001_URL = "https://www.ine.es/sdc/es/tablas/nacional/V1_M.xls"

# 2011: the municipal results of the 2011 census. The dwelling-type breakdown is
# published only for municipalities over 2,000 inhabitants (10mun00), so the totals of
# the complete municipality list (9mun00) are read as well.
_DWELLING_USE_2011_TYPE_URL = ("https://www.ine.es/jaxi/files/_px/es/csv_bdsc/t20/e244/viviendas/p06/l0/"
                               "10mun00.csv_bdsc?nocab=1")
_DWELLING_USE_2011_TOTAL_URL = ("https://www.ine.es/jaxi/files/_px/es/csv_bdsc/t20/e244/viviendas/p06/l0/"
                                "9mun00.csv_bdsc?nocab=1")

# 2011, autonomous communities and provinces. The municipal tables above cannot be
# added up to these: they only break down the municipalities over 2,000 inhabitants,
# whereas this one covers the whole territory.
_DWELLING_USE_2011_REGIONAL_URL = ("https://www.ine.es/jaxi/files/_px/es/csv_bdsc/t20/e244/viviendas/p01/l0/"
                                   "01010a.csv_bdsc?nocab=1")

# 2021: "Total viviendas familiares convencionales por tipo de vivienda" (table 59525)
# and "Viviendas según su intensidad de uso" (table 59531).
_DWELLING_USE_2021_TYPE_URL = "https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/59525.csv?nocab=1"
_DWELLING_USE_2021_USE_URL = "https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/59531.csv?nocab=1"

# Counts returned, in reading order. "Dwellings" is the denominator of every share.
_DWELLING_USE_COUNTS = [
    "Dwellings",
    "Dwellings ~ Dwelling type:Main",
    "Dwellings ~ Dwelling type:Non-main",
    "Dwellings ~ Dwelling type:Secondary",
    "Dwellings ~ Dwelling type:Empty",
    "Dwellings ~ Dwelling type:Other non-main",
    "Dwellings ~ Electricity use:Empty",
    "Dwellings ~ Electricity use:Very low consumption",
    "Dwellings ~ Electricity use:Sporadic use",
    "Dwellings ~ Electricity use:Regular use",
]

# The bridge between the two classifications, so that a single series can be read across
# the three censuses. Each census fills these from whichever classification it publishes:
#
#   Comparable use     2001 / 2011 (field census)          2021 (electricity)
#   ----------------   ---------------------------------   ---------------------------
#   Main               Dwelling type:Main                  Electricity use:Regular use
#   Secondary          Dwelling type:Secondary             Electricity use:Very low
#                      (+ Other non-main, in 2001)         consumption + Sporadic use
#   Empty              Dwelling type:Empty                 Electricity use:Empty
#
# Two things this alignment does, both deliberate:
#
# * 2021 "very low consumption" (up to 250 kWh, about a month of use) is counted as
#   secondary rather than empty. It sits between the two, and a dwelling used a month a
#   year is what the earlier censuses would have recorded as a second home, not as an
#   unoccupied one. Read alone, "sporadic use" would understate secondary dwellings.
# * 2001's "other type" of non-main dwelling is counted as secondary, which is what INE
#   itself does when it publishes the 2001-2011 comparison: 3,360,631 + 292,332 =
#   3,652,963, the secondary figure of its own series. 2011 has no such residual class.
#
# The three classes partition the total in every census, so the shares always add to 100.
#
# This is a bridge, not an identity. The 2021 figures come from electricity meters and
# the earlier ones from a census agent's judgement at the door, so a change between 2011
# and 2021 in any of these three lines mixes a real change in use with the change of
# instrument — most visibly in tourist municipalities, where a second home occupied for a
# full summer consumes well over 750 kWh and lands in "main". The classification each
# census actually published is kept alongside, under "Dwelling type:" and
# "Electricity use:", so the raw figures are always one column away.
# Each class names the columns it is built from under either classification, as
# (required, optional): a class is only available where every required column is, and the
# optional ones are added when the census happens to publish them. The electricity
# classification wins wherever it exists, which is 2021 and only 2021 — that census also
# publishes main/non-main, but those come from the residence register and would not
# partition the total alongside the electricity-based secondary and empty counts.
_DWELLING_USE_COMPARABLE = {
    "Dwellings ~ Comparable use:Main": {
        "field": (["Dwellings ~ Dwelling type:Main"], []),
        "electricity": (["Dwellings ~ Electricity use:Regular use"], []),
    },
    "Dwellings ~ Comparable use:Secondary": {
        # 2001 is the only census with an "other type" of non-main dwelling, so it is
        # optional: its absence must not blank the 2011 secondary count.
        "field": (["Dwellings ~ Dwelling type:Secondary"], ["Dwellings ~ Dwelling type:Other non-main"]),
        "electricity": (["Dwellings ~ Electricity use:Very low consumption",
                         "Dwellings ~ Electricity use:Sporadic use"], []),
    },
    "Dwellings ~ Comparable use:Empty": {
        "field": (["Dwellings ~ Dwelling type:Empty"], []),
        "electricity": (["Dwellings ~ Electricity use:Empty"], []),
    },
}

_DWELLING_USE_COMPARABLE_COUNTS = list(_DWELLING_USE_COMPARABLE)

_DWELLING_USE_LOCATION_COLUMNS = ["Country code", "Autonomous community code", "Autonomous community name",
                                  "Province code", "Municipality code", "Year"]

# Column positions of the 2001 Excel sheet. The file is a SAS export with the header
# spread over three merged rows, so the counts are read by position and the header text
# is checked instead (see _dwelling_use_2001).
_C2001_DWELLING_COLUMNS = {
    3: "Dwellings",                                  # 2    Total viviendas familiares
    4: "Dwellings ~ Dwelling type:Main",             # 2.1  Total viviendas principales
    7: "Dwellings ~ Dwelling type:Non-main",         # 2.2  Total viviendas no principales
    8: "Dwellings ~ Dwelling type:Secondary",        # 2.21 Viviendas secundarias
    9: "Dwellings ~ Dwelling type:Empty",            # 2.22 Viviendas vacías
    10: "Dwellings ~ Dwelling type:Other non-main",  # 2.23 Otro tipo
}

_C2011_DWELLING_TYPES = {
    "2 Total viviendas familiares (2.1+2.2)": "Dwellings",
    "2.1 Total viviendas principales (2.11+2.12)": "Dwellings ~ Dwelling type:Main",
    "2.2 Total viviendas no principales (2.21+2.22)": "Dwellings ~ Dwelling type:Non-main",
    "2.21 Viviendas secundarias": "Dwellings ~ Dwelling type:Secondary",
    "2.22 Viviendas vacias": "Dwellings ~ Dwelling type:Empty",
}

_C2011_DWELLING_TOTALS = {
    "2 Total viviendas familiares": "Dwellings",
    "2.1 Total viviendas principales": "Dwellings ~ Dwelling type:Main",
}

_C2021_DWELLING_TYPES = {
    "Total": "Dwellings",
    "Vivienda principal": "Dwellings ~ Dwelling type:Main",
    "Vivienda no principal": "Dwellings ~ Dwelling type:Non-main",
}

# Electricity-use classes of table 59531. The table also breaks "uso esporádico" into
# its two kWh bands and lists every band above 750 kWh separately; those are summed
# into "Regular use" rather than returned one by one.
_C2021_DWELLING_USES = {
    "Viviendas totales": "Dwellings",
    "Viviendas vacías": "Dwellings ~ Electricity use:Empty",
    "Viviendas con bajo consumo": "Dwellings ~ Electricity use:Very low consumption",
    "Viviendas de uso esporádico": "Dwellings ~ Electricity use:Sporadic use",
    "Mediana consumo anual": "Median annual electricity consumption (kWh)",
}


def _dwelling_use_municipal_table(url, category_column, categories, municipality_column):
    """Read one of the INE dwelling tables and pivot it to one row per municipality.

    All of them are published in the same long shape — a municipality label of the form
    ``"08001  Abrera"``, a category and a value — differing only in the column names and
    in the category labels, which ``categories`` maps to the returned column names.
    Rows of a coarser level (national, province, and the ``"PP999 Resto de ..."``
    aggregates of table 59531) do not carry a municipality code and are dropped.
    """
    r = request_with_retries(url, headers={'User-Agent': 'Mozilla/5.0'}, expect_csv=True)
    r.encoding = 'utf-8'
    df = pd.read_csv(StringIO(r.text), sep=";", encoding="utf-8", dtype=str)
    df = df.rename(columns=lambda col: col.strip().lstrip("﻿"))

    missing = [col for col in (category_column, municipality_column, "Total") if col not in df.columns]
    if missing:
        raise RuntimeError(f"Unexpected layout of {url}: missing column(s) {missing}")

    df = df[df[municipality_column].notna()].copy()
    df["Municipality code"] = df[municipality_column].str.extract(r"^(\d{5})\s")[0]
    df = df[df["Municipality code"].notna()]
    # The 3-digit "999" municipality of each province is INE's aggregate of the
    # municipalities it does not publish individually, not a municipality.
    df = df[df["Municipality code"].str[2:] != "999"]

    df = df[df[category_column].isin(categories)]
    df["Value"] = _parse_ine_number(df["Total"])
    df = df.pivot_table(index="Municipality code", columns=category_column, values="Value")
    df = df.rename(columns=categories)

    return df.reset_index()


def _dwelling_use_2001():
    """Dwellings by type in the 2001 census, for every municipality."""
    r = request_with_retries(_DWELLING_USE_2001_URL, headers={'User-Agent': 'Mozilla/5.0'})
    raw = pd.read_excel(io.BytesIO(r.content), header=None)

    # The header is spread over three merged rows; row 6 carries the leaf labels, which
    # are checked so that a reshuffling of the file fails here instead of silently
    # returning the wrong class.
    header = raw.iloc[6].astype(str).str.strip()
    expected = {3: "TOTAL", 4: "TOTAL", 7: "TOTAL", 8: "Secundarias", 9: "Vacías", 10: "Otro tipo"}
    mismatched = {col: header.get(col) for col, label in expected.items() if header.get(col) != label}
    if mismatched:
        raise RuntimeError(f"Unexpected layout of {_DWELLING_USE_2001_URL}: header reads {mismatched}")

    # Municipality rows are labelled "08001-Abrera" in the second column; the province
    # and national totals carry "TOTAL" there instead.
    labels = raw[1].astype(str)
    df = raw[labels.str.match(r"^\d{5}-")].copy()
    df["Municipality code"] = labels[df.index].str[:5]

    df = df.rename(columns=_C2001_DWELLING_COLUMNS)
    df = df[["Municipality code"] + list(_C2001_DWELLING_COLUMNS.values())]
    for col in _C2001_DWELLING_COLUMNS.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Year"] = 2001
    return df


def _dwelling_use_2011():
    """Dwellings by type in the 2011 census.

    The breakdown into secondary and empty dwellings exists only for municipalities over
    2,000 inhabitants; the smaller ones get their totals from the complete municipality
    list, so their non-main count is still known — just not what it is made of.
    """
    detail = _dwelling_use_municipal_table(
        _DWELLING_USE_2011_TYPE_URL, "Tipo de vivienda", _C2011_DWELLING_TYPES,
        "Municipios (con más de 2.000 habitantes)")
    totals = _dwelling_use_municipal_table(
        _DWELLING_USE_2011_TOTAL_URL, "Tipo de vivienda", _C2011_DWELLING_TOTALS, "Municipios")

    df = totals.merge(detail, on="Municipality code", how="outer", suffixes=("", " (detail)"))
    for col in _C2011_DWELLING_TOTALS.values():
        df[col] = df[col].fillna(df[f"{col} (detail)"])
        df = df.drop(columns=[f"{col} (detail)"])

    # INE publishes no "no principales" total for the municipalities left out of the
    # detailed table, but it is the remainder of the two counts that are published.
    df["Dwellings ~ Dwelling type:Non-main"] = df["Dwellings ~ Dwelling type:Non-main"].fillna(
        df["Dwellings"] - df["Dwellings ~ Dwelling type:Main"])

    df["Year"] = 2011
    return df


def _dwelling_use_2021():
    """Dwellings by type and by electricity use in the 2021 census."""
    types = _dwelling_use_municipal_table(
        _DWELLING_USE_2021_TYPE_URL, "Tipo de vivienda (principal o no)", _C2021_DWELLING_TYPES, "Municipios")
    uses = _dwelling_use_municipal_table(
        _DWELLING_USE_2021_USE_URL, "Consumo eléctrico", _C2021_DWELLING_USES, "Municipios")

    # Both tables count the same conventional family dwellings, so the total of the
    # electricity table is redundant and is dropped in favour of the type one.
    uses = uses.drop(columns=["Dwellings"], errors="ignore")

    df = types.merge(uses, on="Municipality code", how="outer")

    # The four electricity classes partition the total, so the regular-use one is what
    # the other three leave; it is only defined where the classification is published.
    classified = df[["Dwellings ~ Electricity use:Empty",
                     "Dwellings ~ Electricity use:Very low consumption",
                     "Dwellings ~ Electricity use:Sporadic use"]]
    df["Dwellings ~ Electricity use:Regular use"] = df["Dwellings"] - classified.sum(axis=1, min_count=3)

    df["Year"] = 2021
    return df


def _dwelling_use_regional_codes(df, community_labels, province_labels):
    """Attach the standard codes to the community and province names of an INE table.

    The 2021 tables prefix the code to the name ("01 Andalucía"), the 2011 ones do not
    ("ANDALUCÍA", "Barcelona"), so the names are matched against the official relation
    instead. A name INE spells differently would silently drop the row, so anything left
    unmatched raises.
    """
    rel = RelationAutonomousCommunityAndProvince()
    community_codes = dict(zip(rel["Autonomous community name"].str.upper(), rel["Autonomous community code"]))
    province_codes = dict(zip(rel["Province name"].str.upper(), rel["Province code"]))

    def _code(labels, codes):
        labels = labels.str.strip()
        prefixed = labels.str.extract(r"^(\d{2})\s")[0]
        return prefixed.fillna(labels.str.upper().map(codes))

    df = df.copy()
    df["Autonomous community code"] = _code(community_labels, community_codes)
    df["Province code"] = _code(province_labels, province_codes) if province_labels is not None else np.nan

    unmatched = pd.concat([
        community_labels[df["Autonomous community code"].isna()],
        province_labels[df["Province code"].isna()] if province_labels is not None else pd.Series(dtype=str),
    ]).dropna().unique()
    if len(unmatched):
        raise RuntimeError(f"Unknown INE community/province name(s): {list(unmatched)}")

    return df


def _dwelling_use_regional_table(url, category_column, categories, community_column, province_column,
                                 keep=None, finer_column=None):
    """Read the community and province rows of one of the INE dwelling tables.

    These tables stack the levels in one file, each level blanking the columns finer than
    itself: the national row leaves both the community and the province blank, a
    community row leaves the province blank, and a province row fills both. A table that
    goes further down still repeats the community and province of every municipality, so
    ``finer_column`` names the finer level and its rows are dropped — without that, a
    province would be read as the average of its municipalities.
    """
    r = request_with_retries(url, headers={'User-Agent': 'Mozilla/5.0'}, expect_csv=True)
    r.encoding = 'utf-8'
    df = pd.read_csv(StringIO(r.text), sep=";", encoding="utf-8", dtype=str)
    df = df.rename(columns=lambda col: col.strip().lstrip("﻿"))

    missing = [col for col in (category_column, community_column, province_column, "Total")
               if col not in df.columns]
    if missing:
        raise RuntimeError(f"Unexpected layout of {url}: missing column(s) {missing}")

    if keep is not None:
        for column, value in keep.items():
            df = df[df[column] == value]
    if finer_column is not None:
        if finer_column not in df.columns:
            raise RuntimeError(f"Unexpected layout of {url}: missing column {finer_column}")
        df = df[df[finer_column].isna()]

    df = df[df[community_column].notna() & df[category_column].isin(categories)].copy()
    df = _dwelling_use_regional_codes(df, df[community_column], df[province_column])
    df["Value"] = _parse_ine_number(df["Total"])

    frames = {}
    for level, group in (("Province", df[df[province_column].notna()]),
                         ("Autonomous community", df[df[province_column].isna()])):
        index = ["Autonomous community code", "Province code"] if level == "Province" \
            else ["Autonomous community code"]
        table = group.pivot_table(index=index, columns=category_column, values="Value")
        frames[level] = table.rename(columns=categories).reset_index()

    # INE writes no province row for the communities made of a single province, since it
    # would repeat the community one; they are filled in so the province table covers all
    # 52 of them.
    rel = RelationAutonomousCommunityAndProvince()
    single = rel.groupby("Autonomous community code").filter(lambda g: len(g) == 1)
    missing = single[~single["Province code"].isin(frames["Province"]["Province code"])]
    if len(missing):
        filled = frames["Autonomous community"].merge(
            missing[["Autonomous community code", "Province code"]], on="Autonomous community code")
        frames["Province"] = pd.concat([frames["Province"], filled], ignore_index=True)

    return frames


def _dwelling_use_2011_regional():
    """Dwellings by type in the 2011 census, per autonomous community and province."""
    return _dwelling_use_regional_table(
        _DWELLING_USE_2011_REGIONAL_URL, "Tipo de vivienda", _C2011_DWELLING_TYPES,
        "Comunidades y Ciudades Autónomas", "Provincias",
        keep={"Tamaño de municipio": "Total"})


def _dwelling_use_2021_regional():
    """Dwellings by electricity use in the 2021 census, per autonomous community and province."""
    frames = _dwelling_use_regional_table(
        _DWELLING_USE_2021_USE_URL, "Consumo eléctrico", _C2021_DWELLING_USES,
        "Comunidades y Ciudades Autónomas", "Provincias", finer_column="Municipios")

    for level, df in frames.items():
        classified = df[["Dwellings ~ Electricity use:Empty",
                         "Dwellings ~ Electricity use:Very low consumption",
                         "Dwellings ~ Electricity use:Sporadic use"]]
        df["Dwellings ~ Electricity use:Regular use"] = df["Dwellings"] - classified.sum(axis=1, min_count=3)

    return frames


def _dwelling_use_aggregate(df, group_columns):
    """Add the municipal counts up to a coarser level.

    Only usable where INE publishes every municipality of the level, which is the case
    for the 2001 counts and for the 2021 main/non-main ones; the 2011 breakdown and the
    2021 electricity classification are read from INE's own regional tables instead.
    """
    counts = [col for col in _DWELLING_USE_COUNTS if col in df.columns]
    return df.groupby(group_columns, dropna=False)[counts].sum(min_count=1).reset_index()


def _dwelling_use_comparable(df):
    """Add the ``Dwellings ~ Comparable use:*`` columns aligning the two classifications.

    Each row is filled from the classification its census published (see
    ``_DWELLING_USE_COMPARABLE``): the field-census one for 2001 and 2011, the
    electricity one for 2021. A row that has neither — a municipality left out of the
    2011 breakdown or of the 2021 electricity table — stays ``NaN`` rather than being
    filled from the main/non-main counts, which do not split the same way.
    """
    def _class(required, optional):
        if not all(col in df.columns for col in required):
            return pd.Series(np.nan, index=df.index)
        value = pd.concat([df[col] for col in required], axis=1).sum(axis=1, min_count=len(required))
        for col in optional:
            if col in df.columns:
                value = value + df[col].fillna(0)
        return value

    # A row takes all three classes from one classification or from none of them: mixing
    # them would break the partition of the total, and a share of a partly-filled row
    # would silently mean something different from the same share elsewhere.
    blocks = {}
    for source in ("electricity", "field"):
        block = {name: _class(*spec[source]) for name, spec in _DWELLING_USE_COMPARABLE.items()}
        complete = pd.concat(block.values(), axis=1).notna().all(axis=1)
        blocks[source] = {name: value.where(complete) for name, value in block.items()}

    for name in _DWELLING_USE_COMPARABLE:
        df[name] = blocks["electricity"][name].fillna(blocks["field"][name])
    return df


def _dwelling_use_shares(df):
    """Add the ``Percentage of dwellings ~ ...`` share of every count column."""
    for col in _DWELLING_USE_COUNTS + _DWELLING_USE_COMPARABLE_COUNTS:
        if col == "Dwellings":
            continue
        df[col.replace("Dwellings ~", "Percentage of dwellings ~", 1)] = df[col] / df["Dwellings"] * 100
    return df


def _dwelling_use_present(df, location_columns):
    """Derive the harmonised columns and the shares, and put the columns in a fixed order.

    Only the counts each census publishes are cached; everything derived from them is
    rebuilt here, so a cache written before these columns existed still reads correctly.
    """
    # The caller passes a filtered slice, which the derived columns must not write through.
    df = df.copy()
    for col in _DWELLING_USE_COUNTS + ["Median annual electricity consumption (kWh)"]:
        if col not in df.columns:
            df[col] = np.nan

    df = _dwelling_use_comparable(df)
    df = _dwelling_use_shares(df)

    share = lambda col: col.replace("Dwellings ~", "Percentage of dwellings ~", 1)
    counts = _DWELLING_USE_COUNTS + _DWELLING_USE_COMPARABLE_COUNTS
    order = (location_columns + counts +
             [share(col) for col in counts if col != "Dwellings"] +
             ["Median annual electricity consumption (kWh)"])
    return df[order + [col for col in df.columns if col not in order]]


def _dwelling_use_regional_level(municipal, level):
    """Build the province or autonomous community table from the sources each year allows."""
    group_columns = ["Autonomous community code", "Province code"] if level == "Province" \
        else ["Autonomous community code"]

    aggregated = _dwelling_use_aggregate(municipal, group_columns + ["Year"])

    # 2001 is a full field census, so its municipal counts add up to the published
    # regional ones exactly, including the secondary/empty split.
    frames = [aggregated[aggregated["Year"] == 2001]]

    # 2011 publishes the split only for municipalities over 2,000 inhabitants, so the
    # regional figures come from INE's own table rather than from the municipal ones.
    regional_2011 = _dwelling_use_2011_regional()[level]
    regional_2011["Year"] = 2011
    frames.append(regional_2011)

    # 2021 publishes main/non-main for every municipality, so those add up; the
    # electricity classification does not, and is read from INE's regional rows.
    types_2021 = aggregated[aggregated["Year"] == 2021].drop(
        columns=[col for col in _DWELLING_USE_COUNTS if "Electricity use" in col], errors="ignore")
    uses_2021 = _dwelling_use_2021_regional()[level].drop(columns=["Dwellings"], errors="ignore")
    frames.append(types_2021.merge(uses_2021, on=group_columns, how="outer"))

    df = pd.concat(frames, ignore_index=True)
    for col in _DWELLING_USE_COUNTS + ["Median annual electricity consumption (kWh)"]:
        if col not in df.columns:
            df[col] = np.nan

    location = group_columns + ["Year"]
    return df[location + [col for col in _DWELLING_USE_COUNTS +
                          ["Median annual electricity consumption (kWh)"]]].sort_values(location)


def EmptyAndSecondaryDwellingsCensus(wd, municipality_code=None, years=None):
    """Empty, secondary and non-main dwellings in the 2001, 2011 and 2021 censuses.

    Returns a dict with the ``"Municipality"``, ``"Province"`` and
    ``"Autonomous community"`` DataFrames, each holding one row per area and census year,
    with the counts of dwellings of each class and the share of the area's dwellings each
    one represents.

    Two classifications are returned side by side, because the 2021 census dropped the
    one the two earlier censuses used:

    ``Dwellings ~ Dwelling type:*``
        The field-census classification. ``Main`` and ``Non-main`` are published in all
        three censuses; ``Secondary`` and ``Empty`` split the non-main ones in 2001 and
        2011 only, and 2001 adds an ``Other non-main`` residual. 2021 has no way of
        telling a second home from an empty dwelling, so both are ``NaN``.

    ``Dwellings ~ Electricity use:*``
        The 2021 classification by yearly electricity consumption, which INE publishes
        in its place: ``Empty`` (no supply contract, or less than the equivalent of 15
        days a year for that municipality), ``Very low consumption`` (up to 250 kWh),
        ``Sporadic use`` (251-750 kWh, one to three months a year — the closest proxy
        for the old ``Secondary``) and ``Regular use``. The four partition the total.
        ``NaN`` for 2001 and 2011.

    ``Dwellings ~ Comparable use:*``
        The two above aligned into one series that can be read across the three
        censuses, filled from whichever classification each census published:

        =============  ==================================  ==========================
        Comparable use 2001 / 2011                          2021
        =============  ==================================  ==========================
        ``Main``       ``Dwelling type:Main``               ``Electricity use:Regular use``
        ``Secondary``  ``Dwelling type:Secondary``          ``Electricity use:Very low
                       (+ ``Other non-main``, in 2001)       consumption`` + ``Sporadic use``
        ``Empty``      ``Dwelling type:Empty``              ``Electricity use:Empty``
        =============  ==================================  ==========================

        The three partition the total in every census, so their shares add to 100.
        2021's ``Very low consumption`` (up to 250 kWh, about a month of use) counts as
        secondary rather than empty: a dwelling used a month a year is what the earlier
        censuses recorded as a second home. 2001's ``Other non-main`` residual counts as
        secondary too, which is what INE does in its own 2001-2011 comparison.

        This is a bridge, not an identity — the 2021 figures come from electricity
        meters and the earlier ones from a census agent's judgement at the door, so a
        change along any of these lines between 2011 and 2021 mixes a real change in use
        with the change of instrument. It is most visible in tourist municipalities,
        where a second home occupied for a full summer consumes well over 750 kWh and
        lands in ``Main``. Use ``Dwelling type:*`` and ``Electricity use:*`` when the
        published figures are what matters.

    Every count is echoed as ``Percentage of dwellings ~ ...``, its share of the area's
    ``Dwellings``, in percent (0-100). ``Median annual electricity consumption (kWh)`` is
    published for 2021 only.

    Coverage is what each census supports, and is not the same everywhere: 2001 covers
    every municipality in full; 2011 gives the secondary/empty split only for
    municipalities over 2,000 inhabitants (the rest were surveyed by sample and only
    get ``Dwellings``, ``Main`` and ``Non-main``); 2021 gives the electricity
    classification only for the 3,139 municipalities INE publishes it for, those over
    1,000 inhabitants. Missing figures are ``NaN`` rather than zero.

    The province and autonomous community tables are complete regardless, because the
    partially-published columns are read from INE's own regional tables rather than
    added up from the municipalities. **Summing the municipal table therefore does not
    reproduce them** for the 2011 split (only ~2,308 municipalities carry it) or the
    2021 electricity classification (85.9% of the empty dwellings nationally, and as
    little as 48% in Castilla y León); use the coarser tables for regional figures.

    ``Dwellings`` counts family dwellings, which in 2021 means conventional family
    dwellings — the 2021 census no longer counts the few thousand ``alojamientos``
    (makeshift dwellings) that 2001 and 2011 included among the main ones.

    Parameters
    ----------
    wd : str
        Working directory the downloaded data is cached under.
    municipality_code : str or list of str, optional
        Restrict the result to these municipality code(s). Only filters the
        ``"Municipality"`` table; the coarser ones are returned whole.
    years : list, optional
        Restrict the result to these census years (2001, 2011 and/or 2021).
    """
    path = "INE/EmptyAndSecondaryDwellingsCensus"
    path = path_creator(path, wd)

    filename = f"{path}/df.parquet"
    province_filename = f"{path}/provinces.parquet"
    community_filename = f"{path}/autonomous_communities.parquet"

    if not os.path.exists(filename):

        print("Downloading the INE 2001, 2011 and 2021 census dwelling counts", file=sys.stdout)
        df = pd.concat([_dwelling_use_2001(), _dwelling_use_2011(), _dwelling_use_2021()],
                       ignore_index=True)

        df["Province code"] = df["Municipality code"].str[:2]

        for col in _DWELLING_USE_COUNTS + ["Median annual electricity consumption (kWh)"]:
            if col not in df.columns:
                df[col] = np.nan

        # Only the published counts are cached; the harmonised classification and the
        # shares are derived on read, so they follow the code rather than the cache.
        df = df[["Province code", "Municipality code", "Year"] + _DWELLING_USE_COUNTS +
                ["Median annual electricity consumption (kWh)"]]
        df = df.sort_values(["Year", "Municipality code"])

        df.to_parquet(filename, index=False)

    else:
        df = pd.read_parquet(filename)

    df["Country code"] = "ES"
    _rel = RelationAutonomousCommunityAndProvince()
    _cpro2caut = dict(zip(_rel["Province code"], _rel["Autonomous community code"]))
    _cpro2cauname = dict(zip(_rel["Province code"], _rel["Autonomous community name"]))
    _caut2cauname = dict(zip(_rel["Autonomous community code"], _rel["Autonomous community name"]))
    df["Autonomous community code"] = df["Province code"].map(_cpro2caut)
    df["Autonomous community name"] = df["Province code"].map(_cpro2cauname)

    if not os.path.exists(province_filename) or not os.path.exists(community_filename):
        print("Downloading the INE regional census dwelling counts", file=sys.stdout)
        _dwelling_use_regional_level(df, "Province").to_parquet(province_filename, index=False)
        _dwelling_use_regional_level(df, "Autonomous community").to_parquet(community_filename, index=False)

    provinces = pd.read_parquet(province_filename)
    communities = pd.read_parquet(community_filename)
    for table in (provinces, communities):
        table["Country code"] = "ES"
        table["Autonomous community name"] = table["Autonomous community code"].map(_caut2cauname)
    provinces["Province name"] = provinces["Province code"].map(
        dict(zip(_rel["Province code"], _rel["Province name"])))

    if years != None:
        df = df[df['Year'].isin(years)]
        provinces = provinces[provinces['Year'].isin(years)]
        communities = communities[communities['Year'].isin(years)]
    if municipality_code is not None:
        if type(municipality_code) == str:
            df = df[(df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            df = df[df["Municipality code"].isin(municipality_code)]

    df = _dwelling_use_present(df, _DWELLING_USE_LOCATION_COLUMNS)
    provinces = _dwelling_use_present(provinces, ["Country code", "Autonomous community code",
                                                  "Autonomous community name", "Province code",
                                                  "Province name", "Year"])
    communities = _dwelling_use_present(communities, ["Country code", "Autonomous community code",
                                                      "Autonomous community name", "Year"])

    return ({
        "Autonomous community": communities.reset_index(drop=True),
        "Province": provinces.reset_index(drop=True),
        "Municipality": df.reset_index(drop=True)
    })


def HouseholdsPriceIndex(wd, municipality_code=None, years=None):

    path = "INE/HouseholdsPriceIndex"
    path = path_creator(path, wd)

    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):

        r = request_with_retries("https://www.ine.es/jaxiT3/files/t/en/csv_bd/25171.csv?nocab=1", expect_csv=True)
        r.encoding = 'utf-8'
        df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", dtype={3: 'str', 6: 'str'})
        df_ = df_[df_["Indices and rates"]=="Index"]
        df_["Country code"] = "ES"
        df_["Autonomous Communities and Cities"] = df_["Autonomous Communities and Cities"].str[:2]
        df_["Year"] = df_["Periodo"].str[:4].astype(int)
        df_["Quarter"] = df_["Periodo"].str[4:].map({"QI": 1, "QII": 2, "QIII": 3, "QIV": 4})
        df_["Index type"] = df_["Index type"].replace({
            "General": "Whole housing market",
            "New dwelling": "First-hand housing market",
            "Second-hand dwelling": "Second-hand housing market"
        })
        df_ = df_.rename(columns = {
            "Autonomous Communities and Cities": 'Autonomous community code',
            "Index type": "Housing market"
        })
        df_["value"] = pd.to_numeric(df_["Total"].astype(str).str.replace('.', '').str.replace(',', '.'), errors="coerce")
        df_ = df_.drop(columns=["Indices and rates", "National Total", "Periodo", "Total"])
        df_ = pd.pivot(df_,index=['Year', 'Quarter', 'Autonomous community code'],
                                   columns=['Housing market'],
                                   values="value")

        subgroups = ["Housing market"]
        if isinstance(df_.columns, pd.MultiIndex):
            allcols = df_.columns.names
            maincol = [col for col in allcols if col not in subgroups]
            maincol.extend([col for col in allcols if col in subgroups])
            df_.columns = df_.columns.reorder_levels(order=maincol)
            df_.columns = [" ~ ".join([f"{level}:{value}" if level in subgroups else f"{value}"
                                       for level, value in zip(df_.columns.names, cols)])
                           if cols[1] != '' else cols[0] for cols in df_.columns.to_flat_index()]
        df_.columns = [cols.strip() for cols in df_.columns]

        for subgroup in subgroups:
            df_.columns = [re.sub(f" ~ {subgroup}:Total", "", cols) for cols in df_.columns]

        df_ = df_.reset_index()

        df_prov = RelationAutonomousCommunityAndProvince()
        df_prov = df_prov.merge(df_, on=["Autonomous community code"], how='outer')

        df_prov.to_csv(filename,sep="\t", index=False)

    else:
        df_prov = pd.read_csv(filename, sep="\t",dtype={0:'str',1:'str',2:'str',3:'str'})
    if years != None:
        df_prov = df_prov[df_prov['Year'].isin(years)]
    if municipality_code is not None:
        if type(municipality_code) == str:
            df_prov = df_prov[(df_prov["Province code"] == municipality_code.str[0:2]).values]
        elif type(municipality_code) == list:
            municipality_code = pd.Series(municipality_code)
            df_prov = df_prov[df_prov["Province code"].isin(municipality_code.str[0:2])]


    return ({
            "Province": df_prov
        })

def path_creator(path, wd):
    path_to_create = []
    for i in path.split("/"):
        path_to_create.append(i)
        os.makedirs(f"{wd}/" + "/".join(path_to_create), exist_ok=True)
    return f"{wd}/{path}"


def estimate_income_distribution(row):
    # Definir puntos conocidos de la CDF: (percentil acumulado, múltiplo de la mediana)
    cdf_percentiles = np.array([
        row['Percentage of the population with income per consumption unit of under 40% of the median '],
        row['Percentage of the population with income per consumption unit of under 50% of the median '],
        row['Percentage of the population with income per consumption unit of under 60% of the median '],
        100 - row['Population with per consumption unit income above 140% of the median'],
        100 - row['Population with per consumption unit income above 160% of the median'],
        100 - row['Population with per consumption unit income above 200% of the median']
    ]) / 100  # pasar a proporciones

    cdf_income_multipliers = np.array([0.4, 0.5, 0.6, 1.4, 1.6, 2.0])

    # Crear función de interpolación
    income_cdf_fn = interp1d(
        cdf_income_multipliers,
        cdf_percentiles,
        kind='linear',
        bounds_error=False,
        fill_value=(cdf_percentiles[0], cdf_percentiles[-1])
    )

    # Definir cortes de ingresos por hogar en múltiplos de la mediana
    income_brackets_multipliers = [500, 1000, 1500, 2000, 2500, 3000, 5000]
    mediana_uc = row['Median income by unit of consumption']
    uc_hogar = row['Unidades de consumo medio en el hogar']
    ingreso_mediana_hogar = mediana_uc * uc_hogar / 12

    # Convertimos a múltiplos de la mediana
    income_brackets_multipliers = [v / ingreso_mediana_hogar for v in income_brackets_multipliers]

    # Calcular CDF en los puntos de corte
    cdf_values = income_cdf_fn(income_brackets_multipliers)

    return pd.Series({
        'Salario mensual neto del hogar de menos de 500 euros': round(cdf_values[0] * 100, 1),
        'Salario mensual neto del hogar de 500 euros a menos de 1.000 euros': round((cdf_values[1] - cdf_values[0]) * 100, 1),
        'Salario mensual neto del hogar de menos de 1.000 euros': round(cdf_values[1] * 100, 1),
        'Salario mensual neto del hogar de 1.000 euros a menos de 1.500 euros': round((cdf_values[2] - cdf_values[1]) * 100, 1),
        'Salario mensual neto del hogar de 1.500 euros a menos de 2.000 euros': round((cdf_values[3] - cdf_values[2]) * 100, 1),
        'Salario mensual neto del hogar de 2.000 euros a menos de 2.500 euros': round((cdf_values[4] - cdf_values[3]) * 100, 1),
        'Salario mensual neto del hogar de 2.500 euros a menos de 3.000 euros': round((cdf_values[5] - cdf_values[4]) * 100, 1),
        'Salario mensual neto del hogar de 2.000 euros a menos de 3.000 euros': round((cdf_values[5] - cdf_values[3]) * 100, 1),
        'Salario mensual neto del hogar de 3.000 euros a menos de 5.000 euros': round((cdf_values[6] - cdf_values[5]) * 100, 1),
        'Salario mensual neto del hogar de 3.000 euros o más': round((1-cdf_values[5]) * 100, 1),
        'Salario mensual neto del hogar de 5.000 euros o más': round((1-cdf_values[6]) * 100, 1),
    })


def estimate_nationality_households(row):
    pct_espanoles = row['Population ~ Nationality:España'] / row['Population_y']

    # Ajustamos pesos usando una distribución plausible (puedes afinar estos coeficientes)
    pct_hogar_esp = min(1.0, pct_espanoles ** 2 + 0.1)  # hogares exclusivamente españoles
    pct_hogar_ext = min(1.0, (1 - pct_espanoles) ** 2 + 0.1)  # hogares exclusivamente extranjeros
    pct_hogar_mixto = 1.0 - pct_hogar_esp - pct_hogar_ext  # hogares mixtos

    # Corrección si hay sobre/infraasignación
    if pct_hogar_mixto < 0:
        pct_hogar_mixto = 0
        total = pct_hogar_esp + pct_hogar_ext
        pct_hogar_esp /= total
        pct_hogar_ext /= total

    return pd.Series({
        'Hogar exclusivamente español': round(pct_hogar_esp * 100, 1),
        'Hogar mixto (con españoles y extranjeros)': round(pct_hogar_mixto * 100, 1),
        'Hogar exclusivamente extranjero': round(pct_hogar_ext * 100, 1),
    })


# =============================================================================
# Essential Characteristics column translation: Spanish -> English snake_case
# =============================================================================
#
# EssentialCharacteristicsOfPopulationAndHouseholds builds its variable keys and
# column names from the raw INE labels, structured as ``{group} - {variable} ~
# {subclass}`` (the dict keys drop the ``~ {subclass}`` part). The curated maps
# below translate each of the three parts to a short English snake_case token;
# group and variable are re-joined with underscores and the subclass is appended
# after a ``~``, e.g.
#   ``Viviendas principales - Tipo de calefacción ~ Sí, individual``
#     -> ``main_dwellings_heating_type~individual``.
# Fragments absent from the maps fall back to an accent-stripped, snake_cased
# form of the Spanish text (deterministic, never raises), so new INE categories
# still get a stable key.

_EC_GROUPS = {
    "Personas": "people",
    "Personas de 16 años o más": "people16plus",
    "Personas de 16 años o más que conviven con otras personas": "people16plus_cohabiting",
    "Personas de 16 años o más que conviven con otras personas y participan en cuidados a personas dependientes dentro del hogar": "people_16plus_in_house_daycare",
    "Personas de 16 años o más que participan en cuidados a personas dependientes fuera del hogar": "people_16plus_out_house_daycare",
    "Personas de 16 años o más que viven solas": "people16plus_living_alone_with_helpers",
    "Personas nacidas en España": "people_born_in_spain",
    "Personas nacidas fuera de España": "people_born_foreign",
    # "Hogares/personas..." groups are folded onto their "Hogares..." counterpart by
    # _normalise_household_group (both count households once "Unidad" is filtered), so
    # each pair of spellings deliberately shares one English token.
    "Hogares": "households",
    "Hogares/personas": "households",
    "Hogares de una sola persona (unipersonales)": "households_single_person",
    "Parejas convivientes": "cohabiting_couples",
    "Hogares en viviendas alquiladas": "households_rented",
    "Hogares/personas en viviendas alquiladas": "households_rented",
    "Hogares en viviendas propias": "households_owned",
    "Hogares/personas en viviendas propias": "households_owned",
    "Hogares con segunda residencia": "households_secondary",
    "Hogares/personas con segunda residencia": "households_secondary",
    "Hogares con vehículo": "households_vehicles",
    "Hogares/personas con vehículo": "households_vehicles",
    "Hogares con servicio doméstico remunerado": "households_with_paid_domestic_service",
    "Hogares/personas con servicio doméstico remunerado": "households_with_paid_domestic_service",
    "Hogares con ayuda externa": "households_with_unpaid_external_help",
    "Hogares/personas con ayuda externa": "households_with_unpaid_external_help",
    "Viviendas principales": "main_dwellings",
    "Viviendas principales con calefacción": "main_dwellings_heating",
}

_EC_VARIABLES = {
    "Lugar de trabajo/estudio": "work_or_study_place",
    "Número de desplazamaientos": "transport_daily_trips",
    "Medio de transporte": "transport_mode",
    "Tipo de vehículo": "transport_type",
    "Tiempo diario": "transport_daily_time",
    "Grado de satisfacción": "transport_satisfaction",
    "Grado de participación en las tareas domésticas": "housework_involvement",
    "Grado de participación en cuidados a menores o dependientes dentro del hogar": "in_house_daycare_involvement",
    "Grado de participación en cuidados a menores o dependientes fuera del hogar": "out_house_daycare_involvement",
    "Tipo de dependiente": "dependency_type",
    "Horas diarias dedicadas al cuidado": "daily_care_hours",
    "Tiene apoyo social": "has_social_support",
    "Tipo de relación": "relationship_type",
    "Lugar de residencia": "residence_place",
    "Lugar de nacimiento progenitores": "parents_birthplace",
    "Residencia progenitores": "parents_residence",
    "Nacionalidad progenitores": "parents_nationality",
    "Nivel estudios progenitores": "parents_education",
    "Accede habitualmente a internet": "internet_access",
    "Dispone de perfil en alguna red social": "has_social_networks",
    "Dispone de smartphone": "has_smartphone",
    "Realiza compras por internet": "online_shopping",
    "Realiza ventas por internet": "online_selling",
    "Edad": "age",
    "Nacionalidad": "nationality",
    "Estado civil": "marital_status",
    "Nivel educativo": "education_level",
    "Situación laboral": "employment_status",
    "Nivel de ingresos mensuales netos del hogar": "net_incomes",
    "Sexo de la pareja": "genres",
    "Nacionalidad de la pareja": "couple_nationality",
    "Número de hijos": "n_children",
    "Número de habitaciones de la vivienda": "n_rooms",
    "Superficie útil de la vivienda": "floor_area",
    "Tipo de edificio": "building_type",
    "Régimen de tenencia de la vivienda": "tenure",
    "Cuota mensual del alquiler": "monthly_rent",
    "Cuota mensual de la hipoteca": "monthly_mortgage",
    "Disponen de segunda residencia": "second_home_ownership",
    "Lugar de la segunda residencia": "second_home_place",
    "Días de uso de la segunda residencia al año": "second_home_occupancy",
    "Número de vehículos": "vehicles_number",
    "Vehículo ecólogico": "vehicles_eco",
    "Separan algún tipo de residuo": "waste_separation",
    "Tipo de residuos separados": "waste_type",
    "Servicio doméstico remunerado": "paid_domestic_service",
    "Ayuda externa": "unpaid_external_help",
    "Adaptada a necesidades propias del envejecimiento": "adapted_to_elderly",
    "Problema de aislamiento": "insulation_issues",
    "Tipo de calefacción": "heating_type",
    "Tipo de combustible": "fuel",
    "Sistema de suministro de agua": "water_supply",
    "Tiene sistema de refrigeración": "has_cooling",
    "Tipo de conexión a internet": "internet_connection",
    "Tipo de electrodoméstico": "domestic_appliances_type",
    "Tipo de bombillas": "lighting_type",
    "Aseo con inodoro / Bañera o ducha": "toilet_bath",
    "Número de cuartos de baño o aseos": "n_bathrooms",
    "Cocina independiente de 4 m2 o más": "kitchen_sized_4m2plus",
    "Número de habitaciones": "n_rooms",
    "Tipo de problemática en la zona": "surroundings_issues",
    "Tipo de infraestructura o servicio": "infrastructure_service",
    "Estado de conservación": "conservation_status",
    "Accesibilidad": "accessibility_status",
    "Tipo de instalación": "installations",
    "Número de plazas de garaje": "n_garages_places",
    "Tipo de dispositivo de energía renovable": "renewable_device",
}

_EC_SUBCLASSES = {
    # generic yes/no and counts
    "Sí": "yes",
    "No": "no",
    "0": "0", "1": "1", "2": "2", "3": "3",
    "4 o más": "4plus", "3 o más": "3plus", "2 o más": "2plus",
    # work / study location
    "En el municipio en el que resido": "same_municipality",
    "En el propio domicilio": "at_home",
    "En otro municipio de la misma provincia": "other_municipalities_same_provinces",
    "En varios municipios (soy comercial, repartidor, taxista...)": "several_municipalities",
    "Otros lugares": "other_places",
    "Más de 2": "2plus",
    # transport
    "Andando": "on_foot",
    "De empresa u otro medio": "company_or_other",
    "Particular": "private",
    "Público": "public",
    "Autobús, tren, metro o tranvía": "bus_train_metro_tram",
    "Coche": "car",
    "Moto, bicicleta y otros tipos": "motorbike_bike_other",
    # daily commute time
    "90 minutos o más": "90min_plus",
    "Entre 20 y 39 minutos": "20_39min",
    "Entre 40 y 59 minutos": "40_59min",
    "Entre 60 y 89 minutos": "60_89min",
    "Menos de 20 minutos": "under_20min",
    # satisfaction
    "Insatisfecho": "dissatisfied",
    "Muy satisfecho": "very_satisfied",
    "Satisfecho": "satisfied",
    # housework / care participation
    "Me encargo de la mayor parte de las tareas domésticas de las tareas domésticas": "most",
    "Me encargo de una parte importante de las tareas, compartiéndolas con otra/s personas": "shared",
    "Me encargo de una pequeña parte de las tareas domésticas": "small_part",
    "No participo habitualmente en las tareas domésticas": "none",
    "Me encargo de la mayor parte de los cuidados": "most",
    "Me encargo de una parte importante de los cuidados, compartiéndolos con otra/s personas": "shared",
    "Me encargo de una pequeña parte de los cuidados": "small_part",
    "No hay personas menores ni personas dependientes en el hogar": "no_minors_or_dependents",
    "No participio habitualmente en los cuidados": "none",
    "No tengo ninguna persona dependiente a mi cargo": "no_dependents",
    # dependent type
    "Discapacitado/a": "disabled",
    "Enfermo/a crónico/a": "chronically_ill",
    "Mayor de 70 años u otro tipo": "over_70_or_other",
    "Menor de edad": "children",
    # daily care hours
    "6 horas o más": "6h_plus",
    "Entre 2 y 6 horas": "2_6h",
    "Menos de 2 horas": "under_2h",
    "3 horas o más": "3h_plus",
    "Entre 1 y 3 horas": "1_3h",
    "Menos de 1 hora": "under_1h",
    # relationship type (living alone)
    "Amigos/as o vecinos/as y otros parientes (que no son hijos/as)": "friends_neighbors_relatives",
    "Hijos/as y amigos/as o vecinos/as": "children_friends_neighbors",
    "Hijos/as y otras personas (parientes o no)": "children_others",
    "Otros parientes (que no son hijos/as)": "other_relatives",
    "Sólo amigos/as o vecinos/as": "only_friends_neighbors",
    "Sólo hijos/as": "only_children",
    # residence location
    "En el mismo municipio": "same_muni",
    "Fuera de la provincia": "outside_prov",
    # parents birthplace / residence
    "España pero distinta comunidad autónoma": "es_other_region",
    "Misma comunidad autónoma pero distinta provincia": "same_region_other_prov",
    "Misma provincia pero distinto municipio": "same_prov_other_muni",
    "Mismo municipio": "same_muni",
    "Ningún progenitor ha nacido en España": "no_parent_born_es",
    "Distinto país": "other_country",
    "Mismo país": "same_country",
    "Mismo hogar": "same_hh",
    "Mismo municipio pero distinto hogar": "same_muni_other_hh",
    "Ningún progenitor reside en España": "no_parent_resides_es",
    "Diferente nacionalidad": "different_nationality",
    "Misma nacionalidad": "same_nationality",
    # parents education level
    "Mayor nivel de estudios que sus progenitores": "higher_than_parents",
    "Menor nivel de estudios que sus progenitores": "lower_than_parents",
    "Mismo nivel de estudios que sus progenitores": "same_as_parents",
    # age (single-person households)
    "De 30 a 39 años": "30_39",
    "De 40 a 49 años": "40_49",
    "De 50 a 59 años": "50_59",
    "De 60 a 69 años": "60_69",
    "De 70 a 79 años": "70_79",
    "De 80 y más años": "80plus",
    "Menos de 30 años": "under_30",
    # nationality / marital status
    "Española": "spanish",
    "Extranjera": "foreign",
    "Casado/a": "married",
    "Separado/a o divorciado/a": "separated_divorced",
    "Soltero/a": "single",
    "Viudo/a": "widowed",
    # education level
    "Educación primaria e inferior": "primary_or_below",
    "Educación superior": "tertiary",
    "Primera etapa de educación secundaria y similar": "lower_secondary",
    "Segunda etapa de educación secundaria y educación postsecundaria no superior": "upper_secondary",
    # employment status
    "Jubilado/a, prejubilado/a o incapacitado/a permamentemente para trabajar": "retired_or_disabled",
    "No trabaja": "not_working",
    "Ocupado/a": "employed",
    # income levels (single-person households)
    "3.000 euros o más": "ge_3000eur",
    "De 1.000 euros a menos de 1.500 euros": "1000_1500eur",
    "De 1.500 euros a menos de 2.000 euros": "1500_2000eur",
    "De 2.000 euros a menos de 3.000 euros": "2000_3000eur",
    "Menos de 1.000 euros": "under_1000eur",
    # couple sex / nationality
    "Pareja de distinto sexo": "different_sex",
    "Pareja del mismo sexo": "same_sex",
    "Ambos españoles": "both_spanish",
    "Ambos extranjeros": "both_foreign",
    "Español/a y extranjero/a": "spanish_and_foreign",
    # number of children
    "0 hijos conviviendo": "0_cohabiting",
    "0 hijos conviviendo menores de 25 años": "0_cohabiting_under25",
    "Algún hijo conviviendo": "some_cohabiting",
    "Algún hijo conviviendo menor de 25 años": "some_cohabiting_under25",
    "Ningún hijo conviviendo menor de 25 años": "none_cohabiting_under25",
    # useful floor area
    "Hasta 45 m2": "le_45m2",
    "Entre 46 y 60 m2": "46_60m2",
    "Menos de 60 m2": "under_60m2",
    "Entre 61 y 75 m2": "61_75m2",
    "Entre 76 y 90 m2": "76_90m2",
    "Entre 91 y 105 m2": "91_105m2",
    "Entre 106 y 120 m2": "106_120m2",
    "Entre 121 y 150 m2": "121_150m2",
    "Más de 150 m2": "over_150m2",
    # building type
    "Edificio de 2 o más viviendas": "multi_family",
    "Vivienda unifamiliar (chalet, adosado, pareado...)": "single_family",
    # tenure regime
    "Alquilada": "rented",
    "Cedida gratis o a bajo precio (por otro hogar, pagada por la empresa...) u otra forma": "ceded_or_other",
    "Propia por herencia o donación": "owned_inherited",
    "Propia, por compra, con pagos pendientes (hipotecas)": "owned_with_mortgage",
    "Propia, por compra, totalmente pagada": "owned_fully_paid",
    # rent / mortgage brackets
    "Menos de 200 euros": "under_200eur",
    "De 200 euros a menos de 500 euros": "200_500eur",
    "De 500 euros a menos de 700 euros": "500_700eur",
    "De 700 euros a menos de 1.000 euros": "700_1000eur",
    "De 1.000 euros o más": "ge_1000eur",
    # second home
    "En el mismo municipio que la primera residencia": "same_muni_as_primary",
    "En otra CCAA": "other_region",
    "En otra provincia, pero en la misma CCAA": "other_prov_same_region",
    "60 o más días": "60plus_days",
    "Entre 15 y 29 días": "15_29days",
    "Entre 30 y 59 días": "30_59days",
    "Menos de 15 días": "under_15days",
    # eco vehicle
    "No tiene vehículo ecológico (híbrido o eléctrico)": "no",
    "Tiene algún vehículo ecológico (híbrido o eléctrico)": "yes",
    # separated waste type
    "Envases": "packaging",
    "Orgánico": "organic",
    "Papel": "paper",
    "Vidrio": "glass",
    # paid domestic service / external help
    "No dispone de servicio doméstico": "no",
    "Sí, dispone de servicio doméstico": "yes",
    "No dispone de ayudas externas no remuneradas": "none",
    "Sí, dispone de ayudas de familiares, parientes, amigos, vecinos": "family_or_friends",
    "Sí, dispone de ayudas de otros, como servicios sociales o una ONG": "social_services_or_ngo",
    # heating type
    "No tiene calefacción": "none",
    "No tiene instalación de calefacción pero sí algún aparato que permite calentar alguna habitación (por ejemplo radiadores eléctricos)": "no_install_but_appliance",
    "Sí, colectiva": "collective",
    "Sí, individual": "individual",
    # fuel type
    "Electricidad": "electricity",
    "Gas natural": "natural_gas",
    "Otros": "other",
    "Petróleo o derivados (gasoil, fueloil, gasolina...)": "oil_derivatives",
    # water supply
    "Agua corriente por abastecimiento privado o particular del edificio": "private_supply",
    "Agua corriente por abastecimiento público": "public_supply",
    # internet connection
    "Conexión fija": "fixed",
    "Conexión fija y móvil": "fixed_and_mobile",
    "Conexión móvil": "mobile",
    "Sin conexión": "none",
    # appliances
    "Horno": "oven",
    "Lavadora": "washing_machine",
    "Lavavajillas": "dishwasher",
    "Microondas": "microwave",
    "Secadora": "dryer",
    "Vitocerámica/Inducción": "ceramic_induction_hob",
    # bulbs
    "Bajo consumo": "low_consumption",
    "Halógena": "halogen",
    "Led": "led",
    # toilet / bath
    "Aseo con inodoro": "toilet",
    "Bañera o ducha": "bath_or_shower",
    # area problems
    "Contaminación o malos olores": "pollution_odors",
    "Delincuencia": "crime",
    "Malas comunicaciones": "poor_transport",
    "Molestias relacionadas con actividades turísticas o locales de hostelería": "tourism_nuisance",
    "Poca limpieza en las calles": "dirty_streets",
    "Pocas zonas verdes": "few_green_areas",
    "Ruidos exteriores": "outdoor_noise",
    # nearby infrastructure / services
    "Colegio": "school",
    "Farmacia": "pharmacy",
    "Hospital, centros de salud o ambulatorio": "hospital_health_center",
    "Servicios de restauración (bares, restaurantes...)": "food_services",
    "Supermercado": "supermarket",
    # conservation status
    "Excelente": "excellent",
    "Muy bueno": "very_good",
    "Bueno": "good",
    "Normal": "normal",
    "Regular": "fair",
    "Malo": "bad",
    # accessibility
    "Es accesible": "accessible",
    "No es accesible": "not_accessible",
    # installation type
    "Agua caliente central": "central_hot_water",
    "Ascensor": "elevator",
    "Dispositivo de energía renovable": "renewable_device",
    "Garaje": "garage",
    "Gas por tubería": "piped_gas",
    # garage spaces
    "De 3 a 20": "3_20",
    "De 21 a 50": "21_50",
    "Más de 50": "over_50",
    # renewable energy device type
    "No dispone de dispositivo de energía renovable": "none",
    "Un único tipo de dispositivo: Energía solar fotovoltaica, eólica, biomasa, etc": "solar_pv_wind_biomass",
    "Un único tipo de dispositivo: Energía solar térmica": "solar_thermal",
}


def _to_snake_case(name):
    """Normalise an identifier to ``snake_case`` (CamelCase, acronym runs and
    free text with spaces/punctuation all handled)."""
    if name is None:
        return name
    s = str(name).strip()
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    s = re.sub(r'[^a-zA-Z0-9]+', '_', s)
    return s.strip('_').lower()


def _ec_camelize(text):
    """Accent-stripped PascalCase fallback for text absent from the maps."""
    t = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    t = re.sub(r"[^0-9A-Za-z]+", " ", t).strip()
    return "".join(w[:1].upper() + w[1:] for w in t.split()) if t else ""


def _clean_ec_part(text):
    """Strip whitespace, a trailing ``(%)`` marker and trailing punctuation."""
    t = re.sub(r"\s*\(%\)\s*$", "", str(text)).strip()
    return t.rstrip(",.").strip()


def _translate_ec_part(text, mapping):
    cleaned = _clean_ec_part(text)
    if cleaned in mapping:
        return mapping[cleaned]
    return _to_snake_case(_ec_camelize(cleaned))


def _normalise_household_group(group):
    """Rewrite an INE ``Hogares/personas...`` group title as ``Hogares...``.

    Those tables carry a ``Unidad`` column and are filtered down to
    ``'Cantidad de hogares'`` further below, so they count households just like
    their ``Hogares...`` counterparts and only differ in the variable INE
    cross-tabulates them by. Sharing one group name lets both feed a single
    output variable, whose per-table downscalings are then averaged.
    """
    return re.sub(r"^Hogares/personas\b", "Hogares", str(group))


def _drop_leading_overlap(group_part, variable_part):
    """Drop the head of ``variable_part`` that the tail of ``group_part`` already
    states, so that a group named after its own variable does not stutter:
    ``hh_paid_domestic`` + ``paid_domestic`` -> ``''`` and ``hh_second_home`` +
    ``second_home_place`` -> ``place``. Returns ``variable_part`` untouched when
    the two do not overlap."""
    if not group_part or not variable_part:
        return variable_part
    g, v = group_part.split("_"), variable_part.split("_")
    for n in range(min(len(g), len(v)), 0, -1):
        if g[-n:] == v[:n]:
            return "_".join(v[n:])
    return variable_part


def translate_essential_characteristic(name):
    """Translate one raw Spanish characteristic name to English snake_case.

    Parses ``{group} - {variable} ~ {subclass}`` (the ``~ {subclass}`` part is
    optional, as in the returned dict keys). Group and variable are joined with
    underscores and the subclass is appended after a ``~``, e.g.
    ``Viviendas principales - Tipo de calefacción ~ Sí, individual``
    -> ``main_dwellings_heating~individual``. Names without the ``-``/``~``
    separators (already-English or non-characteristic labels) are returned
    unchanged, so a second pass is a no-op.
    """
    if not isinstance(name, str) or (" - " not in name and " ~ " not in name):
        return name
    left, sep, subclass = name.partition(" ~ ")
    group, gsep, variable = left.partition(" - ")
    group_part = _translate_ec_part(group, _EC_GROUPS)
    variable_part = _translate_ec_part(variable, _EC_VARIABLES) if gsep else ""
    subclass_part = _translate_ec_part(subclass, _EC_SUBCLASSES) if sep else ""
    head = "_".join(p for p in (group_part,
                                _drop_leading_overlap(group_part, variable_part)) if p)
    # The subclass is joined with "~" so that the variable a column belongs to stays
    # readable next to the class it measures, e.g. main_dwellings_conservation~good.
    return f"{head}~{subclass_part}" if subclass_part else head


def _scalar_code(value):
    """
    Normalise an INE code that may arrive as a scalar or as a list/tuple/array of
    codes (hypercadaster_ES stores one code per address, so a compacted building
    carries a list) into a plain string, or None when there is no usable code.
    """
    if isinstance(value, (list, tuple, np.ndarray)):
        value = value[0] if len(value) else None
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    return str(value)


def _dedupe_names(names):
    """Return ``names`` made unique positionally, appending _2, _3… on collision
    (positional so it is safe even when the input list has repeated labels)."""
    out, seen = [], {}
    for name in names:
        n = seen.get(name, 0) + 1
        seen[name] = n
        out.append(name if n == 1 else f"{name}_{n}")
    return out


def EssentialCharacteristicsOfPopulationAndHouseholds(
        wd, hypercadaster_ES_input_pkl_file=None, hypercadaster_ES_input_gdf=None):
    # Year 2021, more info:
    # https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177092&menu=resultados&idp=1254735572981

    path = "INE/EssentialCharacteristicsOfPopulationAndHouseholds"
    path = path_creator(path, wd)
    # _v2: the cached metadata of earlier releases was built with a variable-splitting
    # bug that emitted a spurious "<variable> 2" entry for every variable published in
    # more than one INE table, so the old caches must be rebuilt.
    filenames = {
        "variables_meta": f"{path}/variables_meta_v2.pkl",
        "filtering_variables": f"{path}/filtering_variables_v2.pkl",
        "dfs": f"{path}/dfs_v2.pkl"
    }

    base_link = "https://www.ine.es/dynt3/inebase/es/index.htm"
    links_to_obtain_ids = {
        "People": {
            "Mobility": "?padre=8983&capsel=8987",
            "FamilyDynamics": "?padre=8988&capsel=8992",
            "SocialSupport": "?padre=8993&capsel=8997",
            "FamilyOrigin": "?padre=8998&capsel=9002",
            "ContactWithNewTechnologies": "?padre=9003&capsel=9007"
        },
        "Homes": {
            "FamilyUnit": "?padre=9545&capsel=9549",
            "OneSinglePerson": "?padre=9550&capsel=9554",
            "Couples": "?padre=9555&capsel=9559",
            "Monoparental": "?padre=9560&capsel=9564",
            "SizeCharacteristics": "?padre=9565&capsel=9569",
            "Ownership": "?padre=9570&capsel=9574",
            "SecondHomes": "?padre=9575&capsel=9579",
            "Vehicles": "?padre=9580&capsel=9584",
            "WasteSeparation": "?padre=9585&capsel=9589",
            "DomesticServices": "?padre=9590&capsel=9594"
        },
        "Households": {
            "Installations": "?padre=9595&capsel=9599",
            "MainHouseholdSizes": "?padre=9600&capsel=9604",
            "MainHouseholdContexts": "?padre=9605&capsel=9609",
            "AccessibilityAndConservation": "?padre=9610&capsel=9614",
            "BuildingInstallation": "?padre=9615&capsel=9619"
        }
    }

    if not all([os.path.exists(filename) for filename in filenames.values()]):

        print("Reading the metadata to gather the INE essential characteristics of population and households", file=sys.stdout)
        mun_df = MunicipalityNamesToMunicipalityCodes()
        dfs = {}
        for related_to, sections_dict in links_to_obtain_ids.items():
            dfs[related_to] = []
            #related_to, sections_dict = list(links_to_obtain_ids.items())[2]
            for subject, sections_link in sections_dict.items():
                #subject, sections_link = list(sections_dict.items())[3]
                req = request_with_retries(f"{base_link}{sections_link}", headers={'User-Agent': 'Chrome/51.0.2704.103'})
                ids = extract_titles_and_ids(req.text)
                urls = {k: f"https://www.ine.es/jaxi/files/tpx/es/csv_bd/{v}.csv?nocab=1" for k,v in ids.items()}
                for k,url in urls.items():
                    r = request_with_retries(url, expect_csv=True)
                    r.encoding = 'utf-8'
                    df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", low_memory=False)
                    df_ = df_.rename({"Municipalities": "Municipios", "ï»¿Municipios": "Municipios"}, axis="columns")
                    df_ = df_.merge(mun_df, left_on="Municipios", right_on="Municipality name")
                    df_["Municipios"] = df_["Municipality code"]
                    df_ = df_.drop(["Municipality name", "Municipality code"], axis="columns")
                    # if municipality_code is not None:
                    #     df_ = df_.loc[
                    #           df_["Municipios"].isin(
                    #               municipality_code if isinstance(municipality_code,list) else [municipality_code]),
                    #           :]
                    df_["Total"] = np.where(df_["Total"]==".", np.nan, df_["Total"])
                    df_["Total"] = np.where(df_["Total"]=="..", np.nan, df_["Total"])
                    if df_["Total"].dtype=="object":
                        df_["Total"] = df_["Total"].str.replace(".", "")
                        df_["Total"] = df_["Total"].str.replace(",",".").astype("float", errors="ignore")
                    cols = list(df_.columns)
                    pattern = r"^(.*?)(?=\b(por|según)\b)"
                    match = re.match(pattern, k)
                    if match:
                        k = match.group(1).strip()
                    cols[-2] = _normalise_household_group(k) + " - " + cols[-2]
                    df_.columns = cols
                    dfs[related_to].append(df_)

        variables_meta = {}
        filtering_variables = {}
        classes_variables = {}
        variables_split = {}
        for k in dfs.keys():
            for i in range(len(dfs[k])):
                if "Unidad" in dfs[k][i].columns:
                    dfs[k][i] = dfs[k][i][dfs[k][i]["Unidad"]=='Cantidad de hogares'] #Cantidad de personas
                    dfs[k][i].drop(columns=["Unidad"], inplace=True)
                column_name = dfs[k][i].columns[-2]  # Get the second-to-last column name
                column_filters = list(dfs[k][i].columns[[r not in [column_name, "Total"] for r in list(dfs[k][i].columns)]])
                if not all([col in ['Municipios', 'Edad', 'Sexo',
                    'Nivel de ingresos mensuales netos del hogar', 'Nacionalidad de los miembros del hogar',
                    'Superficie útil de la vivienda', 'Tipo de edificio', 'Año de construcción del edificio',
                    'Número de miembros del hogar'] for col in column_filters]):
                    continue
                if column_name not in variables_split:
                    variables_split[column_name] = {}
                subclasses = sorted(list(dfs[k][i][column_name].unique()))
                if "~".join(subclasses) not in variables_split[column_name]:
                    variables_split[column_name]["~".join(subclasses)] = (
                        f" {str(len(variables_split[column_name])+1)}" if len(variables_split[column_name]) >= 1 else "")
                column_name_df = column_name
                column_name = f"{column_name}{variables_split[column_name]["~".join(subclasses)]}"
                if column_name not in variables_meta:
                    variables_meta[column_name] = {}
                    variables_meta[column_name]['NameInDataFrame'] = column_name_df
                if column_name not in classes_variables:
                    classes_variables[column_name] = list(subclasses)
                else:
                    new_values = dfs[k][i][column_name_df].unique()
                    for val in new_values:
                        if val not in classes_variables[column_name]:
                            classes_variables[column_name].append(val)
                for colf in column_filters:
                    if colf in filtering_variables:
                        new_values = dfs[k][i][colf].unique()
                        for val in new_values:
                            if val not in filtering_variables[colf]:
                                filtering_variables[colf].append(val)
                    else:
                        filtering_variables[colf] = list(dfs[k][i][colf].unique())
                if "FilteringVariables" in variables_meta[column_name]:
                    variables_meta[column_name]["FilteringVariables"].append(column_filters)
                else:
                    variables_meta[column_name]["FilteringVariables"] = [column_filters]
                if "ElementDfs" in variables_meta[column_name]:
                    variables_meta[column_name]["ElementDfs"].append((k,i))
                else:
                    variables_meta[column_name]["ElementDfs"] = [(k,i)]
                if "Total" in variables_meta[column_name]:
                    variables_meta[column_name]["Total"].append(dfs[k][i].columns[-1])
                else:
                    variables_meta[column_name]["Total"] = [dfs[k][i].columns[-1]]

        with open(filenames["variables_meta"], "wb") as f:
            pickle.dump(variables_meta, f)
        with open(filenames["filtering_variables"], "wb") as f:
            pickle.dump(filtering_variables, f)
        with open(filenames["dfs"], "wb") as f:
            pickle.dump(dfs, f)

    else:

        with open(filenames["variables_meta"], "rb") as f:
            variables_meta = pickle.load(f)
        with open(filenames["filtering_variables"], "rb") as f:
            filtering_variables = pickle.load(f)
        with open(filenames["dfs"], "rb") as f:
            dfs = pickle.load(f)

    atlas_df = HouseholdIncomeDistributionAtlas(wd=wd)['Census tracts']
    atlas_df = atlas_df[atlas_df.Year==2021]
    population_df = PopulationCensus(wd=wd)['Census tracts']
    population_df = population_df[population_df.Year==2021]
    atlas_df["census_tract_code"] = atlas_df["Municipality code"] + atlas_df["District code"] + atlas_df["Census tract code"]
    atlas_df.drop(columns=["Municipality code", "District code", "Census tract code"], inplace=True)
    population_df["census_tract_code"] = population_df["Municipality code"] + population_df["District code"] + population_df["Census tract code"]
    population_df.drop(columns=["Municipality code", "District code", "Census tract code"], inplace=True)
    social_df = atlas_df.merge(population_df, on="census_tract_code", how="left")

    # Calculation of the consumption units per household
    social_df["Menores de 14 años por hogar"] = social_df["Average size of the household"] / social_df['Population_y'] * (
        social_df['Population ~ Age:10-14'] + social_df['Population ~ Age:5-9'] + social_df['Population ~ Age:0-4'])
    social_df["Mayores de 15 años por hogar"] = social_df["Average size of the household"] - social_df["Menores de 14 años por hogar"]
    social_df["Unidades de consumo medio en el hogar"] = (
        (social_df["Mayores de 15 años por hogar"]).clip(upper=1) +
        (social_df["Mayores de 15 años por hogar"]-1).clip(lower=0)*0.5 +
        social_df["Menores de 14 años por hogar"]*0.3)

    social_df = pd.concat([social_df, social_df.apply(estimate_income_distribution, axis=1)], axis=1)
    social_df = pd.concat([social_df, social_df.apply(estimate_nationality_households, axis=1)], axis=1)

    if hypercadaster_ES_input_gdf is not None:
        hypercadaster_df = hypercadaster_ES_input_gdf.copy()
    else:
        hypercadaster_df = pd.read_pickle(hypercadaster_ES_input_pkl_file, compression="gzip")

    # Defensive rename: hypercadaster_ES exports the merge key as "section_code".
    # Rename it to the new internal key so social_ES stays self-contained without
    # requiring a matching hypercadaster_ES release. No-op once the upstream
    # export uses "census_tract_code".
    if "section_code" in hypercadaster_df.columns:
        hypercadaster_df = hypercadaster_df.rename(columns={"section_code": "census_tract_code"})

    # After address compaction hypercadaster_ES stores the code as a list (a
    # building can span more than one census tract). The downscaling below merges
    # and groups on a scalar key, and exploding the lists would duplicate
    # buildings and double-count their area, so keep the first code per building.
    hypercadaster_df["census_tract_code"] = hypercadaster_df["census_tract_code"].map(_scalar_code)
    hypercadaster_df = hypercadaster_df[hypercadaster_df["census_tract_code"].notna()]

    exogenous_df = hypercadaster_df.merge(social_df, on="census_tract_code")
    residential_area_by_census_tract_code = exogenous_df.groupby("census_tract_code")[
        "br__area_without_communals"] \
        .apply(lambda x: x.apply(extract_residential).sum())
    exogenous_df = exogenous_df.merge(residential_area_by_census_tract_code.reset_index().rename(
        columns={'br__area_without_communals': 'residential_area_in_census_tract_code'}
    ), on="census_tract_code")
    exogenous_df["residential_area"] = exogenous_df["br__area_without_communals"].apply(
        extract_residential)
    exogenous_df["residential_spaces"] = exogenous_df["br__building_spaces"].apply(extract_residential)
    exogenous_df["number_of_people_in_households"] = \
        (exogenous_df['Population_y'] *
         exogenous_df['residential_area'] /
         exogenous_df['residential_area_in_census_tract_code']) / exogenous_df['residential_spaces']
    exogenous_df = exogenous_df[~exogenous_df['residential_area'].isna()]
    cases = {
        'Edad': {
            'Menos de 30 años': ((exogenous_df['Population ~ Age:0-4'] + exogenous_df['Population ~ Age:5-9'] +
                                  exogenous_df['Population ~ Age:10-14'] + exogenous_df['Population ~ Age:15-19'] +
                                  exogenous_df['Population ~ Age:20-24'] + exogenous_df['Population ~ Age:25-29']) /
                                 exogenous_df["Population_y"]),
            'Menos de 40 años': ((exogenous_df['Population ~ Age:0-4'] + exogenous_df['Population ~ Age:5-9'] +
                                  exogenous_df['Population ~ Age:10-14'] + exogenous_df['Population ~ Age:15-19'] +
                                  exogenous_df['Population ~ Age:20-24'] + exogenous_df['Population ~ Age:25-29'] +
                                  exogenous_df['Population ~ Age:30-34'] + exogenous_df['Population ~ Age:35-39']) /
                                 exogenous_df["Population_y"]),
            'De 30 a 49 años': (exogenous_df['Population ~ Age:30-34'] + exogenous_df['Population ~ Age:35-39'] +
                                exogenous_df['Population ~ Age:40-44'] + exogenous_df['Population ~ Age:45-49']) /
                               exogenous_df["Population_y"],
            'De 30 a 39 años': (exogenous_df['Population ~ Age:30-34'] + exogenous_df['Population ~ Age:35-39']) /
                               exogenous_df["Population_y"],
            'De 40 a 59 años': (exogenous_df['Population ~ Age:40-44'] + exogenous_df['Population ~ Age:45-49'] +
                                exogenous_df['Population ~ Age:50-54'] + exogenous_df['Population ~ Age:55-59']) /
                               exogenous_df["Population_y"],
            'De 40 a 49 años': (exogenous_df['Population ~ Age:40-44'] + exogenous_df['Population ~ Age:45-49']) /
                               exogenous_df["Population_y"],
            'De 50 a 59 años': (exogenous_df['Population ~ Age:50-54'] + exogenous_df['Population ~ Age:55-59']) /
                               exogenous_df["Population_y"],
            'De 60 a 69 años': (exogenous_df['Population ~ Age:60-64'] + exogenous_df['Population ~ Age:65-69']) /
                               exogenous_df["Population_y"],
            'De 70 a 79 años': (exogenous_df['Population ~ Age:70-74'] + exogenous_df['Population ~ Age:75-79']) /
                               exogenous_df["Population_y"],
            'De 50 y más años': ((exogenous_df['Population ~ Age:50-54'] + exogenous_df['Population ~ Age:55-59'] +
                                  exogenous_df['Population ~ Age:60-64'] + exogenous_df['Population ~ Age:65-69'] +
                                  exogenous_df['Population ~ Age:70-74'] + exogenous_df['Population ~ Age:75-79'] +
                                  exogenous_df['Population ~ Age:80-84'] + exogenous_df['Population ~ Age:85-89'] +
                                  exogenous_df['Population ~ Age:90-94'] + exogenous_df['Population ~ Age:95-99'] +
                                  exogenous_df['Population ~ Age:>99']) /
                                 exogenous_df["Population_y"]),
            'De 60 y más años': ((exogenous_df['Population ~ Age:60-64'] + exogenous_df['Population ~ Age:65-69'] +
                                  exogenous_df['Population ~ Age:70-74'] + exogenous_df['Population ~ Age:75-79'] +
                                  exogenous_df['Population ~ Age:80-84'] + exogenous_df['Population ~ Age:85-89'] +
                                  exogenous_df['Population ~ Age:90-94'] + exogenous_df['Population ~ Age:95-99'] +
                                  exogenous_df['Population ~ Age:>99']) /
                                 exogenous_df["Population_y"]),
            'De 70 y más años': ((exogenous_df['Population ~ Age:70-74'] + exogenous_df['Population ~ Age:75-79'] +
                                  exogenous_df['Population ~ Age:80-84'] + exogenous_df['Population ~ Age:85-89'] +
                                  exogenous_df['Population ~ Age:90-94'] + exogenous_df['Population ~ Age:95-99'] +
                                  exogenous_df['Population ~ Age:>99']) /
                                 exogenous_df["Population_y"]),
            'De 80 y más años': ((exogenous_df['Population ~ Age:80-84'] + exogenous_df['Population ~ Age:85-89'] +
                                  exogenous_df['Population ~ Age:90-94'] + exogenous_df['Population ~ Age:95-99'] +
                                  exogenous_df['Population ~ Age:>99']) /
                                 exogenous_df["Population_y"]),
        },
        'Sexo': {
            'Hombre': exogenous_df['Population ~ Sex:Males'] / exogenous_df["Population_y"],
            'Mujer': exogenous_df['Population ~ Sex:Females'] / exogenous_df["Population_y"]
        },
        'Nivel de ingresos mensuales netos del hogar': {
            'Menos de 500 euros': exogenous_df["Salario mensual neto del hogar de menos de 500 euros"] / 100,
            'De 500 euros a menos de 1.000 euros': exogenous_df[
                'Salario mensual neto del hogar de 500 euros a menos de 1.000 euros'] / 100,
            'Menos de 1.000 euros': exogenous_df["Salario mensual neto del hogar de menos de 1.000 euros"] / 100,
            'De 1.000 euros a menos de 1.500 euros': exogenous_df[
                'Salario mensual neto del hogar de 1.000 euros a menos de 1.500 euros'] / 100,
            'De 1.500 euros a menos de 2.000 euros': exogenous_df[
                'Salario mensual neto del hogar de 1.500 euros a menos de 2.000 euros'] / 100,
            'De 2.000 euros a menos de 3.000 euros': exogenous_df[
                'Salario mensual neto del hogar de 2.000 euros a menos de 3.000 euros'] / 100,
            'De 2.000 euros a menos de 2.500 euros': exogenous_df[
                                                         'Salario mensual neto del hogar de 2.000 euros a menos de 2.500 euros'] / 100,
            'De 2.500 euros a menos de 3.000 euros': exogenous_df[
                                                         'Salario mensual neto del hogar de 2.500 euros a menos de 3.000 euros'] / 100,
            '3.000 euros o más': exogenous_df['Salario mensual neto del hogar de 3.000 euros o más'] / 100,
            'De 3.000 euros a menos de 5.000 euros': exogenous_df[
                                                         'Salario mensual neto del hogar de 3.000 euros a menos de 5.000 euros'] / 100,
            'De 5.000 euros o más': exogenous_df['Salario mensual neto del hogar de 5.000 euros o más'] / 100
        },
        'Nacionalidad de los miembros del hogar': {
            'Hogar exclusivamente español': exogenous_df["Hogar exclusivamente español"] / 100,
            'Hogar mixto (con españoles y extranjeros)': exogenous_df["Hogar mixto (con españoles y extranjeros)"] / 100,
            'Hogar exclusivamente extranjero': exogenous_df["Hogar exclusivamente extranjero"] / 100
        },
        'Superficie útil de la vivienda': {
            'Hasta 75 m2': np.where((exogenous_df["residential_area"]/exogenous_df["residential_spaces"]) < 76, 1, 0),
            'Entre 76 y 90 m2': np.where(((exogenous_df["residential_area"]/exogenous_df["residential_spaces"]) >= 76) &
                                         ((exogenous_df["residential_area"]/exogenous_df["residential_spaces"]) < 91), 1, 0),
            'Entre 91 y 120 m2': np.where(((exogenous_df["residential_area"]/exogenous_df["residential_spaces"]) >= 91) &
                                          ((exogenous_df["residential_area"]/exogenous_df["residential_spaces"]) < 121), 1, 0),
            'Más de 120 m2': np.where((exogenous_df["residential_area"]/exogenous_df["residential_spaces"]) >= 121, 1, 0)
        },
        'Tipo de edificio': {
            'Vivienda unifamiliar (chalet, adosado, pareado...)':
                np.where(exogenous_df["residential_spaces"]==1, 1, 0),
            'Edificio de 2 o más viviendas':
                np.where(exogenous_df["residential_spaces"]>1, 1, 0)
        },
        'Año de construcción del edificio': {
            '1990 y anterior': np.where(~exogenous_df["year_of_construction"].isna() &
                                        (exogenous_df["year_of_construction"] <= 1990), 1, 0),
            'Posterior a 1990': np.where(~exogenous_df["year_of_construction"].isna() &
                                         (exogenous_df["year_of_construction"] > 1990), 1, 0),
            '2000 y anterior': np.where(~exogenous_df["year_of_construction"].isna() &
                                        (exogenous_df["year_of_construction"] <= 2000), 1, 0),
            'Posterior a 2000': np.where(~exogenous_df["year_of_construction"].isna() &
                                         (exogenous_df["year_of_construction"] > 2000), 1, 0)
        },
        'Número de miembros del hogar': {
            '1 persona': np.where(exogenous_df["number_of_people_in_households"] < 1.5, 1, 0),
            '2 personas': np.where((exogenous_df["number_of_people_in_households"] >= 1.5) &
                                   (exogenous_df["number_of_people_in_households"] < 2.5), 1, 0),
            '3 personas': np.where((exogenous_df["number_of_people_in_households"] >= 2.5) &
                                   (exogenous_df["number_of_people_in_households"] < 3.5), 1, 0),

            '4 personas': np.where((exogenous_df["number_of_people_in_households"] >= 3.5) &
                                   (exogenous_df["number_of_people_in_households"] < 4.5), 1, 0),
            '4 personas o más': np.where(exogenous_df["number_of_people_in_households"] >= 3.5, 1, 0),
            '5 personas o más': np.where(exogenous_df["number_of_people_in_households"] >= 4.5, 1, 0)
        }
    }

    flattened = {}
    for category, subcats in cases.items():
        for label, series in subcats.items():
            flattened[f"{category} ~ {label}"] = series

    # Create a new DataFrame
    cases_df = pd.DataFrame(flattened)
    cases_df["Municipios"] = exogenous_df["ine_code"]
    cases_df["building_reference"] = exogenous_df["building_reference"]
    cases_df.set_index("building_reference", inplace=True)

    total_element_of_variables = {
        'Lugar de trabajo/estudio': 'Total',
        'Número de desplazamaientos': 'Total',
        'Medio de transporte': 'Total',
        'Tipo de vehículo': 'Total',
        'Tiempo diario': 'Total',
        'Grado de satisfacción': 'Total',
        'Grado de participación en las tareas domésticas': 'Total',
        'Grado de participación en cuidados a menores o dependientes dentro del hogar': 'Total',
        'Tipo de dependiente': 'Total',
        'Horas diarias dedicadas al cuidado': 'Total',
        'Grado de participación en cuidados a menores o dependientes fuera del hogar': 'Total',
        'Tiene apoyo social': 'Total',
        'Tipo de relación': 'Total',
        'Lugar de residencia': 'Total',
        'Lugar de nacimiento progenitores': 'Total',
        'Residencia progenitores': 'Total',
        'Nacionalidad progenitores': 'Total',
        'Nivel estudios progenitores': 'Total',
        'Accede habitualmente a internet': 'Total',
        'Dispone de perfil en alguna red social': 'Total',
        'Dispone de smartphone': 'Total',
        'Realiza compras por internet': 'Total',
        'Realiza ventas por internet': 'Total',
        'Language': None,
        'Número de hijos': 'Total',
        'Edad': 'Total',
        'Nacionalidad': 'Total',
        'Estado civil': 'Total',
        'Nivel educativo': 'Total',
        'Situación laboral': 'Total',
        'Nivel de ingresos mensuales netos del hogar': 'Total',
        'Sexo de la pareja': 'Total',
        'Nacionalidad de la pareja': 'Total',
        'Número de habitaciones de la vivienda': 'Total',
        'Superficie útil de la vivienda': 'Total',
        'Tipo de edificio': 'Total',
        'Régimen de tenencia de la vivienda': 'Total',
        'Cuota mensual del alquiler': 'Total',
        'Cuota mensual de la hipoteca': 'Total',
        'Disponen de segunda residencia': 'Total',
        'Lugar de la segunda residencia': 'Total',
        'Días de uso de la segunda residencia al año': 'Total',
        'Número de vehículos': 'Total',
        'Vehículo ecólogico': 'Total',
        'Separan algún tipo de residuo': 'Total',
        'Tipo de residuos separados': 'Total (valores absolutos)',
        'Servicio doméstico remunerado': 'Total',
        'Ayuda externa': 'Total',
        'Adaptada a necesidades propias del envejecimiento': 'Total',
        'Problema de aislamiento': 'Total',
        'Tipo de calefacción': 'Total',
        'Tipo de combustible': 'Total',
        'Sistema de suministro de agua': 'Total',
        'Tiene sistema de refrigeración': 'Total',
        'Tipo de conexión a internet': 'Total',
        'Tipo de electrodoméstico': 'Total (valores absolutos)',
        'Tipo de bombillas': 'Total (valores absolutos)',
        'Aseo con inodoro / Bañera o ducha': 'Total (valores absolutos)',
        'Número de cuartos de baño o aseos': 'Total',
        'Cocina independiente de 4 m2 o más': 'Total',
        'Número de habitaciones': 'Total',
        'Tipo de problemática en la zona': 'Total (valores absolutos)',
        'Tipo de infraestructura o servicio': 'Total (valores absolutos)',
        'Estado de conservación': 'Total',
        'Accesibilidad': 'Total',
        'Tipo de instalación': 'Total (valores absolutos)',
        'Número de plazas de garaje': 'Total',
        'Tipo de dispositivo de energía renovable': 'Total'}
    total_element_of_filtering_variables = {
        'Edad': 'Total',
        'Sexo': 'Ambos Sexos',
        'Tipo de núcleo familiar': 'Total',
        'Tipo de unión': 'Total',
        'Nivel educativo alcanzado de la pareja': 'Total',
        'Situación laboral de la pareja': 'Total',
        'Nivel de ingresos mensuales netos del hogar': 'Total',
        'Sexo del progenitor': 'Ambos Sexos',
        'Estado civil del progenitor': 'Total',
        'Nivel educativo del progenitor': 'Total',
        'Situación laboral del progenitor': 'Total',
        'Tipo de hogar': 'Total',
        'Número de miembros del hogar': 'Total',
        'Nivel de estudios alcanzado por los miembros del hogar': 'Total',
        'Situación laboral de los miembros del hogar': 'Total',
        'Tipo de edificio': 'Total',
        'Año de construcción del edificio': 'Total',
        'Nacionalidad de los miembros del hogar': 'Total',
        'Superficie útil de la vivienda': 'Total'
    }

    all_proportion_dfs = {}
    for variable in tqdm(variables_meta.keys(), desc="Downscale each variable to building level..."):
        variable_meta = variables_meta[variable]
        variable = variable_meta['NameInDataFrame']
        if variable not in all_proportion_dfs:
            all_proportion_dfs[variable] = []
        for i, (gr, elem) in enumerate(variable_meta["ElementDfs"]):
            filt_vars = variable_meta["FilteringVariables"][i]
            df_ = dfs[gr][elem][dfs[gr][elem]["Municipios"].isin(cases_df["Municipios"].unique())]
            #df_[variable_meta["Total"][0]] = df_[variable_meta["Total"][i]].astype(str).str.replace(".","").astype("float")
            df_.loc[:, variable_meta["Total"][0]] = (
                df_[variable_meta["Total"][i]].astype(str).str.replace(".", "", regex=False).astype(float)
            )
            df_ = df_[df_[variable_meta['NameInDataFrame']] != total_element_of_variables[variable_meta['NameInDataFrame'].split(" - ")[1]]].copy()
            totals_by_group = df_.groupby(filt_vars)[variable_meta["Total"][i]].transform("sum")
            totals_safe = totals_by_group.astype(float).replace(0.0, np.nan)

            # Avoid division issues by making sure everything is float
            numerator = pd.to_numeric(df_[variable_meta["Total"][i]], errors="coerce")
            denominator = pd.to_numeric(totals_safe, errors="coerce")
            df_.loc[:, "Proportion"] = numerator * 100 / denominator

            filt_vars_ = [v for v in filt_vars if "Municipios" not in v]
            if len(filt_vars_) > 0:
                mask = pd.DataFrame(
                    {col: df_[col] == total_element_of_filtering_variables[col] for col in filt_vars_}
                )
                df_ = df_[~mask.any(axis=1)]

                for filt_var in filt_vars_:
                    # One-hot encode the 'Número de miembros del hogar' column
                    one_hot = pd.get_dummies(df_[filt_var], prefix=filt_var,dtype=int,prefix_sep=' ~ ')
                    # Concatenate the one-hot columns back to the original dataframe
                    df_.drop(columns=[filt_var], inplace=True)
                    df_ = pd.concat([df_, one_hot], axis=1)

            df_ = df_.drop(columns=["Total"])

            pivot_df = df_.pivot_table(
                index=[col for col in df_.columns if
                       col not in [variable_meta['NameInDataFrame'], "Proportion"]],
                columns=variable_meta['NameInDataFrame'],
                values="Proportion"
            )
            variable_and_subs = pivot_df.columns = [f"{variable_meta['NameInDataFrame']} ~ {col}" for col in pivot_df.columns]
            pivot_df = pivot_df.reset_index()
            filt_vars_pivot = [i for i in pivot_df.columns if not i.startswith(variable_meta['NameInDataFrame'])]
            filt_vars__pivot = [i for i in pivot_df.columns if
                any([i.startswith(j) for j in filt_vars_])]
            cases_df_ = cases_df[
                [col for col in cases_df.columns if
                 any(col.startswith(f"{filt_var}") for filt_var in filt_vars)]
            ]
            filt_vars__pivot = [i for i in filt_vars__pivot if i in cases_df_.columns]
            cases_df_ = cases_df_[filt_vars_pivot]

            # Loop over each target variable
            for target in variable_and_subs:
                if len(filt_vars_)>0:
                    results = []
                    pivot_df_vars = [col for col in pivot_df.columns if any(col.startswith(filt_var) for filt_var in filt_vars_)]

                    if ((cases_df_[pivot_df_vars].values == 0) | (cases_df_[pivot_df_vars].values == 1)).all():
                        cases_df_aux = (cases_df_.reset_index().
                                        merge(pd.DataFrame(pivot_df[["Municipios", target] + pivot_df_vars]), on=["Municipios"] + pivot_df_vars,
                                              how="left").
                                        set_index("building_reference"))
                        cases_df_[target] = cases_df_aux[target]

                    else:
                        for municipio, group in pivot_df.groupby("Municipios"):
                            #municipio, group = list(pivot_df.groupby("Municipios"))[0]
                            # Filter predictor matrix A
                            A = group[pivot_df_vars]

                            # Ensure it's square
                            try:
                                b = group[target].astype(float)
                                # INE suppresses cells below its reliability threshold ('.'),
                                # which arrive here as NaN. np.linalg.lstsq propagates a single
                                # NaN to every coefficient, so fit on the published strata only
                                # instead of losing the whole municipality.
                                observed = b.notna().values
                                if not observed.any():
                                    continue
                                x, residuals, rank, s = np.linalg.lstsq(
                                    A.values[observed], b.values[observed], rcond=None)
                                result_row = pd.Series(x, index=A.columns)
                                result_row["Municipios"] = municipio
                                results.append(result_row)
                            except np.linalg.LinAlgError:
                                print(f"Singular system for {municipio} with target {target}")

                        cases_df_aux = (cases_df_.reset_index().
                                        merge(pd.DataFrame(results), on="Municipios", how="left").
                                        set_index("building_reference"))
                        cases_df_aux = (
                                cases_df_aux[[f"{i}_x" for i in filt_vars__pivot]].rename(
                                    columns={f"{i}_x": i for i in filt_vars__pivot}
                                ) *
                                cases_df_aux[[f"{i}_y" for i in filt_vars__pivot]].rename(
                                    columns={f"{i}_y": i for i in filt_vars__pivot}
                                ))
                        cases_df_[target] = cases_df_aux.sum(axis=1).fillna(0)
                else:
                    cases_df_aux = (cases_df_.reset_index().
                                    merge(pd.DataFrame(pivot_df[["Municipios", target]]), on="Municipios", how="left").
                                    set_index("building_reference"))
                    cases_df_[target] = cases_df_aux[target].fillna(0)

            all_proportion_dfs[variable].append(cases_df_[variable_and_subs])

    all_proportion_df = {}
    for variable in tqdm(variables_meta.keys(), desc="Creating the summarized dataframe per each variable..."):
        variable_meta = variables_meta[variable]
        variable = variable_meta['NameInDataFrame']

        ldfs = all_proportion_dfs[variable]  # list of DataFrames
        # 1) Stack side-by-side (outer join to allow different columns)
        combined = pd.concat(ldfs, axis=1, join="outer")
        # 2) Row-wise mean across dataframes for each column name
        #    (columns that exist in fewer DFs are averaged over those available; NaNs are ignored)
        out = combined.T.groupby(level=0).mean().T  # equivalent to groupby(level=0, axis=1).mean()
        # 3) (Optional) Reorder columns to match the first DF, keeping any extras at the end
        first_cols = ldfs[0].columns
        extra_cols = [c for c in out.columns if c not in first_cols]
        out = out.reindex(columns=list(first_cols) + extra_cols)
        # 4) Assign back
        all_proportion_df[variable] = out

        # Normalization 0-100
        row_sums = all_proportion_df[variable].sum(axis=1).values[:, None]  # shape (n, 1)
        index = all_proportion_df[variable].index
        cols = all_proportion_df[variable].columns
        all_proportion_df[variable] = (all_proportion_df[variable].values * 100) / row_sums
        all_proportion_df[variable] = pd.DataFrame(
            all_proportion_df[variable],
            index=index,
            columns=cols
        )

    # Translate the Spanish INE labels (both the dict keys and the column names)
    # to short English snake_case, e.g. 'Viviendas principales - Tipo de
    # calefacción ~ Sí, individual' -> 'main_dwellings_heating~individual'.
    translated = {}
    for variable, df in all_proportion_df.items():
        df = df.copy()
        df.columns = _dedupe_names(
            [translate_essential_characteristic(c) for c in df.columns])
        new_key = translate_essential_characteristic(variable)
        if new_key in translated:  # keep distinct if two keys collide
            i = 2
            while f"{new_key}_{i}" in translated:
                i += 1
            new_key = f"{new_key}_{i}"
        translated[new_key] = df

    # ECEPOV publishes a handful of dwelling attributes twice: once counting households
    # and once counting main dwellings. The main-dwelling table carries the same
    # information, so drop the redundant household variant. The two prefixes are read
    # from _EC_GROUPS rather than hardcoded, so renaming a group there keeps working.
    households, main_dwellings = _EC_GROUPS["Hogares"], _EC_GROUPS["Viviendas principales"]
    for key in [k for k in translated if k.startswith(f"{households}_")]:
        if f"{main_dwellings}_{key[len(households) + 1:]}" in translated:
            del translated[key]

    return dict(sorted(translated.items()))


def extract_residential(value):
    if pd.isna(value):
        return np.nan
    try:
        # Convert string dict to actual dict if needed
        if isinstance(value, str):
            d = ast.literal_eval(value)
        elif isinstance(value, dict):
            d = value
        else:
            return np.nan
        return d.get('Residential', np.nan)
    except Exception:
        return np.nan


def MunicipalityNamesToMunicipalityCodes():

    df = pd.read_excel("https://www.ine.es/daco/daco42/codmun/diccionario24.xlsx", header=1)
    df['Municipality code'] = df['CPRO'].astype(int).apply(lambda x: f"{x:02d}") +\
                              df['CMUN'].astype(int).apply(lambda x: f"{x:03d}")
    df.rename(columns = {'NOMBRE':'Municipality name'}, inplace=True)
    df.drop(columns = ["CODAUTO","CPRO","CMUN","DC"],inplace=True)

    return df


def AggregatedElectricityConsumption(wd, municipality_code=None, years=None):

    path = "INE/AggregatedElectricityConsumption"
    path = path_creator(path, wd)
    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):
        print("Downloading  electrical consumption...")
        DATA_CONSUMO = "https://www.ine.es/jaxi/files/tpx/en/csv_bd/59532.csv?nocab=1"

        g_df = fetch_data(DATA_CONSUMO, separation="\t")
        g_df['Municipality code'] = g_df['Distritos'].str[:5]
        g_df['District code'] = g_df['Distritos'].str[5:7]
        g_df['Municipality name'] = g_df['Distritos'].str.extract(r"^\d*(.+?)\sdistrito")
        g_df = g_df.pivot_table(index=['Municipality code', 'District code', 'Municipality name'], columns='Percentil', values='Total').reset_index()
        g_df.rename(columns=lambda x: re.sub(r'Percentil (\d+) de consumo eléctrico en kwh', r'Percentile \1 of electricity consumption in kwh', x), inplace = True)
        g_df['Year'] = '2021'
        g_df.to_csv(filename,sep="\t", index=False)

    else:
        g_df = pd.read_csv(filename,sep="\t",dtype={0:str,1:str,2:str})

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    if years != None:
        g_df = g_df[g_df['Year'].isin(years)]
    # municipality = g_df[-pd.isna(g_df["Municipality code"]) & pd.isna(g_df["District code"])]
    # municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["Municipality code"]) & -pd.isna(g_df["District code"])]
    districts = districts[districts.columns[districts.notna().any()]]

    return ({
        "Districts": districts
    })

# def Census2021(wd, municipality_code=None, years=None):
#
#     path = "INE/Census2021"
#     path = path_creator(path, wd)
#     filename = f"{path}/df.tsv"
#
#     censo_ingestion_urls = {
#         'Tamaño del hogar': {
#             'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/59543.csv?nocab=1',
#             'by':'Municipio',
#             'filter': lambda df: df.loc[(df['Municipality code'] != 'Total')],
#             'columns': {
#                 'rename':{'1 persona':'Households with 1 person', '2 personas':'Households with 2 people','3 personas':'Households with 3 people', '4 personas':'Households of 4 people', '5 o más personas':'Households of 5 or more people','Total (tamaño del hogar)': 'Total Households'}
#             }
#         },
#         'Tipo de vivienda (principal o no)': {
#             'url': 'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/59525.csv?nocab=1',
#             'by':'Municipio',
#             'filter': lambda df: df.loc[(df['Municipality code'] != 'Total')],
#             'columns': {
#                 'rename':{'Total':'Total Homes', 'Vivienda no principal':'Non-main Homes','Vivienda principal':'Main Homes'}
#             }
#         },
#         'Edad en grandes grupos': {
#             'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55242.csv',
#             'by':'Municipio de residencia',
#             'columns':{
#                 'aggregate':{
#                     'Population': lambda df: df.sum(axis=1,numeric_only=True),
#                     'Percentage of people between 16 (inclusive) and 64 (inclusive) years': lambda df: df['16-64']/ df['Population'],
#                     'Percentage of people over 64 years of age': lambda df: df['65 o más']/ df['Population'],
#                     'Percentage of people under 16 years': lambda df: df['Menos de 16']/ df['Population'],
#                 }
#             },
#             'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') &  (df['Nacionalidad (española/extranjera)'] == 'TOTAL')& (df['Sexo'] == 'Ambos sexos')],
#         },
#         'Sexo': {
#             'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55242.csv',
#             'by':'Municipio de residencia',
#             'columns':{
#                 'aggregate':{
#                     'Percentage of women': lambda df: df['Mujeres']/ df['Ambos sexos'],
#                     'Percentage of men': lambda df: df['Hombres']/ df['Ambos sexos'],
#                 }
#             },
#             'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Edad en grandes grupos'] == 'TOTAL') & (df['Nacionalidad (española/extranjera)'] == 'TOTAL') ],
#         },
#         'Nacionalidad (española/extranjera)': {
#             'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55242.csv',
#             'by':'Municipio de residencia',
#             'columns':{
#                 'aggregate':{
#                     'Percentage foreigners': lambda df: df['Extranjera']/ df['TOTAL'],
#                 }
#             },
#             'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Edad en grandes grupos'] == 'TOTAL') & (df['Sexo'] == 'Ambos sexos') ],
#         },
#         'Unidades de medida': {
#             'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55245.csv?nocab=1',
#             'by':'Municipio de residencia',
#             'filter': lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Nacionalidad (española/extranjera)'] == 'TOTAL') & (df['Sexo'] == 'Ambos sexos')],
#             'columns':{
#                 'rename':{'Edad media':'Average age'}
#             },
#         },
#         'País de nacimiento (grandes grupos)': {
#             'url': 'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55243.csv?nocab=1',
#             'by':'Municipio de residencia',
#             'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Sexo'] == 'Ambos sexos') ],
#             'columns': {
#                 'aggregate':{'Percentage of people born abroad': lambda df: 1 - (df['España'] / df['TOTAL'])}
#             },
#
#         },
#         'Nivel de estudios (grado)': {
#             'url': 'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55249.csv?nocab=1',
#             'by':'Municipio de residencia',
#             'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Nacionalidad (española/extranjera)'] == 'TOTAL') & (df['Sexo'] == 'Ambos sexos') ],
#             'columns': {
#                 'aggregate':{'Percentage of people with higher education (esreal_cneda=08 09 10 11 12) on population aged 16 and over': lambda df: df['Educación Superior']/(df['TOTAL'] - df['No aplicable (menor de 15 años)'])}
#             },
#
#         }
#     }
#
#     if not os.path.exists(filename):
#         print("Downloading Censo 2021..")
#         # Downloading Censo 2021
#         g_df = fetch_data("https://www.ine.es/censos2021/C2021_Indicadores.csv" ,separation=",", type=str)
#         g_df['cmun'] = g_df['cpro'] + g_df['cmun']
#         column_names = {'cmun':'Municipality code','dist':'District code', 'secc': 'Census tract code', 't1_1': 'Total People', 't2_1': 'Percentage of women', 't2_2': 'Percentage of men', 't3_1': 'Average age', 't4_1': 'Percentage of people under 16 years', 't4_2': 'Percentage of people between 16 (inclusive) and 64 (inclusive) years', 't4_3': 'Percentage of people over 64 years of age', 't5_1': 'Percentage foreigners', 't6_1': 'Percentage of people born abroad', 't7_1': 'Percentage of people pursuing higher education (escur =08 09 10 11 12 ) of the population aged 16 and over', 't8_1': 'Percentage of people pursuing university studies ( escur = 09 10 11 12) on population aged 16 and over', 't9_1': 'Percentage of people with higher education (esreal_cneda=08 09 10 11 12) on population aged 16 and over', 't10_1': 'Percentage of population unemployment over active population= Unemployed /Active', 't11_1': 'Percentage of employed population over population aged 16 and over =Employed/ Population 16 and +', 't12_1': 'Percentage of active population over population aged 16 and over= Active / Population 16 and +', 't13_1': 'Percentage of disability pensioner population over population aged 16 and over = Disability pensioners / Population 16 and +', 't14_1': 'Percentage of retirement pensioner population over population 16 and over=Retirement pensioners / Population 16 and +', 't15_1': 'Percentage of population in another situation of inactivity over population 16 and over=Population in another situation of inactivity / Population 16 and +', 't16_1' : 'Percentage of student population over population 16 and over = Students / Population 16 and +', 't17_1': 'Percentage of people with single marital status', 't17_2': 'Percentage of people with married marital status', 't17_3': 'Percentage of people with marital status widowed', 't17_4': 'Percentage of people for whom their marital status is not stated', 't17_5': 'Percentage of people with marital status legally separated or divorced', 't18_1': 'Total Homes', 't19_1': 'Main Homes', 't19_2': 'Non-main Homes', 't20_1': 'Owned Homes', 't20_2': 'Rental Homes', 't20_3' : 'Homes in another type of tenure regime', 't21_1': 'Total Households', 't22_1': 'Households with 1 person', 't22_2': 'Households with 2 people', 't22_3': 'Households with 3 people', 't22_4': 'Households of 4 people', 't22_5': 'Households of 5 or more people'}
#         g_df.rename(columns=column_names,inplace=True)
#         g_df.drop(columns=['ccaa','cpro'],inplace=True)
#
#         # Integrating data sources at municipal level to fill the missing information (1363 rows). This can be done since all the municipalities with missing values were found to have unique districts.
#         for x in censo_ingestion_urls:
#             data= fetch_data(censo_ingestion_urls[x]['url'])
#             data['Municipality code'] = data[censo_ingestion_urls[x]['by']].str[:5]
#             data = censo_ingestion_urls[x]['filter'](data)
#             data = data.pivot(index=['Municipality code'], columns=x, values='Total').reset_index()
#             for op_code, operations in censo_ingestion_urls[x]['columns'].items():
#                 operation_dict.get(op_code)(data,operations)
#
#         g_df['Year'] = '2021'
#         g_df.to_csv(filename,sep="\t", index=False)
#
#     else:
#         g_df = pd.read_csv(filename,sep="\t",dtype={0:str,1:str,2:str})
#     if municipality_code is not None:
#         if type(municipality_code) == str:
#             g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
#         elif type(municipality_code) == list:
#             g_df = g_df[g_df["Municipality code"].isin(municipality_code)]
#
#     if years != None:
#         g_df = g_df[g_df['Year'].isin(years)]
#
#     g_df["Country code"] = "ES"
#     g_df["Province code"] = g_df["Municipality code"].str[:2]
#
#     return ({
#         "Census tracts": g_df
#     })


def HouseholdsRentalPriceIndex(wd, municipality_code=None, years=None):

    path = "INE/HouseholdsRentalPriceIndex"
    path = path_creator(path, wd)
    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):
        r = request_with_retries("https://www.ine.es/jaxiT3/files/t/es/csv_bd/59061.csv?nocab=1", expect_csv=True)
        r.encoding = 'utf-8'
        df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", low_memory=False)
        df_ = df_[df_["Tipo de dato"]=="Índice"]
        df_ = df_.drop(columns=["Total Nacional", "Tipo de dato"])
        cols = df_.columns
        df_["Total"] = pd.to_numeric(df_["Total"].astype(str).str.replace('.', '').str.replace(',', '.'), errors="coerce")

        allcols = {
            "Distritos": "District code",
            "Periodo": "Year",
            "Total": "Household rental index"
        }
        df_ = df_.rename(columns={col: allcols[col] for col in cols})

        df_["Municipality code"] = df_["District code"].str[:5]
        df_["District code"] = df_["District code"].str[5:8]

        municipal = df_.groupby(["Municipality code", "Year"])[
            [col for col in df_.columns if
             col not in ["Municipality code", "District code", "Year"]]
        ].mean()
        municipal["District code"] = np.nan
        municipal = municipal.set_index("District code", append=True)
        municipal = municipal.reset_index()
        df_ = pd.concat([df_[municipal.columns], municipal])

        df_.to_csv(filename, index=False, sep="\t")
    else:
        df_ = pd.read_csv(filename, sep="\t",dtype={0:'str',1:'int',2:'str'})
    if municipality_code is not None:
        if type(municipality_code) == str:
            df_ = df_[(df_["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            df_ = df_[df_["Municipality code"].isin(municipality_code)]

    if years != None:
        df_ = df_[df_['Year'].isin(years)]

    df_["Country code"] = "ES"
    df_["Province code"] = df_["Municipality code"].str[:2]

    municipality = df_[-pd.isna(df_["Municipality code"]) & pd.isna(df_["District code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = df_[-pd.isna(df_["Municipality code"]) & -pd.isna(df_["District code"])]
    districts = districts[districts.columns[districts.notna().any()]]

    return ({
        "Municipality": municipality,
        "Districts": districts
    })


def ConsumerPriceIndex(wd, years=None):

    path = "INE/ConsumerPriceIndex"
    path = path_creator(path, wd)
    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):
        r = request_with_retries("https://www.ine.es/jaxiT3/files/t/es/csv_bd/23708.csv?nocab=1", expect_csv=True)
        r.encoding = 'utf-8'
        df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", low_memory=False)
        df_ = df_[df_["Tipo de dato"] == "Índice"]

        spanish_clases = list(df_["Clases"].unique())
        english_clases = ['General', '0111 Bread and cereals', '0112 Meat','0113 Fish and seafood', '0114 Milk, cheese and eggs',
        '0115 Oils and fats', '0116 Fruits', '0117 Pulses and vegetables', '0118 Sugar, jam, honey, chocolate and confectionery',
        '0119 Other food products', '0121 Coffee, tea and cocoa', '0122 Mineral waters, soft drinks, fruit and vegetable juices',
        '0211 Distilled beverages', '0212 Wine', '0213 Beer', '0220 Tobacco', '0312 Clothing',
        '0313 Other articles of clothing and haberdashery', '0314 Cleaning, repair and hire of clothing', '0321 Footwear',
        '0322 Repair and hire of footwear', '0411 Renting of main dwelling ', '0412 Other rentals',
        '0431 Materials for the maintenance and repair of the dwelling', '0432 Services for the maintenance and repair of the dwelling',
        '0441 Water supply', '0442 Refuse collection', '0443 Sewerage', '0444 Other services related to housing',
        '0451 Electricity', '0452 Gas', '0453 Liquid fuels', '0511 Furniture and furnishings', '0512 Carpets and other floor coverings',
        '0520 Household textiles', '0531 Major household appliances, electric or otherwise', '0532 Small household appliances',
        '0533 Repair of household appliances', '0540 Glassware, tableware and household utensils',
        '0551 Large tools and equipment', '0552 Small tools and accessories', '0561 Non-durable household goods',
        '0562 Domestic and other household services', '0611 Pharmaceutical products', '0612 Other medical products',
        '0613 Therapeutic appliances and equipment', '0621 Medical services', '0622 Dental services', '0623 Paramedical services',\
        '0630 Hospital services', '0711 Motor vehicles', '0712 Motorcycles', '0713 Bicycles',
        '0721 Spare parts and accessories for personal vehicles', '0722 Fuels and lubricants for personal vehicles',
        '0723 Maintenance and repair of personal motor vehicles', '0724 Other services relating to personal motor vehicles',
        '0731 Passenger transport by rail', '0732 Passenger transport by road', '0733 Passenger transport by air',
        '0734 Passenger transport by sea and inland waterways', '0735 Combined passenger transport',
        '0736 Other transport services', '0810 Postal services', '0820 Telephone and facsimile equipment',
        '0830 Telephone and facsimile services', '0911 Equipment for the reception, recording and reproduction of sound and images',
        '0912 Photographic and cinematographic equipment and optical instruments', '0913 Information processing equipment',
        '0914 Image, sound and data media', '0922 Musical instruments and major durables for indoor entertainment',
        '0931 Games, toys and hobbies', '0932 Equipment for sports, camping and outdoor recreation',
        '0933 Gardening, plants and flowers', '0934 Pets and related products', '0935 Veterinary and other services for domestic animals',
        '0941 Recreational and sporting services', '0942 Cultural services', '0951 Books', '0952 Press',
        '0954 Stationery and drawing materials', '0960 Package tours', '1010 Pre-primary and primary education',
        '1020 Secondary education', '1040 Higher education', '1050 Education not defined by level', '1111 Catering',
        '1112 Canteens', '1120 Accommodation services', '1211 Hairdressing and beauty parlours',
        '1212 Electrical appliances for personal care', '1213 Other appliances, articles and products for personal care',
        '1231 Jewellery, costume jewellery and watches', '1232 Other personal effects', '1240 Social protection',
        '1252 Insurance related to housing', '1253 Health-related insurance', '1254 Transport related insurance',
        '1255 Other insurance', '1262 Other financial services', '1270 Other services']
        df_["Clases"] = df_["Clases"].replace({k: v for k, v in zip(spanish_clases, english_clases)})
        df_ = df_.drop(columns=["Tipo de dato"])

        df_ = df_.rename(columns={
            "Periodo": "Year"
        })
        df_["Month"] = df_["Year"].str[5:8].astype(int)
        df_["Year"] = df_["Year"].str[:4].astype(int)
        df_["Total"] = pd.to_numeric(df_["Total"].astype(str).str.replace('.', '').str.replace(',', '.'),
                                     errors="coerce")
        df_["Country code"] = "ES"
        df_ = pd.pivot(df_,
                       index=["Country code","Year","Month"],
                       columns="Clases",
                       values="Total")
        df_.columns = [f'CPI 2015 base ~ Class:{col}' for col in df_.columns]
        df_ = df_.reset_index()

        df_.to_csv(filename, index=False, sep="\t")
    else:
        df_ = pd.read_csv(filename, sep="\t",dtype={0:'str',1:'int',2:'str'})
    if years != None:
        df_ = df_[df_['Year'].isin(years)]
    return ({
        "National": df_
    })

# =============================================================================
# Time Use Survey (Encuesta de Empleo del Tiempo, EET 2009-2010)
# =============================================================================
#
# The EET microdata are anonymised to the autonomous-community level, so they
# cannot be assigned to a census tract directly. The only variable that bridges
# the survey to the HouseholdIncomeDistributionAtlas is household income: the
# survey records a household monthly-net-income band (INGRESOSH), and the Atlas
# reports the average net household income per census tract. Time-use profiles
# are therefore computed per (autonomous community, income band) cell and each
# census tract is matched to the cell of its region and income band.
#
# The bands below are the ones respondents answered in, so the Atlas assigns them
# on income deflated to _EET_INCOME_REFERENCE_YEAR prices (see the "Household
# income group" column it publishes); a tract is otherwise pushed up a band by
# inflation alone. The survey also merges Ceuta and Melilla into one community,
# whose joint profile is published under both standard codes so that the tables
# join against the usual INE coding.

# Whole-Spain EET 2009-2010 microdata (fixed-width files inside the ZIP).
_EET_DATA_URL = "https://www.ine.es/ftp/microdatos/emptiem/datos_emptiem0910.zip"

# HETUS main activity groups: the first digit of the 3-digit APRIN activity code
# (the survey "Lista EET" classification) maps to one of ten broad groups.
_EET_ACTIVITY_GROUPS = {
    "0": "personal_care",
    "1": "paid_work",
    "2": "study",
    "3": "household_and_family_care",
    "4": "volunteer_work_and_meetings",
    "5": "social_life_and_entertainment",
    "6": "sports_and_outdoor",
    "7": "hobbies_and_computing",
    "8": "mass_media",
    "9": "travel_and_unspecified",
}
# Column order and nicely-presented headers for the activity shares.
_EET_ACTIVITY_ORDER = list(dict.fromkeys(_EET_ACTIVITY_GROUPS.values()))
_EET_ACTIVITY_LABELS = {
    "personal_care": "Personal care",
    "paid_work": "Paid work",
    "study": "Study",
    "household_and_family_care": "Household and family care",
    "volunteer_work_and_meetings": "Volunteer work and meetings",
    "social_life_and_entertainment": "Social life and entertainment",
    "sports_and_outdoor": "Sports and outdoor activities",
    "hobbies_and_computing": "Hobbies and computing",
    "mass_media": "Mass media",
    "travel_and_unspecified": "Travel and unspecified",
}

# The bands below are the ones the surveyed households answered in, so they are
# expressed in the euros of the survey fieldwork. Nominal incomes of any other
# year (the Atlas ones) must be deflated to this year before being bucketed.
_EET_INCOME_REFERENCE_YEAR = 2010

# Household monthly-net-income bands (INGRESOSH); band 5 (unknown) is not used.
_EET_INCOME_LABELS = {
    1: "1,200 € or less",
    2: "1,201 to 2,000 €",
    3: "2,001 to 3,000 €",
    4: "More than 3,000 €",
}

_EET_WEEKDAY_NAMES = {
    1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
    5: "Friday", 6: "Saturday", 7: "Sunday",
}

# Minimum number of surveyed persons in a (community, income band) cell before it
# is trusted; thinner cells fall back to the income-band national profile.
_EET_MIN_SUPPORT = 30


def _eet_income_band_from_monthly(monthly):
    """Assign a household monthly net income (€) to an INGRESOSH band (1-4)."""
    if pd.isna(monthly):
        return np.nan
    if monthly <= 1200:
        return 1
    if monthly <= 2000:
        return 2
    if monthly <= 3000:
        return 3
    return 4


def _eet_read_fwf(zf, name, colspecs, names):
    """Parse a fixed-width EET file straight from the open ZIP archive."""
    with zf.open(name) as fh:
        return pd.read_fwf(io.TextIOWrapper(fh, encoding="latin-1"),
                           colspecs=colspecs, names=names, dtype=str)


def _eet_weighted_activity_shares(df, group_keys):
    """Weighted activity-group share (%) per (group_keys, weekday, hour).

    Within each (group_keys, weekday, hour) the ten activity groups sum to 100.
    """
    keys = group_keys + ["Day of week number", "Hour", "activity"]
    grouped = df.groupby(keys, observed=True)["weight"].sum().reset_index()
    totals = grouped.groupby(group_keys + ["Day of week number", "Hour"],
                             observed=True)["weight"].transform("sum")
    grouped["share"] = grouped["weight"] / totals * 100.0
    wide = grouped.pivot_table(
        index=group_keys + ["Day of week number", "Hour"],
        columns="activity", values="share").reset_index()
    for col in _EET_ACTIVITY_ORDER:
        if col not in wide.columns:
            wide[col] = 0.0
    wide[_EET_ACTIVITY_ORDER] = wide[_EET_ACTIVITY_ORDER].fillna(0.0)
    return wide


def _eet_free_probability_and_support(df, group_keys, suffix):
    """Weighted free/holiday-day share (%) and sample size per ``group_keys``."""
    def _agg(g):
        w = g["weight"].sum()
        prob = (g["weight"] * g["free"]).sum() / w * 100.0 if w else np.nan
        return pd.Series({f"prob_{suffix}": prob, f"n_{suffix}": len(g)})
    return (df.groupby(group_keys, observed=True)
              .apply(_agg, include_groups=False)
              .reset_index())


def _build_time_use_profiles(wd):
    """Download the EET 2009-2010 microdata and build the two survey profile
    tables keyed by (autonomous community, income band):

    - weekly activity shares per weekday and hour, and
    - free/holiday-day probability per quarter and weekday.
    """
    print("Downloading the INE Time Use Survey (EET 2009-2010) microdata",
          file=sys.stdout)
    resp = request_with_retries(_EET_DATA_URL, headers={'User-Agent': 'Mozilla/5.0'})
    zf = zipfile.ZipFile(io.BytesIO(resp.content))

    # Household file: household id, autonomous community, income band.
    households = _eet_read_fwf(
        zf, "DHOGAR.TXT", [(0, 5), (5, 7), (17, 18)],
        ["IDHOGAR", "CAUT", "INGRESOSH"])
    households["band"] = pd.to_numeric(households["INGRESOSH"], errors="coerce")

    # Activity diary: 144 ten-minute records per person (starting at 06:00).
    diary = _eet_read_fwf(
        zf, "DIARIO2.TXT",
        [(0, 5), (5, 7), (7, 8), (8, 9), (9, 12), (12, 15), (28, 44)],
        ["IDHOGAR", "NPERS", "TRIM", "DDIASEM", "INTERVALO", "APRIN", "FACTORF"])
    diary["INTERVALO"] = diary["INTERVALO"].astype(int)
    diary["Day of week number"] = diary["DDIASEM"].astype(int)
    diary["weight"] = diary["FACTORF"].astype(float) / 1e10  # 6 int + 10 decimals
    # Clock hour: interval 1 is 06:00-06:10, the day runs 06:00 -> 06:00 next day.
    diary["Hour"] = ((360 + (diary["INTERVALO"] - 1) * 10) % 1440) // 60
    diary["activity"] = diary["APRIN"].str[:1].map(_EET_ACTIVITY_GROUPS).fillna(
        "travel_and_unspecified")
    diary = diary.merge(households[["IDHOGAR", "CAUT", "band"]], on="IDHOGAR",
                        how="left")

    # Complementary diary info: whether the diary day was a free/holiday day.
    diary1 = _eet_read_fwf(
        zf, "DIARIO1.TXT", [(0, 5), (5, 7), (14, 15)],
        ["IDHOGAR", "NPERS", "D_LIBRE"])

    valid = diary[diary["band"].isin([1, 2, 3, 4]) & diary["CAUT"].notna()].copy()
    cauts = sorted(valid["CAUT"].unique())

    # Number of surveyed persons per (community, band) cell -> fallback decisions.
    support = (valid.drop_duplicates(["IDHOGAR", "NPERS"])
                    .groupby(["CAUT", "band"]).size())

    # --- Weekly schedule: (community, band) profiles with band-level fallback ---
    prof_cb = dict(tuple(
        _eet_weighted_activity_shares(valid, ["CAUT", "band"]).groupby(["CAUT", "band"])))
    prof_b = dict(tuple(
        _eet_weighted_activity_shares(valid, ["band"]).groupby("band")))
    weekly_blocks = []
    for caut in cauts:
        for band in (1, 2, 3, 4):
            if support.get((caut, band), 0) >= _EET_MIN_SUPPORT and (caut, band) in prof_cb:
                block = prof_cb[(caut, band)].copy()
            else:
                block = prof_b[band].drop(columns="band").copy()
                block["CAUT"] = caut
                block["band"] = band
            weekly_blocks.append(block)
    weekly = pd.concat(weekly_blocks, ignore_index=True)

    # --- Free/holiday-day probability per (community, band, quarter, weekday) ---
    # One diary (one free/holiday flag) per person. The finest (community, band,
    # quarter, weekday) sub-cells are tiny, so each sub-cell falls back to the
    # income-band national pattern (then fully national) unless it holds at least
    # _EET_MIN_SUPPORT diaries of its own.
    persons = valid.drop_duplicates(["IDHOGAR", "NPERS"])[
        ["IDHOGAR", "NPERS", "TRIM", "Day of week number", "CAUT", "band", "weight"]]
    free = diary1.merge(persons, on=["IDHOGAR", "NPERS"], how="inner")
    free = free[free["D_LIBRE"].isin(["1", "6"])].copy()
    free["free"] = (free["D_LIBRE"] == "1").astype(int)
    keys = ["TRIM", "Day of week number"]
    p_cb = _eet_free_probability_and_support(free, ["CAUT", "band"] + keys, "cb")
    p_b = _eet_free_probability_and_support(free, ["band"] + keys, "band")
    p_nat = _eet_free_probability_and_support(free, keys, "national")
    grid = pd.MultiIndex.from_product(
        [cauts, [1, 2, 3, 4], ["1", "2", "3", "4"], [1, 2, 3, 4, 5, 6, 7]],
        names=["CAUT", "band"] + keys).to_frame(index=False)
    holiday = (grid.merge(p_cb, on=["CAUT", "band"] + keys, how="left")
                   .merge(p_b, on=["band"] + keys, how="left")
                   .merge(p_nat, on=keys, how="left"))
    holiday["free_day_probability"] = np.where(
        holiday["n_cb"].fillna(0) >= _EET_MIN_SUPPORT, holiday["prob_cb"],
        np.where(holiday["n_band"].fillna(0) >= _EET_MIN_SUPPORT,
                 holiday["prob_band"], holiday["prob_national"]))
    holiday = holiday[["CAUT", "band"] + keys + ["free_day_probability"]]

    return weekly, holiday


def _eet_duplicate_ceuta_into_melilla(df):
    """Publish the shared Ceuta+Melilla profile under Melilla's own community code.

    The EET microdata are anonymised with both cities merged into community ``18``,
    so no separate Melilla profile can be computed. Every other dataset here, and
    the INE relation table, code Melilla as ``19``; copying the ``18`` rows under
    that code keeps the survey tables joinable with the standard coding instead of
    leaving Melilla census tracts unmatched. Both codes therefore carry the same
    (joint) profile. No-op when the input already provides ``19``.
    """
    if df.empty or (df["CAUT"] == "19").any():
        return df
    melilla = df[df["CAUT"] == "18"].copy()
    if melilla.empty:
        return df
    melilla["CAUT"] = "19"
    return pd.concat([df, melilla], ignore_index=True)


def _eet_present(df):
    """Rename the internal keys/activity columns to nicely-presented English."""
    df = df.rename(columns={"CAUT": "Autonomous community code",
                            "band": "Household income group"})
    df = df.rename(columns={k: v for k, v in _EET_ACTIVITY_LABELS.items()
                            if k in df.columns})
    if "Day of week number" in df.columns:
        df.insert(df.columns.get_loc("Day of week number") + 1, "Day of week",
                  df["Day of week number"].map(_EET_WEEKDAY_NAMES))
    return df


def TimeUseSurvey(wd, municipality_code=None, reference_year=2010):
    """Weekly (hourly) and yearly-holiday (daily) time-use schedules per census tract.

    Builds, from the INE Time Use Survey (Encuesta de Empleo del Tiempo, EET
    2009-2010), a weekly activity schedule at hourly frequency and a yearly
    holiday schedule at daily frequency, and links them to every census tract in
    Spain through the ``HouseholdIncomeDistributionAtlas`` (2015 edition, the
    closest to the 2011 census the EET is calibrated against).

    Because the EET microdata are anonymised to the autonomous-community level,
    profiles are computed per (autonomous community, household income band) cell.
    Each census tract is matched to the cell of its region and of the income band
    its average net household income (Atlas 2015) falls into. Cells with fewer
    than 30 surveyed persons fall back to the income-band national profile.

    The survey anonymises Ceuta and Melilla as one community, so their joint
    profile is published under both standard codes (18 and 19). Census tracts keep
    the usual INE coding throughout, and the schedules can be joined onto any other
    dataset here without special-casing Melilla.

    Returns a dict with three tables (all columns in English):

    - ``"Census tracts"``: one row per census tract, with its autonomous community and
      household income group (the keys into the two schedule tables below).
    - ``"WeeklySchedule"``: for each (autonomous community, income group), the
      share (%) of the population in each of the ten HETUS activity groups, by
      day of week (1=Monday) and hour of day (0-23). The ten shares sum to 100
      within every (region, group, weekday, hour).
    - ``"HolidaySchedule"``: for each (autonomous community, income group) and
      every date of ``reference_year``, the estimated share (%) of the population
      on a free/holiday/vacation day (derived from the survey's D_LIBRE flag by
      quarter and weekday; the survey has no day-of-year calendar, so this is the
      daily-frequency approximation that is available).

    A tract's own schedules are obtained by merging ``"Census tracts"`` with either
    schedule table on ``["Autonomous community code", "Household income group"]``.

    Parameters
    ----------
    wd : str
        Working directory. The survey profiles are cached under
        ``{wd}/INE/TimeUseSurvey/`` on first use.
    municipality_code : str or list, optional
        Restrict ``"Census tracts"`` to these municipality code(s).
    reference_year : int, default 2010
        Calendar year the daily holiday schedule is expanded over.
    """
    path = path_creator("INE/TimeUseSurvey", wd)
    weekly_file = f"{path}/weekly_schedule.tsv"
    holiday_file = f"{path}/holiday_profile.tsv"

    if os.path.exists(weekly_file) and os.path.exists(holiday_file):
        # CAUT must stay a zero-padded string ("01", not 1): it is renamed to
        # "Autonomous community code" below and joined against the Atlas, whose
        # codes are strings, so a cached round-trip that drops the padding would
        # turn every such join into an empty result.
        weekly = pd.read_csv(weekly_file, sep="\t", dtype={"CAUT": str})
        holiday = pd.read_csv(holiday_file, sep="\t", dtype={"TRIM": str, "CAUT": str})
    else:
        weekly, holiday = _build_time_use_profiles(wd)
        weekly.to_csv(weekly_file, sep="\t", index=False)
        holiday.to_csv(holiday_file, sep="\t", index=False)

    # Applied after the cache is written, so the stored profiles stay a faithful
    # copy of what the microdata support and the duplication remains a presentation
    # step that can be revisited without rebuilding them.
    weekly = _eet_duplicate_ceuta_into_melilla(weekly)
    holiday = _eet_duplicate_ceuta_into_melilla(holiday)

    # --- Census tracts -> (autonomous community, income band) mapping ---
    atlas = HouseholdIncomeDistributionAtlas(wd=wd, years=[2015])["Census tracts"].copy()
    atlas["Census tract full code"] = (atlas["Municipality code"] + atlas["District code"]
                                       + atlas["Census tract code"])
    rel = RelationAutonomousCommunityAndProvince()
    # Census tracts keep the standard INE community coding, Melilla included: the
    # schedules above already publish the joint Ceuta+Melilla profile under both
    # 18 and 19, so no survey-specific recoding is needed here.
    prov2caut = dict(zip(rel["Province code"], rel["Autonomous community code"]))
    caut_name = dict(zip(rel["Autonomous community code"], rel["Autonomous community name"]))

    annual = pd.to_numeric(atlas["Average household net income"], errors="coerce")
    reference_income = pd.to_numeric(
        atlas[f"Average household net income ({_EET_INCOME_REFERENCE_YEAR} EUR)"], errors="coerce")
    sections = pd.DataFrame({
        "Municipality code": atlas["Municipality code"],
        "District code": atlas["District code"],
        "Census tract code": atlas["Census tract code"],
        "Census tract full code": atlas["Census tract full code"],
        "Autonomous community code": atlas["Municipality code"].str[:2].map(prov2caut),
        "Average net household income (annual, EUR)": annual,
        "Average net household income (monthly, EUR)": (annual / 12).round(2),
        f"Average net household income (monthly, {_EET_INCOME_REFERENCE_YEAR} EUR)":
            (reference_income / 12).round(2),
        # Taken from the Atlas, which already deflates each year's nominal income
        # to the euros the EET bands are expressed in, so both datasets bucket
        # identically and can be joined on this column.
        "Household income group": atlas["Household income group"],
        "Household income group label": atlas["Household income group label"],
    })
    sections["Autonomous community name"] = sections["Autonomous community code"].map(caut_name)
    sections = sections.dropna(subset=["Household income group", "Autonomous community code"])

    if municipality_code is not None:
        codes = [municipality_code] if isinstance(municipality_code, str) else municipality_code
        sections = sections[sections["Municipality code"].isin(codes)]

    # --- Expand the holiday profile over the reference-year calendar (daily) ---
    dates = pd.date_range(f"{reference_year}-01-01", f"{reference_year}-12-31", freq="D")
    calendar = pd.DataFrame({"Date": dates})
    calendar["Quarter"] = calendar["Date"].dt.quarter
    calendar["Day of week number"] = calendar["Date"].dt.weekday + 1
    calendar["TRIM"] = calendar["Quarter"].astype(str)
    holiday["TRIM"] = holiday["TRIM"].astype(str)
    holiday_schedule = holiday.merge(
        calendar, on=["TRIM", "Day of week number"], how="left")
    holiday_schedule["free_day_probability"] = holiday_schedule["free_day_probability"].round(2)
    holiday_schedule = holiday_schedule.rename(
        columns={"free_day_probability": "Free or holiday day probability (%)"})
    holiday_schedule = holiday_schedule.drop(columns=["TRIM"]).sort_values(
        ["CAUT", "band", "Date"]).reset_index(drop=True)
    holiday_schedule = holiday_schedule[
        ["CAUT", "band", "Date", "Quarter", "Day of week number",
         "Free or holiday day probability (%)"]]

    weekly = weekly.sort_values(["CAUT", "band", "Day of week number", "Hour"]).reset_index(drop=True)
    weekly[_EET_ACTIVITY_ORDER] = weekly[_EET_ACTIVITY_ORDER].round(2)
    
    # ---- WeeklyScheduleHouseholdOccupancy: probabilistic mapping from activity shares to occupancy state ----
    # User-editable probabilistic mapping from activity groups and hour-of-day to occupancy state percentages.
    activities_mapping = [
        {
            "occupancy_state": {"Sleeping": 100, "WithActivity": 0, "NonOccupied": 0},
            "activity_groups": ["personal_care"],
            "hour_ranges": [[22, 23], [0, 8]]
        },
        {
            "occupancy_state": {"Sleeping": 0, "WithActivity": 100, "NonOccupied": 0},
            "activity_groups": ["personal_care"],
            "hour_ranges": [[8, 21]]
        },
        {
            "occupancy_state": {"Sleeping": 0, "WithActivity": 100, "NonOccupied": 0},
            "activity_groups": ["household_and_family_care", "hobbies_and_computing", "mass_media"],
            "hour_ranges": [[0, 23]]
        },
        {
            "occupancy_state": {"Sleeping": 0, "WithActivity": 0, "NonOccupied": 100},
            "activity_groups": [
                "paid_work",
                "study",
                "volunteer_work_and_meetings",
                "social_life_and_entertainment",
                "sports_and_outdoor",
                "travel_and_unspecified"
            ],
            "hour_ranges": [[0, 23]]
        }
    ]
 
    # Compute occupancy state and state shares for each row based on activity shares and the probabilistic mapping.
    def get_state_probs(activity_key, hour):
        """Return the state probability dict for the given activity key and hour."""
        for mapping in activities_mapping:
            if activity_key in mapping["activity_groups"]:
                for start, end in mapping["hour_ranges"]:
                    if start <= hour <= end:
                        return mapping["occupancy_state"]
        # If no mapping found, return zero probabilities for all states (should not happen if mapping is complete)
        return {"Sleeping": 0.0, "WithActivity": 0.0, "NonOccupied": 0.0}
 
    # Initialize columns for occupancy label and state shares
    weekly["occupancy"] = None
    weekly["Sleeping_share"] = None
    weekly["WithActivity_share"] = None
    weekly["NonOccupied_share"] = None
 
    # Iterate over rows (it'sacceptable for moderate data size; we can also use apply)
    for idx, row in weekly.iterrows():
        state_shares = {"Sleeping": 0.0, "WithActivity": 0.0, "NonOccupied": 0.0}
        hour = row["Hour"]
        for act in _EET_ACTIVITY_ORDER:
            act_share = row[act]  # value between 0 and 100
            probs = get_state_probs(act, hour)
            for state, prob in probs.items():
                state_shares[state] += act_share * (prob / 100.0)
        # Determine the state with the highest share for the label
        weekly.at[idx, "occupancy"] = max(state_shares, key=state_shares.get)
        # Store the state shares (as percentages)
        weekly.at[idx, "Sleeping_share"] = state_shares["Sleeping"]
        weekly.at[idx, "WithActivity_share"] = state_shares["WithActivity"]
        weekly.at[idx, "NonOccupied_share"] = state_shares["NonOccupied"]
 
    # Round the share columns to 2 decimal places for consistency
    weekly["Sleeping_share"] = weekly["Sleeping_share"].round(2)
    weekly["WithActivity_share"] = weekly["WithActivity_share"].round(2)
    weekly["NonOccupied_share"] = weekly["NonOccupied_share"].round(2)
 
    # Compute hour of week: (Day of week number - 1) * 24 + Hour
    weekly['Hour of week'] = (weekly['Day of week number'] - 1) * 24 + weekly['Hour']
    
    # Prepare for pivot: we want to pivot on 'occupancy'
    pivot_df = weekly[["CAUT", "band", "Hour of week", "occupancy"]].copy()
    pivot_df = pivot_df.rename(columns={
        "CAUT": "Autonomous community code",
        "band": "Household income group"
    })
    
    # Pivot to wide format
    weekly_occupancy = pivot_df.pivot_table(
        index=['Autonomous community code', 'Household income group'],
        columns='Hour of week',
        values='occupancy',
        aggfunc='first'
    ).reset_index()
    
    # Ensure we have all hours from 0 to 167, in case any are missing (though they shouldn't be)
    expected_hours = list(range(168))
    # Get the current column names (the two id columns and the hour columns that exist)
    cols = list(weekly_occupancy.columns)
    # The first two are the id columns, the rest are the hour columns that exist (as integers)
    existing_hour_cols = [c for c in cols if isinstance(c, int) and 0 <= c < 168]
    missing_hour_cols = [h for h in expected_hours if h not in existing_hour_cols]
    # For missing hours, we add columns with NaN
    for h in missing_hour_cols:
        weekly_occupancy[h] = np.nan
    # Now reorder the columns: id columns then 0-167
    weekly_occupancy = weekly_occupancy[
        ['Autonomous community code', 'Household income group'] + expected_hours
    ]
 
    # Now, compute the three value DataFrames for Sleeping, WithActivity, NonOccupied
    # We'll create a function to avoid repetition
    def pivot_value_df(value_col):
        df = weekly[["CAUT", "band", "Hour of week", value_col]].copy()
        df = df.rename(columns={
            "CAUT": "Autonomous community code",
            "band": "Household income group"
        })
        wide = df.pivot_table(
            index=['Autonomous community code', 'Household income group'],
            columns='Hour of week',
            values=value_col,
            aggfunc='first'
        ).reset_index()
        # Ensure all hours 0-167 are present
        cols = list(wide.columns)
        existing_hour_cols = [c for c in cols if isinstance(c, int) and 0 <= c < 168]
        missing_hour_cols = [h for h in expected_hours if h not in existing_hour_cols]
        for h in missing_hour_cols:
            wide[h] = np.nan
        wide = wide[
            ['Autonomous community code', 'Household income group'] + expected_hours
        ]
        return wide
 
    sleeping_value_df = pivot_value_df("Sleeping_share")
    withactivity_value_df = pivot_value_df("WithActivity_share")
    nonoccupied_value_df = pivot_value_df("NonOccupied_share")
 
    return {
        "Census tracts": sections.reset_index(drop=True),
        "WeeklySchedule": _eet_present(weekly),
        "HolidaySchedule": _eet_present(holiday_schedule),
        "WeeklyScheduleHouseholdOccupancy": weekly_occupancy,
        "WeeklyScheduleHouseholdOccupancyValue": {
            "Sleeping": sleeping_value_df,
            "WithActivity": withactivity_value_df,
            "NonOccupied": nonoccupied_value_df
        }
    }



# =============================================================================
# Administrative boundaries (INE cartography)
# =============================================================================
#
# INE publishes the georeferenced boundaries of every census tract of the country,
# one national file per year, from its open data portal:
# https://www.ine.es/dyngs/DAB/index.htm?cid=1389
#
# Only census tracts are published. Districts, municipalities, provinces and
# autonomous communities are exact unions of tracts, so they are built here by
# dissolving them: every level then comes from the same source and nests inside
# the coarser ones without slivers or mismatched coastlines.
#
# The published files come in two shapes:
#
#   * 2011 onwards: one national shapefile in ETRS89 / UTM 30N (EPSG:25830) whose
#     attributes already carry the codes and the community, province and
#     municipality names (CUSEC, CUMUN, CDIS, CSEC, CPRO, CCA, NPRO, NCA, NMUN).
#   * 2001 to 2010: two shapefiles instead — peninsula plus Balearic islands in
#     ED50 / UTM 30N (EPSG:23030) and the Canary islands in WGS84 / UTM 28N
#     (EPSG:32628) — with the codes in PROVMUN, DISTRITO and SECCION and no names
#     at all, which are filled in from the library's own lookups.
#
# Both are normalised to the column names the rest of the library uses and
# reprojected to WGS84 (EPSG:4326), which is what a web map expects.
#
# Boundaries are redrawn every year: tracts are split as population grows and
# municipalities merge or change name, so the cartography of a year only matches
# the codes of data published for roughly that year. `AdministrativeBoundaries`
# therefore takes the year as an argument rather than picking one.

_INE_CARTOGRAPHY_PAGE = "https://www.ine.es/dyngs/DAB/index.htm?cid=1389"

# The five levels, finest first, keyed as the dataset functions key their results.
_BOUNDARY_LEVELS = ("Census tracts", "Districts", "Municipality", "Province", "Autonomous community")

# The columns that identify an area at each level, and so the columns a dataset is
# joined to its geometry by.
_BOUNDARY_LEVEL_KEYS = {
    "Census tracts": ["Municipality code", "District code", "Census tract code"],
    "Districts": ["Municipality code", "District code"],
    "Municipality": ["Municipality code"],
    "Province": ["Province code"],
    "Autonomous community": ["Autonomous community code"],
}

# Everything each level carries, coarser attributes included, so that a map of
# census tracts can still label them with their municipality and province.
_BOUNDARY_LEVEL_COLUMNS = {
    "Census tracts": ["Country code", "Autonomous community code", "Autonomous community name",
                      "Province code", "Province name", "Municipality code", "Municipality name",
                      "District code", "Census tract code"],
    "Districts": ["Country code", "Autonomous community code", "Autonomous community name",
                  "Province code", "Province name", "Municipality code", "Municipality name",
                  "District code"],
    "Municipality": ["Country code", "Autonomous community code", "Autonomous community name",
                     "Province code", "Province name", "Municipality code", "Municipality name"],
    "Province": ["Country code", "Autonomous community code", "Autonomous community name",
                 "Province code", "Province name"],
    "Autonomous community": ["Country code", "Autonomous community code", "Autonomous community name"],
}

# The cached file of each level. Spelled out rather than derived from the level
# name so that renaming a level never silently orphans a cache.
_BOUNDARY_LEVEL_FILES = {
    "Census tracts": "census_tracts",
    "Districts": "districts",
    "Municipality": "municipalities",
    "Province": "provinces",
    "Autonomous community": "autonomous_communities",
}

# What each level may be called when passed in, so that the keys of the dataset
# dictionaries and the obvious singulars and plurals all work.
_BOUNDARY_LEVEL_ALIASES = {
    "census tracts": "Census tracts", "census tract": "Census tracts", "sections": "Census tracts",
    "section": "Census tracts", "secciones": "Census tracts",
    "districts": "Districts", "district": "Districts", "distritos": "Districts",
    "municipality": "Municipality", "municipalities": "Municipality", "municipios": "Municipality",
    "province": "Province", "provinces": "Province", "provincias": "Province",
    "autonomous community": "Autonomous community", "autonomous communities": "Autonomous community",
    "ccaa": "Autonomous community", "comunidades autónomas": "Autonomous community",
}

_BOUNDARY_YEAR_URLS = None
_SHAPELY_CHECKED = False


def _require_geopandas():
    """Import geopandas, which the cartography needs and the rest of the library does not.

    Also checks that shapely can merge geometries at all: a shapely built against
    NumPy 1 (2.0.4 and earlier) fails on every vectorised operation once NumPy 2 is
    installed alongside it, with a ``ufunc 'create_collection' not supported`` deep
    inside a dissolve. Saying so here beats letting that surface from six frames down.
    """
    try:
        import geopandas as gpd
    except ImportError as error:
        raise ImportError(
            "Mapping needs geopandas, which social_ES does not install by default because none of "
            "the dataset functions require it. Install it with `pip install social_ES[geo]` or "
            "`pip install geopandas`."
        ) from error

    global _SHAPELY_CHECKED
    if not _SHAPELY_CHECKED:
        import shapely
        from shapely.geometry import Point
        try:
            shapely.union_all(np.array([Point(0, 0).buffer(1), Point(1, 1).buffer(1)], dtype=object))
        except TypeError as error:
            raise ImportError(
                f"shapely {shapely.__version__} cannot merge geometries under numpy "
                f"{np.__version__}: shapely 2.0.4 and earlier were built against numpy 1 and break "
                f"on every vectorised operation once numpy 2 is installed. Upgrade with "
                f"`pip install 'shapely>=2.0.6'`."
            ) from error
        _SHAPELY_CHECKED = True

    return gpd


def AvailableBoundaryYears():
    """The years INE publishes census tract cartography for, and the file of each.

    Scraped from INE's cartography page rather than hardcoded, so that a newly
    published year is picked up without touching the library. Returns a dict
    mapping the year to the URL of its shapefile, ordered by year.
    """
    global _BOUNDARY_YEAR_URLS

    if _BOUNDARY_YEAR_URLS is None:
        r = request_with_retries(_INE_CARTOGRAPHY_PAGE, headers={'User-Agent': 'Mozilla/5.0'})
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")

        urls = {}
        for option in soup.find_all("option"):
            value = (option.get("value") or "").strip()
            match = re.search(r"seccionado_(\d{4})\.zip$", value)
            if match:
                urls[int(match.group(1))] = value

        if not urls:
            raise RuntimeError(f"No cartography files found in {_INE_CARTOGRAPHY_PAGE}. "
                               f"The page layout may have changed.")

        _BOUNDARY_YEAR_URLS = dict(sorted(urls.items()))

    return dict(_BOUNDARY_YEAR_URLS)


def _resolve_boundary_year(year=None):
    """Return the published cartography year to use for `year`.

    An unpublished year falls back to the closest published one, preferring the
    earlier of two equally distant years, since a boundary revision applies from
    its year onwards.
    """
    available = AvailableBoundaryYears()

    if year is None:
        return max(available)

    year = int(year)
    if year in available:
        return year

    closest = min(available, key=lambda published: (abs(published - year), published))
    print(f"INE publishes no cartography for {year}; using {closest} instead", file=sys.stdout)

    return closest


def _resolve_boundary_level(level):
    """Return the canonical name of `level`, accepting the aliases users may pass."""
    if level in _BOUNDARY_LEVELS:
        return level

    canonical = _BOUNDARY_LEVEL_ALIASES.get(str(level).strip().lower())
    if canonical is None:
        raise ValueError(f"Unknown geographic level {level!r}. Use one of {list(_BOUNDARY_LEVELS)}.")

    return canonical


def _normalise_cartography(gdf):
    """Turn a shapefile INE publishes into the columns the rest of the library uses.

    Handles both layouts (see the section header) and leaves the geometry alone.
    """
    columns = set(gdf.columns)

    if "CUSEC" in columns:
        # 2011 onwards: the codes are already split into their own attributes.
        codes = pd.DataFrame({
            "Municipality code": gdf["CUMUN"].astype(str).str.strip().str.zfill(5),
            "District code": gdf["CDIS"].astype(str).str.strip().str.zfill(2),
            "Census tract code": gdf["CSEC"].astype(str).str.strip().str.zfill(3),
        })
        codes["Municipality name"] = (gdf["NMUN"].astype(str).str.strip()
                                      if "NMUN" in columns else np.nan)
    elif {"PROVMUN", "DISTRITO", "SECCION"} <= columns:
        # 2001 to 2010: the same codes under their Spanish names, and no names
        # anywhere in the file.
        codes = pd.DataFrame({
            "Municipality code": gdf["PROVMUN"].astype(str).str.strip().str.zfill(5),
            "District code": gdf["DISTRITO"].astype(str).str.strip().str.zfill(2),
            "Census tract code": gdf["SECCION"].astype(str).str.strip().str.zfill(3),
            "Municipality name": np.nan,
        })
    else:
        raise RuntimeError(f"Unrecognised INE cartography layout, with columns {sorted(columns)}. "
                           f"Expected either CUSEC or PROVMUN, DISTRITO and SECCION.")

    codes["Country code"] = "ES"
    codes["Province code"] = codes["Municipality code"].str[:2]

    relation = RelationAutonomousCommunityAndProvince()
    codes["Autonomous community code"] = codes["Province code"].map(
        dict(zip(relation["Province code"], relation["Autonomous community code"])))
    codes["Autonomous community name"] = codes["Province code"].map(
        dict(zip(relation["Province code"], relation["Autonomous community name"])))
    codes["Province name"] = codes["Province code"].map(
        dict(zip(relation["Province code"], relation["Province name"])))

    if codes["Municipality name"].isna().all():
        # Only the pre-2011 files, whose municipality names are taken from INE's
        # current dictionary; the handful of municipalities renamed since are
        # therefore labelled with their present name.
        names = MunicipalityNamesToMunicipalityCodes()
        codes["Municipality name"] = codes["Municipality code"].map(
            dict(zip(names["Municipality code"], names["Municipality name"])))

    codes["geometry"] = gdf.geometry.values

    return codes


def _dissolve_boundaries(gdf, level, gpd):
    """Merge the areas of `gdf` into the areas of `level`, keeping their attributes."""
    keys = _BOUNDARY_LEVEL_KEYS[level]
    columns = _BOUNDARY_LEVEL_COLUMNS[level]

    dissolved = gdf[columns + ["geometry"]].dissolve(by=keys, aggfunc="first", sort=True)
    dissolved = dissolved.reset_index()

    return gpd.GeoDataFrame(dissolved[columns + ["geometry"]], geometry="geometry", crs=gdf.crs)


def _build_boundaries(wd, year):
    """Download the cartography of `year` and cache one file per geographic level."""
    gpd = _require_geopandas()

    path = path_creator("INE/AdministrativeBoundaries", wd)
    url = AvailableBoundaryYears()[year]
    zip_filename = f"{path}/seccionado_{year}.zip"

    if not os.path.exists(zip_filename):
        print(f"Downloading the INE census tract cartography of {year} "
              f"(a ~60 MB file, downloaded once)", file=sys.stdout)
        r = request_with_retries(url, headers={'User-Agent': 'Mozilla/5.0'})
        # Written through a temporary name so that an interrupted download is never
        # left behind looking like a complete cache.
        with open(f"{zip_filename}.part", "wb") as file:
            file.write(r.content)
        os.replace(f"{zip_filename}.part", zip_filename)

    shapefiles = [name for name in zipfile.ZipFile(zip_filename).namelist()
                  if name.lower().endswith(".shp")]
    if not shapefiles:
        raise RuntimeError(f"No shapefile inside {zip_filename}")

    print(f"Building the {year} boundaries of every geographic level", file=sys.stdout)

    # More than one shapefile means the year splits the country in pieces, each in
    # the UTM zone of its own, so each is reprojected before they are put together.
    pieces = []
    for shapefile in shapefiles:
        piece = gpd.read_file(f"/vsizip/{os.path.abspath(zip_filename)}/{shapefile}")
        pieces.append(piece.to_crs("EPSG:4326"))

    tracts = gpd.GeoDataFrame(pd.concat([_normalise_cartography(piece) for piece in pieces],
                                        ignore_index=True),
                              geometry="geometry", crs="EPSG:4326")

    # Self-intersections in the published polygons would propagate into every
    # dissolved level, so they are repaired once, here.
    invalid = ~tracts.geometry.is_valid
    if invalid.any():
        tracts.loc[invalid, "geometry"] = tracts.loc[invalid, "geometry"].make_valid()

    tracts = tracts[_BOUNDARY_LEVEL_COLUMNS["Census tracts"] + ["geometry"]]
    tracts = tracts.sort_values(_BOUNDARY_LEVEL_KEYS["Census tracts"]).reset_index(drop=True)
    tracts.to_parquet(f"{path}/{_BOUNDARY_LEVEL_FILES['Census tracts']}_{year}.parquet", index=False)

    # Each level is dissolved from the previous one rather than from the tracts:
    # the result is the same and the geometry count falls at every step.
    coarser = tracts
    for level in _BOUNDARY_LEVELS[1:]:
        coarser = _dissolve_boundaries(coarser, level, gpd)
        coarser.to_parquet(f"{path}/{_BOUNDARY_LEVEL_FILES[level]}_{year}.parquet", index=False)


def AdministrativeBoundaries(wd, year=None, level="Census tracts", municipality_code=None,
                             province_code=None, autonomous_community_code=None):
    """Spanish administrative boundaries, as published by INE.

    Returns a ``geopandas.GeoDataFrame`` in WGS84 (EPSG:4326) with one row per area
    and the same code and name columns the dataset functions use, so that any of
    them joins straight onto it.

    Only the census tract file is published by INE
    (https://www.ine.es/dyngs/DAB/index.htm?cid=1389); the coarser levels are
    dissolved from it here, and cached alongside it.

    Boundaries change from year to year — tracts are split as population grows,
    municipalities merge — so `year` should be the year of the data being mapped.
    A year INE does not publish falls back to the closest one it does.

    Needs geopandas, which social_ES does not install by default: `pip install
    social_ES[geo]`.

    Parameters
    ----------
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
    """
    gpd = _require_geopandas()

    level = _resolve_boundary_level(level)
    year = _resolve_boundary_year(year)

    path = path_creator("INE/AdministrativeBoundaries", wd)
    filename = f"{path}/{_BOUNDARY_LEVEL_FILES[level]}_{year}.parquet"

    if not os.path.exists(filename):
        _build_boundaries(wd, year)

    gdf = gpd.read_parquet(filename)

    for column, codes in (("Municipality code", municipality_code),
                          ("Province code", province_code),
                          ("Autonomous community code", autonomous_community_code)):
        if codes is None or column not in gdf.columns:
            continue
        codes = [codes] if isinstance(codes, str) else list(codes)
        gdf = gdf[gdf[column].isin(codes)]

    return gdf.reset_index(drop=True)


# =============================================================================
# Vector tiles (PMTiles)
# =============================================================================
#
# A page that carries its geometry can only carry so much: the 36,333 census tracts
# of the country are close to seven million vertices, and coarsening them enough to
# fit would flatten tracts whose median extent is 822 m. Vector tiles cut the
# geometry into pieces the browser fetches as it needs them, so what a page holds
# stops depending on how much of the country it covers.
#
# The archive is built per level and year, over the whole country, and cached beside
# the boundaries it comes from — so every map of that level and year reuses it,
# whether it draws a city or all of Spain. The values stay in the page and are joined
# to the tiles by the area code each feature carries.
#
# The cost is that tiles have to be fetched, and a page opened from a file:// URL is
# not allowed to fetch anything — so a tiled map has to be served. `ServeMaps` does
# that; without it the page says so rather than drawing an empty map.

_PMTILES_EXTENT = 4096       # the integer grid each tile's coordinates are written on
_PMTILES_BUFFER = 16         # grid units kept past the edge, so borders meet across tiles
_PMTILES_MIN_ZOOM = 5
_PMTILES_MAX_ZOOM = 12       # a tile unit is ~2 m here, finer than the boundaries are drawn


def _require_pmtiles():
    """Import the tile writers, which only the tiled maps need."""
    try:
        from mapbox_vector_tile import encode
        from pmtiles.writer import Writer
        from pmtiles.tile import zxy_to_tileid, TileType, Compression
    except ImportError as error:
        raise ImportError(
            "Building vector tiles needs the `pmtiles` and `mapbox-vector-tile` packages, which "
            "social_ES does not install by default. Install them with `pip install social_ES[geo]` "
            "or `pip install pmtiles mapbox-vector-tile`."
        ) from error
    return encode, Writer, zxy_to_tileid, TileType, Compression


def _tile_bounds(zoom, x, y):
    """The longitude and latitude bounds of a slippy-map tile."""
    n = 2.0 ** zoom
    return (x / n * 360.0 - 180.0,
            math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))),
            (x + 1) / n * 360.0 - 180.0,
            math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n)))))


def _tile_range(bounds, zoom):
    """The tiles of `zoom` that cover a longitude and latitude box."""
    n = 2 ** zoom

    def column(longitude):
        return min(n - 1, max(0, int((longitude + 180.0) / 360.0 * n)))

    def row(latitude):
        latitude = max(-85.05112878, min(85.05112878, latitude))
        radians = math.radians(latitude)
        return min(n - 1, max(0, int((1 - math.log(math.tan(radians) + 1 / math.cos(radians))
                                      / math.pi) / 2 * n)))

    return column(bounds[0]), column(bounds[2]), row(bounds[3]), row(bounds[1])


def _build_boundary_tiles(gdf, filename, key_columns,
                          min_zoom=_PMTILES_MIN_ZOOM, max_zoom=_PMTILES_MAX_ZOOM):
    """Write the geometry of `gdf` to a PMTiles archive, one layer of areas.

    Each feature carries only its area code: everything else a map says about an area
    lives in the page, which is what lets one archive serve every map of its level.
    """
    encode, Writer, zxy_to_tileid, TileType, Compression = _require_pmtiles()
    import shapely
    from shapely import STRtree
    from shapely.geometry import box

    geometries = gdf.geometry.values
    codes = ["".join(row) for row in gdf[key_columns].to_numpy()]
    bounds = tuple(float(value) for value in gdf.total_bounds)

    tiles = {}
    for zoom in range(min_zoom, max_zoom + 1):
        # Simplified once per zoom, to what a tile unit can hold, rather than once per
        # tile: the same polygon lands in many tiles and the work would be repeated.
        width = 360.0 / (2 ** zoom)
        simplified = shapely.simplify(geometries, width / _PMTILES_EXTENT, preserve_topology=True)
        tree = STRtree(simplified)

        first_column, last_column, first_row, last_row = _tile_range(bounds, zoom)
        for x in range(first_column, last_column + 1):
            for y in range(first_row, last_row + 1):
                minx, miny, maxx, maxy = _tile_bounds(zoom, x, y)
                pad_x = (maxx - minx) * _PMTILES_BUFFER / _PMTILES_EXTENT
                pad_y = (maxy - miny) * _PMTILES_BUFFER / _PMTILES_EXTENT
                clip = box(minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y)

                hits = tree.query(clip)
                if len(hits) == 0:
                    continue

                features = []
                for index in hits:
                    piece = shapely.intersection(simplified[index], clip)
                    if not piece.is_empty:
                        features.append({"geometry": piece, "properties": {"c": codes[index]}})
                if not features:
                    continue

                data = encode({"name": "areas", "features": features},
                              default_options={"quantize_bounds": (minx - pad_x, miny - pad_y,
                                                                   maxx + pad_x, maxy + pad_y),
                                               "extents": _PMTILES_EXTENT,
                                               "y_coord_down": False,
                                               "on_invalid_geometry": None})
                if data:
                    # Stored compressed, which the header declares and the reader
                    # passes straight to the browser as gzipped content.
                    tiles[zxy_to_tileid(zoom, x, y)] = gzip.compress(data, 6)

        print(f"  zoom {zoom}: {len(tiles):,} tiles so far", file=sys.stdout)

    # Written through a temporary name, so an interrupted build is never left behind
    # looking like a complete archive.
    with open(f"{filename}.part", "wb") as handle:
        writer = Writer(handle)
        for tileid in sorted(tiles):
            writer.write_tile(tileid, tiles[tileid])
        writer.finalize(
            {"tile_type": TileType.MVT, "tile_compression": Compression.GZIP,
             "min_zoom": min_zoom, "max_zoom": max_zoom,
             "min_lon_e7": int(bounds[0] * 1e7), "min_lat_e7": int(bounds[1] * 1e7),
             "max_lon_e7": int(bounds[2] * 1e7), "max_lat_e7": int(bounds[3] * 1e7),
             "center_zoom": min_zoom,
             "center_lon_e7": int((bounds[0] + bounds[2]) / 2 * 1e7),
             "center_lat_e7": int((bounds[1] + bounds[3]) / 2 * 1e7)},
            {"attribution": "INE", "vector_layers": [{"id": "areas", "fields": {"c": "String"}}]})
    os.replace(f"{filename}.part", filename)

    return len(tiles)


def BoundaryTiles(wd, year=None, level="Census tracts"):
    """The PMTiles archive of a geographic level, built once and cached.

    Returns the path of an archive holding the boundaries of every area of `level` in
    the country, as vector tiles. It covers the whole country whatever the map that
    asked for it draws, so that one archive serves every map of that level and year —
    which is the point of building it, since building it is slow.

    A page reads it over HTTP; see `ServeMaps`.

    Parameters
    ----------
    wd : str
        Working directory the cartography is cached under.
    year : int, optional
        Year of the boundaries. Defaults to the most recent one INE publishes.
    level : str, default "Census tracts"
        One of the five levels `AdministrativeBoundaries` returns.
    """
    level = _resolve_boundary_level(level)
    year = _resolve_boundary_year(year)

    path = path_creator("INE/AdministrativeBoundaries", wd)
    filename = f"{path}/{_BOUNDARY_LEVEL_FILES[level]}_{year}.pmtiles"

    if not os.path.exists(filename):
        gdf = AdministrativeBoundaries(wd=wd, year=year, level=level)
        print(f"Building the vector tiles of the {year} {level.lower()} "
              f"({len(gdf):,} areas, built once and reused by every map of them)", file=sys.stdout)
        started = time.time()
        count = _build_boundary_tiles(gdf, filename, _BOUNDARY_LEVEL_KEYS[level])
        print(f"{count:,} tiles, {os.path.getsize(filename) / 1e6:.1f} MB, "
              f"{time.time() - started:.0f}s", file=sys.stdout)

    return filename


def ServeMaps(wd, port=8000, directory=None):
    """Serve the written maps over HTTP, which a tiled map needs to read its tiles.

    A page opened from a `file://` URL cannot fetch anything, tiles included, so a map
    written with ``tiles=True`` has to be served. This serves ``{wd}/INE`` on
    localhost and returns the running server; call ``shutdown()`` on it when done, or
    leave it running for the session.

    >>> server = INE.ServeMaps(wd)          # doctest: +SKIP
    >>> # open the printed URL, then, when finished:
    >>> server.shutdown()                   # doctest: +SKIP

    Parameters
    ----------
    wd : str
        The working directory the maps were written under.
    port : int, default 8000
        Port to listen on. Pass 0 to let the system choose a free one.
    directory : str, optional
        Directory to serve. Defaults to ``{wd}/INE``.
    """
    import functools
    import threading
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    root = os.path.abspath(directory if directory is not None else f"{wd}/INE")
    archives = {}

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            # /tiles/<archive>/<z>/<x>/<y>.pbf reads one tile out of the PMTiles
            # archive, so that the whole level stays the single cached file it was
            # built as instead of tens of thousands of little ones on disk.
            match = re.match(r"^/tiles/([\w.-]+)/(\d+)/(\d+)/(\d+)\.pbf$", self.path)
            if not match:
                return SimpleHTTPRequestHandler.do_GET(self)

            name, zoom, x, y = match.group(1), *(int(one) for one in match.groups()[1:])
            if name not in archives:
                from pmtiles.reader import Reader, MmapSource
                handle = open(f"{root}/AdministrativeBoundaries/{name}", "rb")
                archives[name] = (handle, Reader(MmapSource(handle)))

            try:
                tile = archives[name][1].get(zoom, x, y)
            except Exception:
                tile = None

            if tile is None:
                self.send_response(204)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.mapbox-vector-tile")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(tile)))
            # An archive is rebuilt only by deleting it, so its tiles never change
            # under a page. Saying so keeps changing the variable from fetching the
            # whole view again: redrawing reads the browser's cache instead.
            self.send_header("Cache-Control", "public, max-age=86400, immutable")
            self.end_headers()
            self.wfile.write(tile)

    server = HTTPServer(("127.0.0.1", port), functools.partial(QuietHandler, directory=root))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    address = f"http://127.0.0.1:{server.server_port}"
    print(f"Serving {root} at {address}", file=sys.stdout)
    print(f"  maps are under {address}/Maps/", file=sys.stdout)

    return server


# =============================================================================
# Mapping a variable to an HTML choropleth
# =============================================================================
#
# `MapVariable` takes what any of the dataset functions returns, one of its
# variables, and writes a standalone HTML map of it.
#
# The colours are the ones the data-visualisation method prescribes: a single-hue
# blue ramp for magnitude, a blue-to-red pair around a midpoint for polarity, and
# the fixed categorical order for classes. Both light and dark modes are styled,
# but only the page chrome changes with the mode: the polygons and the basemap
# stay light in both, because flipping a sequential ramp for dark mode would
# reverse what "low" looks like, and the ramp is what carries the magnitude.

# Sequential ramp, steps 100 (lightest) to 700 (darkest).
_MAP_SEQUENTIAL_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
                        "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]

# The warm arm of the diverging pair: the same lightness steps as the ramp above,
# in red, so that a value and its mirror image read as equally far from the middle.
_MAP_DIVERGING_WARM_RAMP = ["#fed4d0", "#f9c0ba", "#f7aba4", "#f1968e", "#ed7f77", "#e66962",
                            "#e14c49", "#d03b3b", "#ba3333", "#a62729", "#902122", "#7d171a",
                            "#671214"]

# The neutral midpoint of the diverging pair, used only when the bins are odd and
# one of them straddles the centre.
_MAP_NEUTRAL = "#f0efec"

# Where the ramps start. A chart draws a sequential ramp on its own surface, and
# lets the lightest step recede into it; a choropleth draws it over a basemap,
# where a class that recedes is a class nobody can read — step 100 sits at a
# contrast of 1.00 against the grey the areas with no data are painted with, which
# is to say the two are the same shade. So the ramps start at the step the method
# floors an ordinal scale at (250, the lightest that still clears 2:1 against a
# light surface) and run to the darkest.
_MAP_RAMP_FLOOR = 3

# The categorical order. Only the first three clear the colour-blindness floors
# when every pair can end up side by side, which is what a map does, so classes
# past the third lean on the legend and the tooltip to be told apart.
_MAP_CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7",
                    "#e34948"]

_MAP_NO_DATA_COLOR = "#e1e0d9"

# How many digits each code is written with, so that codes that went through a
# float column, or lost their leading zero, still join.
_MAP_CODE_WIDTHS = {"Municipality code": 5, "District code": 2, "Census tract code": 3,
                    "Province code": 2, "Autonomous community code": 2}

# The argument of `AdministrativeBoundaries` that restricts it to the areas the
# data covers, so that a map of one city never loads the boundaries of the country.
_MAP_BOUNDARY_FILTERS = {"Municipality code": "municipality_code",
                         "Province code": "province_code",
                         "Autonomous community code": "autonomous_community_code"}


def _sample_ramp(ramp, n):
    """Take `n` colours spread evenly across `ramp`, ends included."""
    if n <= 1:
        return [ramp[len(ramp) // 2]]
    return [ramp[round(i * (len(ramp) - 1) / (n - 1))] for i in range(n)]


def _map_colors(n, palette):
    """The colours of `n` classes under `palette`."""
    if palette == "sequential":
        return _sample_ramp(_MAP_SEQUENTIAL_RAMP[_MAP_RAMP_FLOOR:], n)

    if palette == "diverging":
        arm = n // 2
        cool = _sample_ramp(_MAP_SEQUENTIAL_RAMP[_MAP_RAMP_FLOOR:], arm)[::-1]
        warm = _sample_ramp(_MAP_DIVERGING_WARM_RAMP[_MAP_RAMP_FLOOR:], arm)
        return cool + ([_MAP_NEUTRAL] if n % 2 else []) + warm

    if palette == "categorical":
        if n > len(_MAP_CATEGORICAL):
            raise ValueError(f"A categorical map holds at most {len(_MAP_CATEGORICAL)} classes, "
                             f"not {n}.")
        return _MAP_CATEGORICAL[:n]

    raise ValueError(f"Unknown palette {palette!r}. Use 'sequential', 'diverging' or 'categorical'.")


def _map_bin_edges(values, classification, bins, palette, center):
    """The class boundaries of a numeric variable.

    Ties collapse: a quantile classification of a variable where half the areas
    share a value returns fewer bins than asked rather than empty ones.
    """
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        raise ValueError("The variable holds no finite value to map.")

    if isinstance(classification, (list, tuple, np.ndarray)):
        edges = np.asarray(sorted(float(edge) for edge in classification), dtype=float)

    elif palette == "diverging":
        # Both arms are cut the same way and mirrored around the centre, so that
        # the colour of a value depends on how far from the centre it is and on
        # which side, and not on how the two sides happen to be populated.
        center = 0.0 if center is None else float(center)
        deviation = np.abs(finite - center)
        arm_bins = max(1, bins // 2)
        if classification == "quantiles":
            arm = np.unique(np.quantile(deviation, np.linspace(0, 1, arm_bins + 1))[1:])
        elif classification == "equal_interval":
            spread = float(deviation.max()) or 1.0
            arm = np.linspace(0, spread, arm_bins + 1)[1:]
        else:
            raise ValueError(f"Unknown classification {classification!r}.")
        edges = np.concatenate([center - arm[::-1], [center], center + arm])

        # Mirroring puts the outermost edges as far from the centre as the furthest
        # value is, on both sides, so one of them always overshoots the data — and a
        # legend reading "-46.8 – 5.6" for a percentage is a legend nobody believes.
        # Pulling the two ends back onto the data moves no value into another class.
        edges[0] = min(edges[1], max(edges[0], float(finite.min())))
        edges[-1] = max(edges[-2], min(edges[-1], float(finite.max())))

    elif classification == "quantiles":
        edges = np.quantile(finite, np.linspace(0, 1, bins + 1))

    elif classification == "equal_interval":
        edges = np.linspace(float(finite.min()), float(finite.max()), bins + 1)

    else:
        raise ValueError(f"Unknown classification {classification!r}. Use 'quantiles', "
                         f"'equal_interval', or a list of class boundaries.")

    edges = np.unique(edges)
    if edges.size < 2:
        edges = np.array([edges[0], edges[0] + 1.0])

    return edges


def _map_decimals(edges):
    """How many decimals the legend and the tooltips of these classes need."""
    step = float(np.min(np.diff(edges)))
    if step >= 10:
        return 0
    if step >= 1:
        return 1
    if step >= 0.01:
        return 2
    return 4


def _format_map_number(value, decimals):
    if value is None or not np.isfinite(value):
        return "no data"
    return f"{value:,.{decimals}f}"


def _map_dataframe_and_level(data, level):
    """Pull the DataFrame to map out of what a dataset function returned.

    `data` may be the whole dictionary, in which case `level` selects the table
    (and, if it is not given, the finest table the dictionary holds), or a single
    DataFrame, whose level is then read off the code columns it carries.
    """
    if isinstance(data, dict):
        keyed = {}
        for key, table in data.items():
            if not isinstance(table, pd.DataFrame):
                continue
            try:
                keyed[_resolve_boundary_level(key)] = (key, table)
            except ValueError:
                continue  # a table of something other than a geographic level

        if not keyed:
            raise ValueError(f"None of the tables {list(data)} is one of a geographic level. Pass "
                             f"the DataFrame to map instead of the whole dictionary.")

        if level is None:
            level = next(candidate for candidate in _BOUNDARY_LEVELS if candidate in keyed)
        else:
            level = _resolve_boundary_level(level)
            if level not in keyed:
                raise ValueError(f"No {level!r} table in this dataset; it holds "
                                 f"{[key for key, _ in keyed.values()]}.")

        return keyed[level][1], level

    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"`data` must be a DataFrame or the dictionary a dataset function returns, "
                        f"not {type(data).__name__}.")

    if level is not None:
        return data, _resolve_boundary_level(level)

    # Finest first: the level of a table is the finest code it fills in.
    for candidate in _BOUNDARY_LEVELS:
        column = _BOUNDARY_LEVEL_KEYS[candidate][-1]
        if column in data.columns and data[column].notna().any():
            return data, candidate

    raise ValueError(f"Could not tell which geographic level this table is at: it carries none of "
                     f"{[keys[-1] for keys in _BOUNDARY_LEVEL_KEYS.values()]}. Pass `level`.")


def _normalise_code(series, width):
    """Zero-pad a code column, undoing a trip through a float column if it took one."""
    return (series.astype(str).str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(width))


# How much geometry a page carries before it is worth coarsening. A vertex costs
# about six bytes gzipped and a third more again once base64'd into the file, so
# this budget is roughly 4.5 MB of geometry.
_MAP_VERTEX_BUDGET = 500_000

# The finest tolerance ever applied. A metre is a pixel at zoom 17, which is as far
# in as a census tract boundary means anything, and it is finer than the boundaries
# were surveyed — but it still drops around half the vertices, which the published
# files spend on detail nobody can see.
_MAP_MIN_TOLERANCE = 1.0

# The coarsest tolerance worth applying, as a fraction of the size of the areas being
# drawn. Simplification is a lie about a boundary, and the lie has to stay small
# against the thing it is told about: at a fiftieth of an area's own extent it is
# invisible, and somewhere past a tenth the area stops being a shape and becomes a
# blob. Nothing is drawn past this — the budget gives way instead.
_MAP_MAX_TOLERANCE_FRACTION = 0.02


def _default_simplify_tolerance(gdf):
    """A simplification tolerance, in metres, for how much geometry there is to draw.

    Detail is worth keeping and only costs what it costs, so the tolerance follows
    the size of the geometry rather than the extent it covers: a city fits inside the
    budget and is drawn as INE published it, and only what overruns is coarsened, by
    as much as the overrun demands. The extent is no guide — the nineteen autonomous
    communities span the country and are one coastline, while the census tracts of a
    city span a few kilometres and are thousands of separate rings.

    Simplifying is slow on a national file, so the tolerance is estimated rather than
    searched for. Across the published cartography the vertices that survive fall as
    roughly the inverse square root of the tolerance, which inverts to the square
    below; the constant is fitted to the 2021 municipalities (4.0 M vertices whole,
    1.0 M at 20 m, 0.73 M at 40 m).

    Raises when the budget cannot be met without coarsening the areas past
    recognition, rather than returning a tolerance that would flatten them: the
    caller is told to draw fewer of them, or to choose the tolerance itself.
    """
    import shapely

    vertices = int(shapely.get_num_coordinates(gdf.geometry.values).sum())
    if vertices <= _MAP_VERTEX_BUDGET:
        return _MAP_MIN_TOLERANCE

    tolerance = min(500.0, 1.2 * (vertices / _MAP_VERTEX_BUDGET) ** 2)

    # How big the areas being drawn are, so the tolerance can be judged against them.
    bounds = gdf.geometry.bounds
    extent = float(np.median(np.maximum(
        (bounds["maxx"] - bounds["minx"]) * 111320 * 0.77,
        (bounds["maxy"] - bounds["miny"]) * 111320)))
    largest = extent * _MAP_MAX_TOLERANCE_FRACTION

    if tolerance > largest:
        raise ValueError(
            f"{len(gdf):,} areas hold {vertices:,} vertices, and fitting them into one page would "
            f"take a tolerance of {tolerance:.0f} m — against areas whose median extent is only "
            f"{extent:.0f} m, which would flatten them into blobs. Map a region rather than the "
            f"whole country, use a coarser level, or pass `simplify_tolerance` to choose the loss "
            f"deliberately ({largest:.0f} m is the most these areas take)."
        )

    return max(_MAP_MIN_TOLERANCE, tolerance)


def _round_geometry(geometry, ndigits):
    """The GeoJSON geometry of a shape, with its coordinates rounded.

    Six decimals is 11 cm on the ground — finer than the boundaries are surveyed,
    and finer than a pixel at any zoom a browser offers — while dropping the
    centimetres of false precision the published files carry.
    """
    from shapely.geometry import mapping

    def round_coordinates(item):
        if isinstance(item, (list, tuple)):
            if item and isinstance(item[0], (int, float)):
                return [round(float(value), ndigits) for value in item[:2]]
            return [round_coordinates(part) for part in item]
        return item

    mapped = mapping(geometry)

    if mapped["type"] == "GeometryCollection":
        return {"type": "GeometryCollection",
                "geometries": [{"type": part["type"],
                                "coordinates": round_coordinates(part["coordinates"])}
                               for part in mapped["geometries"]]}

    return {"type": mapped["type"], "coordinates": round_coordinates(mapped["coordinates"])}




# The columns that say which area a row is, rather than something about it, and so
# are never offered as a variable to map.
_MAP_NON_VARIABLE_COLUMNS = {"Country code", "Year", "Quarter",
                             "Autonomous community code", "Autonomous community name",
                             "Province code", "Province name",
                             "Municipality code", "Municipality name",
                             "District code", "Census tract code"}

# Past this many distinct values a text column is an identifier rather than a
# classification, and mapping it would draw one class and a large "Other".
_MAP_MAX_CATEGORIES_OFFERED = 50

# The payload size, in bytes, past which the page is written compressed rather than
# as plain JSON. Below it the base64 saves too little to be worth a file that cannot
# be read in an editor.
_MAP_GZIP_THRESHOLD = 200_000


_MAP_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__PAGE_TITLE__</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  color-scheme: light;
  --surface-1: #fcfcfb;
  --plane: #f9f9f7;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #898781;
  --hairline: #e1e0d9;
  --border: rgba(11, 11, 11, 0.10);
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --plane: #0d0d0d;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #898781;
    --hairline: #2c2c2a;
    --border: rgba(255, 255, 255, 0.10);
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface-1: #1a1a19;
  --plane: #0d0d0d;
  --text-primary: #ffffff;
  --text-secondary: #c3c2b7;
  --text-muted: #898781;
  --hairline: #2c2c2a;
  --border: rgba(255, 255, 255, 0.10);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--plane);
  color: var(--text-primary);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
}
.viz-root { max-width: 1400px; margin: 0 auto; padding: 24px 20px 40px; }
h1 { font-size: 21px; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.01em; }
.sub { margin: 0 0 16px; color: var(--text-secondary); font-size: 13px; }
.controls { display: flex; align-items: center; gap: 10px; margin: 0 0 12px; flex-wrap: wrap; }
.controls label { font-size: 12px; color: var(--text-muted); }
.controls select {
  font: inherit; font-size: 13px; max-width: min(100%, 640px);
  padding: 6px 10px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface-1); color: var(--text-primary);
}
.map-wrap {
  position: relative;
  height: min(68vh, 720px);
  min-height: 380px;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  background: var(--surface-1);
}
#map { position: absolute; inset: 0; }
.panel {
  position: absolute;
  z-index: 500;
  background: var(--surface-1);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  padding: 10px 12px;
}
/* The polygons and the basemap stay light in both modes, so everything drawn over
   them keeps the light surface too: a legend on a dark plate would key the darkest
   classes in swatches that sink into the plate. */
.map-wrap .panel, .leaflet-tooltip.map-tip {
  --surface-1: #fcfcfb;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #898781;
  --border: rgba(11, 11, 11, 0.14);
}
.legend { right: 12px; bottom: 20px; max-width: 230px; }
.legend h2 { font-size: 11px; font-weight: 600; color: var(--text-muted); margin: 0 0 6px; }
.legend ul { list-style: none; margin: 0; padding: 0; }
.legend li {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: var(--text-secondary); padding: 1px 0;
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 14px; height: 14px; flex: 0 0 14px; border-radius: 3px;
  border: 1px solid var(--border);
}
.yearbar { left: 12px; bottom: 20px; display: flex; align-items: center; gap: 10px; }
.yearbar label { font-size: 12px; color: var(--text-muted); }
.yearbar input { width: 190px; accent-color: #2a78d6; }
.yearbar output { font-size: 13px; font-weight: 600; min-width: 3.2em; font-variant-numeric: tabular-nums; }
.leaflet-tooltip.map-tip {
  background: var(--surface-1);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.16);
  font: 12px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
  padding: 7px 9px;
}
.leaflet-tooltip.map-tip::before { display: none; }
.tiled-tip { position: absolute; z-index: 700; pointer-events: none; white-space: nowrap; }
.tile-problem {
  left: 50%; top: 24px; transform: translateX(-50%);
  max-width: min(560px, calc(100% - 32px)); font-size: 13px; line-height: 1.5;
}
.tile-problem pre {
  margin: 6px 0; padding: 6px 8px; border-radius: 4px; overflow-x: auto;
  background: rgba(11, 11, 11, 0.06); font-size: 12px;
}
.tile-problem code { background: rgba(11, 11, 11, 0.06); padding: 1px 4px; border-radius: 3px; }
.map-tip .tip-name { font-weight: 600; display: block; margin-bottom: 2px; }
.map-tip .tip-value { font-variant-numeric: tabular-nums; }
.map-tip .tip-meta { color: var(--text-muted); }
details {
  margin-top: 16px; background: var(--surface-1);
  border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px;
}
summary { cursor: pointer; font-size: 13px; color: var(--text-secondary); }
.table-scroll { overflow-x: auto; max-height: 420px; overflow-y: auto; margin-top: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 12px; }
th, td { text-align: left; padding: 5px 10px 5px 0; border-bottom: 1px solid var(--hairline); white-space: nowrap; }
th { position: sticky; top: 0; background: var(--surface-1); color: var(--text-muted); font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
footer { margin-top: 14px; font-size: 12px; color: var(--text-muted); }
footer a { color: inherit; }
</style>
</head>
<body>
<div class="viz-root">
  <h1 id="heading">__TITLE__</h1>
  <p class="sub" id="subtitle">__SUBTITLE__</p>
__VARIABLE_CONTROL__
  <div class="map-wrap">
    <div id="map" role="application" aria-label="__ARIA_LABEL__"></div>
    <div class="panel legend">
      <h2 id="legend-title"></h2>
      <ul id="legend-items"></ul>
    </div>
__YEAR_CONTROL__
  </div>
  <details>
    <summary id="table-summary">Data table</summary>
    <div class="table-scroll">
      <table>
        <thead><tr id="table-head"></tr></thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
    <p class="sub" id="table-note" style="margin: 8px 0 0"></p>
  </details>
  <footer>__FOOTER__</footer>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
__TILE_SCRIPT__
<script>
// The payload is written either as plain JSON, which stays readable in an editor,
// or gzipped and base64'd when it is big enough for that to matter — the geometry
// of a country is around a third of the size compressed.
const MAP_PAYLOAD = __PAYLOAD__;
const MAP_PAYLOAD_GZIP = __PAYLOAD_GZIP__;
const TABLE_LIMIT = 500;

let MAP_DATA = null;
let map = null;
let layer = null;
let currentSeries = 0;
let currentYear = null;
// Tiled features arrive carrying only their area code, so the code is what finds an
// area's values; an embedded feature carries its position directly.
const CODE_INDEX = {};

function series() { return MAP_DATA.series[currentSeries]; }

// One year is written as a plain array, several as an array per year: either way
// this returns the column the map is showing.
function column(store, year) {
  return (year === null) ? store : store[year];
}

function classAt(index) {
  const values = column(series().k, currentYear);
  const value = values ? values[index] : null;
  return (value === undefined || value === null) ? null : value;
}

function textAt(index, year) {
  const values = column(series().t, year);
  const value = values ? values[index] : null;
  return (value === undefined || value === null) ? MAP_DATA.noDataLabel : value;
}

function rowTexts(index) {
  if (!MAP_DATA.years.length) { return [textAt(index, null)]; }
  return MAP_DATA.years.map(function (year) { return textAt(index, year); });
}

// Canvas rather than the default SVG: a census tract is one <path> element there,
// and a page of them is tens of thousands of DOM nodes the browser lays out and
// rewrites on every pan. On canvas the whole layer is one node.
function styleAt(position) {
  const k = (position === undefined) ? null : classAt(position);
  return {
    fill: true,
    fillColor: k === null ? MAP_DATA.noDataColor : series().colors[k],
    fillOpacity: k === null ? 0.45 : 0.82,
    color: '#ffffff',
    weight: 0.5,
    opacity: 1
  };
}

function styleOf(feature) { return styleAt(feature.properties.i); }

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, function (character) {
    return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[character];
  });
}

function tooltipOf(position) {
  if (position === undefined) { return ''; }
  return '<span class="tip-name">' + escapeHtml(MAP_DATA.names[position]) + '</span>' +
         '<span class="tip-meta">' + escapeHtml(MAP_DATA.codes[position]) + '</span><br>' +
         '<span class="tip-value">' + escapeHtml(series().label) + ': <strong>' +
         escapeHtml(textAt(position, currentYear)) + '</strong></span>';
}

// The tile a probe asks for: whichever covers the middle of what is being mapped, at
// a zoom the archive certainly holds.
function probeTileUrl() {
  const bounds = MAP_DATA.bounds;
  const latitude = (bounds[0][0] + bounds[1][0]) / 2;
  const longitude = (bounds[0][1] + bounds[1][1]) / 2;
  const zoom = 6, n = Math.pow(2, zoom);
  const radians = latitude * Math.PI / 180;
  return MAP_DATA.tiles.url
    .replace('{z}', zoom)
    .replace('{x}', Math.floor((longitude + 180) / 360 * n))
    .replace('{y}', Math.floor((1 - Math.log(Math.tan(radians) + 1 / Math.cos(radians))
                                / Math.PI) / 2 * n));
}

// A tile that cannot be fetched draws nothing and says nothing, which looks exactly
// like a map with no data on it. So the fetch is tried once, up front, and what went
// wrong is put on the page instead of leaving it blank.
function reportTileProblem(reason) {
  const panel = L.DomUtil.create('div', 'panel tile-problem', map.getContainer());
  const served = location.protocol === 'file:'
    ? 'This map keeps its geometry in vector tiles, and a page opened straight from a ' +
      'file is not allowed to fetch them — which is why the areas are missing.'
    : 'The vector tiles this map draws from could not be fetched (' + escapeHtml(reason) + ').';
  panel.innerHTML =
    '<strong>The areas cannot be drawn</strong><br>' + served +
    '<br><br>Serve the maps and open it from there:' +
    '<pre>server = INE.ServeMaps(wd)</pre>' +
    'then open <code>' + escapeHtml(location.pathname.split('/').pop()) +
    '</code> under the address it prints.';
}

async function tilesReachable() {
  try {
    const response = await fetch(probeTileUrl());
    if (!response.ok && response.status !== 204) { throw new Error('HTTP ' + response.status); }
    return true;
  } catch (error) {
    reportTileProblem(error.message || String(error));
    return false;
  }
}

// Vector tiles have no per-feature Leaflet layer to hang a tooltip on, so the tiled
// map carries its own, following the pointer the way a sticky tooltip would.
function startTiled() {
  const tip = L.DomUtil.create('div', 'leaflet-tooltip map-tip tiled-tip', map.getContainer());
  tip.style.display = 'none';

  layer = L.vectorGrid.protobuf(MAP_DATA.tiles.url, {
    rendererFactory: L.canvas.tile,
    interactive: true,
    maxNativeZoom: MAP_DATA.tiles.maxZoom,
    getFeatureId: function (feature) { return feature.properties.c; },
    vectorTileLayerStyles: {
      areas: function (properties) { return styleAt(CODE_INDEX[properties.c]); }
    }
  }).addTo(map);

  layer.on('mouseover', function (event) {
    const position = CODE_INDEX[event.layer.properties.c];
    if (position === undefined) { return; }
    tip.innerHTML = tooltipOf(position);
    tip.style.display = '';
  });
  layer.on('mouseout', function () { tip.style.display = 'none'; });
  map.getContainer().addEventListener('mousemove', function (event) {
    if (tip.style.display === 'none') { return; }
    const box = map.getContainer().getBoundingClientRect();
    tip.style.left = (event.clientX - box.left + 14) + 'px';
    tip.style.top = (event.clientY - box.top + 14) + 'px';
  });
}

function renderHeading() {
  document.getElementById('heading').textContent = MAP_DATA.title || series().label;
  document.getElementById('subtitle').textContent =
    (MAP_DATA.title ? series().label + ' \\u00b7 ' : '') + MAP_DATA.subtitle;
}

// Built as elements rather than as markup: a class label is data, and data does not
// belong in an innerHTML.
function renderLegend() {
  document.getElementById('legend-title').textContent = series().legendTitle;
  const list = document.getElementById('legend-items');
  list.replaceChildren();
  series().legend.forEach(function (item) {
    const swatch = document.createElement('span');
    swatch.className = 'swatch';
    swatch.style.background = item[0];
    const row = document.createElement('li');
    row.appendChild(swatch);
    row.appendChild(document.createTextNode(item[1]));
    list.appendChild(row);
  });
}

// The reader looks up the largest values, so the table leads with them; areas with
// no value sort last whichever year is asked for.
function sortKey(texts) {
  for (let index = texts.length - 1; index >= 0; index--) {
    const number = parseFloat(String(texts[index]).replace(/,/g, ''));
    if (!isNaN(number)) { return -number; }
  }
  return Infinity;
}

function renderTable() {
  const numeric = series().numeric;
  const columnClass = numeric ? 'num' : '';

  const rows = MAP_DATA.names.map(function (name, position) {
    return {name: name, code: MAP_DATA.codes[position], texts: rowTexts(position)};
  });
  if (numeric) {
    rows.sort(function (left, right) { return sortKey(left.texts) - sortKey(right.texts); });
  } else {
    rows.sort(function (left, right) { return left.name.localeCompare(right.name); });
  }

  const head = document.getElementById('table-head');
  head.replaceChildren();
  const headings = [MAP_DATA.level, 'Code'].concat(
    MAP_DATA.years.length ? MAP_DATA.years : [series().label]);
  headings.forEach(function (text, position) {
    const cell = document.createElement('th');
    if (position > 1) { cell.className = columnClass; }
    cell.textContent = text;
    head.appendChild(cell);
  });

  const body = document.getElementById('table-body');
  body.replaceChildren();
  rows.slice(0, TABLE_LIMIT).forEach(function (row) {
    const line = document.createElement('tr');
    [row.name, row.code].concat(row.texts).forEach(function (text, position) {
      const cell = document.createElement('td');
      if (position > 1) { cell.className = columnClass; }
      cell.textContent = text;
      line.appendChild(cell);
    });
    body.appendChild(line);
  });

  document.getElementById('table-summary').textContent =
    'Data table (' + rows.length.toLocaleString('en-US') + ' areas)';
  document.getElementById('table-note').textContent = rows.length > TABLE_LIMIT
    ? 'Showing the first ' + TABLE_LIMIT + ' of ' + rows.length.toLocaleString('en-US') + ' areas.'
    : '';
}

function repaint() {
  if (MAP_DATA.tiles) {
    layer.redraw();     // re-runs the style function over the tiles already fetched
    return;
  }
  layer.setStyle(styleOf);
  layer.eachLayer(function (featureLayer) {
    featureLayer.setTooltipContent(tooltipOf(featureLayer.feature.properties.i));
  });
}

// Read through a stream reader rather than through Response, whose fetch machinery
// a page opened from a file:// URL is not allowed to use.
async function inflate(base64) {
  const bytes = Uint8Array.from(atob(base64), function (c) { return c.charCodeAt(0); });
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  const reader = stream.getReader();
  const chunks = [];
  let total = 0;
  for (;;) {
    const step = await reader.read();
    if (step.done) { break; }
    chunks.push(step.value);
    total += step.value.length;
  }
  const merged = new Uint8Array(total);
  let at = 0;
  chunks.forEach(function (chunk) { merged.set(chunk, at); at += chunk.length; });
  return new TextDecoder().decode(merged);
}

function wire() {
  const variableInput = document.getElementById('variable-input');
  if (variableInput) {
    variableInput.addEventListener('change', function () {
      currentSeries = Number(variableInput.value);
      renderHeading();
      renderLegend();
      renderTable();
      repaint();
    });
  }

  const yearInput = document.getElementById('year-input');
  if (yearInput) {
    const yearLabel = document.getElementById('year-label');
    yearInput.addEventListener('input', function () {
      currentYear = MAP_DATA.years[Number(yearInput.value)];
      yearLabel.value = currentYear;
      repaint();
    });
  }
}

async function start() {
  if (MAP_PAYLOAD_GZIP) {
    if (typeof DecompressionStream === 'undefined') {
      document.getElementById('subtitle').textContent =
        'This page needs a browser with DecompressionStream (Chrome or Edge 80+, Firefox 113+, ' +
        'Safari 16.4+) to unpack its geometry.';
      return;
    }
    MAP_DATA = JSON.parse(await inflate(MAP_PAYLOAD_GZIP));
  } else {
    MAP_DATA = MAP_PAYLOAD;
  }

  currentYear = MAP_DATA.years.length ? MAP_DATA.years[MAP_DATA.years.length - 1] : null;
  MAP_DATA.codes.forEach(function (code, position) { CODE_INDEX[code] = position; });

  map = L.map('map', {scrollWheelZoom: true, zoomControl: true, preferCanvas: true});
  if (MAP_DATA.basemap) {
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
                   'contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: 19
    }).addTo(map);
  }

  if (MAP_DATA.tiles) {
    if (await tilesReachable()) { startTiled(); }
  } else {
    layer = L.geoJSON(MAP_DATA.geojson, {
      style: styleOf,
      onEachFeature: function (feature, featureLayer) {
        featureLayer.bindTooltip(tooltipOf(feature.properties.i),
                                 {sticky: true, className: 'map-tip', direction: 'top'});
        featureLayer.on('mouseover', function (event) {
          event.target.setStyle({weight: 2, color: '#0b0b0b'});
          event.target.bringToFront();
        });
        featureLayer.on('mouseout', function (event) { layer.resetStyle(event.target); });
      }
    }).addTo(map);
  }

  map.fitBounds(MAP_DATA.bounds);

  renderHeading();
  renderLegend();
  renderTable();
  wire();
}

start();
</script>
</body>
</html>
"""


def _map_year_control(years):
    """The year slider, when the data spans more than one year."""
    if len(years) < 2:
        return ""

    options = "".join(f'<option value="{index}" label="{year}"></option>'
                      for index, year in enumerate(years))

    return (f'    <div class="panel yearbar">\n'
            f'      <label for="year-input">Year</label>\n'
            f'      <input type="range" id="year-input" min="0" max="{len(years) - 1}" step="1" '
            f'value="{len(years) - 1}" list="year-ticks" aria-label="Year shown on the map">\n'
            f'      <datalist id="year-ticks">{options}</datalist>\n'
            f'      <output id="year-label" for="year-input">{years[-1]}</output>\n'
            f'    </div>\n')


def _map_variable_control(labels):
    """The variable picker, when the page carries more than one variable."""
    if len(labels) < 2:
        return ""

    options = "".join(f'<option value="{index}">{_html_escape(label)}</option>'
                      for index, label in enumerate(labels))

    return (f'  <div class="controls">\n'
            f'    <label for="variable-input">Variable</label>\n'
            f'    <select id="variable-input">{options}</select>\n'
            f'  </div>\n')


def _map_legend_title(variable):
    """A heading short enough for the legend, which sits in a corner of the map."""
    title = variable.split("~")[-1].strip()
    return title if len(title) <= 46 else title[:45].rstrip() + "…"


def _map_variables(df, variable, keys):
    """Which columns the page will carry.

    Without a `variable`, every column that says something about an area rather than
    which area it is, skipping the ones that hold nothing and the text columns with
    too many distinct values to read as classes.
    """
    if variable is not None:
        variables = [variable] if isinstance(variable, str) else list(variable)
        missing = [name for name in variables if name not in df.columns]
        if missing:
            offered = [column for column in df.columns
                       if column not in keys and column not in _MAP_NON_VARIABLE_COLUMNS]
            raise ValueError(f"No column {missing} in the table. It can map {offered}.")
        return variables

    variables = []
    for column in df.columns:
        if column in keys or column in _MAP_NON_VARIABLE_COLUMNS:
            continue
        if not df[column].notna().any():
            continue
        if not pd.api.types.is_numeric_dtype(df[column]):
            if (pd.api.types.is_datetime64_any_dtype(df[column]) or
                    df[column].nunique(dropna=True) > _MAP_MAX_CATEGORIES_OFFERED):
                continue
        variables.append(column)

    if not variables:
        raise ValueError("No column of this table can be mapped: they all identify the area rather "
                         "than describe it. Pass `variable` to map one anyway.")

    return variables


def _map_series(df, variable, classification, bins, palette, center):
    """Classify one variable into the classes, colours and labels the page draws it with.

    Returns the class of each row of `df` and its formatted value, alongside the
    colours and the legend of the classification they belong to.
    """
    numeric = pd.api.types.is_numeric_dtype(df[variable])
    if not numeric and palette in ("sequential", "diverging"):
        palette = "categorical"

    if numeric:
        values = pd.to_numeric(df[variable], errors="coerce").to_numpy(dtype=float)
        edges = _map_bin_edges(values, classification, bins, palette, center)
        colors = _map_colors(len(edges) - 1, palette)
        decimals = _map_decimals(edges)

        classes = np.clip(np.searchsorted(edges, values, side="left") - 1,
                          0, len(colors) - 1).astype(float)
        classes[~np.isfinite(values)] = np.nan
        texts = [_format_map_number(value, decimals) for value in values]

        legend = [[colors[index],
                   f"{_format_map_number(edges[index], decimals)} – "
                   f"{_format_map_number(edges[index + 1], decimals)}"]
                  for index in range(len(colors))]
    else:
        text = df[variable].astype("string")
        counts = text.value_counts()
        categories = list(counts.index[:len(_MAP_CATEGORICAL)])
        if len(counts) > len(_MAP_CATEGORICAL):
            print(f"{variable!r} takes {len(counts)} values, more than the {len(_MAP_CATEGORICAL)} "
                  f"a map can tell apart; the rest are shown as 'Other'", file=sys.stdout)
            categories = categories[:len(_MAP_CATEGORICAL) - 1] + ["Other"]
            text = text.where(text.isin(categories[:-1]) | text.isna(), "Other")

        colors = _map_colors(len(categories), "categorical")
        order = {category: index for index, category in enumerate(categories)}
        classes = pd.to_numeric(text.map(order), errors="coerce").to_numpy(dtype=float)
        texts = list(text.fillna("no data").astype(str))

        legend = [[color, category] for color, category in zip(colors, categories)]

    return {"label": variable, "legendTitle": _map_legend_title(variable), "numeric": numeric,
            "colors": colors, "legend": legend, "classes": classes, "texts": texts}


def MapVariable(data, variable=None, wd=None, level=None, year=None, boundaries_year=None,
                output_file=None, classification="quantiles", bins=6, palette="sequential",
                center=None, title=None, subtitle=None, basemap=True, tiles=False,
                simplify_tolerance=None, max_areas=25000, max_cells=10000000):
    """Write a standalone HTML choropleth of a dataset.

    Takes what any of the dataset functions returns, joins its variables to the INE
    boundaries of the matching year (see `AdministrativeBoundaries`) and writes an
    interactive map: hover an area for its value, and, when the data spans several
    years, drag the year slider. The classes are computed over every year at once,
    so the colours mean the same thing at each stop of the slider. The page also
    carries the values as a table, since a colour alone is not a readable number.

    The page is one self-contained file: the geometry travels inside it, gzipped and
    base64'd once it is big enough for that to pay (it is unpacked in the browser
    with `DecompressionStream`, which needs Chrome or Edge 80+, Firefox 113+ or
    Safari 16.4+). Only the basemap tiles are fetched, so a page opened offline draws
    its areas with nothing underneath them.

    Leaving `variable` out puts **every** mappable column of the table in the page,
    behind a picker, so the map can be read without deciding beforehand which
    variable was the interesting one. Each variable is classified on its own, and
    the legend, the heading and the table follow the picker.

    Needs geopandas, which social_ES does not install by default: `pip install
    social_ES[geo]`.

    Examples
    --------
    >>> atlas = INE.HouseholdIncomeDistributionAtlas(wd=wd, municipality_code="08019")
    >>> INE.MapVariable(atlas, "Average net income per person", wd=wd, year=2021)
    >>> INE.MapVariable(atlas, wd=wd, year=2021)   # every variable, pick in the page

    Parameters
    ----------
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
        non-numeric variable, whose values are the classes.
    bins : int, default 6
        Number of classes.
    palette : {"sequential", "diverging", "categorical"}, default "sequential"
        ``"sequential"`` for a magnitude, ``"diverging"`` for a value read against
        a midpoint (a change, a difference from an average), ``"categorical"`` for
        classes with no order. A non-numeric variable is always categorical.
    center : float, optional
        The midpoint of a diverging map. Defaults to 0.
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
        and year, and the browser fetches only the tiles it draws — which is what
        makes the 36,333 census tracts of the country mappable at full detail. The
        page then has to be served rather than opened from disk: see `ServeMaps`.
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
    """
    # Checked up front, so that a missing geopandas is reported before a dataset the
    # size of a census has been ground through.
    _require_geopandas()

    if wd is None:
        raise TypeError("MapVariable() needs `wd`, the working directory the cartography is "
                        "cached under.")

    df, level = _map_dataframe_and_level(data, level)

    keys = _BOUNDARY_LEVEL_KEYS[level]
    missing_keys = [key for key in keys if key not in df.columns]
    if missing_keys:
        raise ValueError(f"The {level!r} table carries no {missing_keys} column, which is what its "
                         f"areas are identified by.")

    df = df.dropna(subset=keys).copy()
    for key in keys:
        df[key] = _normalise_code(df[key], _MAP_CODE_WIDTHS[key])

    # Years -------------------------------------------------------------------
    years = []
    if "Year" in df.columns:
        if year is not None:
            wanted = [year] if isinstance(year, (int, np.integer, str)) else list(year)
            df = df[df["Year"].isin([int(one) for one in wanted])]
            if df.empty:
                raise ValueError(f"No row of the {level!r} table is of year(s) {wanted}.")
        years = sorted(int(one) for one in df["Year"].dropna().unique())

    variables = _map_variables(df, variable, keys)

    group_keys = keys + (["Year"] if years else [])
    if df.duplicated(subset=group_keys).any():
        # Several rows per area and year — a dataset published by quarter, say.
        # Averaging is the only reading that does not depend on the row order, and
        # saying so is better than a map of whichever row happened to come first.
        print(f"Several rows per area and year in the {level!r} table; mapping their mean",
              file=sys.stdout)
        df = df.groupby(group_keys, as_index=False).agg(
            {name: ("mean" if pd.api.types.is_numeric_dtype(df[name]) else "first")
             for name in variables})
    else:
        df = df[group_keys + variables].copy()

    if years:
        df["Year"] = df["Year"].astype(int)

    # A single year is written into the page as a plain value rather than as a
    # one-entry mapping: there is nothing to slide between, so there is no slider.
    slider_years = years if len(years) > 1 else []
    single_year = years[0] if len(years) == 1 else None

    # Geometry ----------------------------------------------------------------
    boundaries_year = _resolve_boundary_year(boundaries_year if boundaries_year is not None
                                             else (max(years) if years else None))

    filters = {}
    for column, argument in _MAP_BOUNDARY_FILTERS.items():
        if column in keys:
            filters[argument] = sorted(df[column].unique())
            break

    gdf = AdministrativeBoundaries(wd=wd, year=boundaries_year, level=level, **filters)

    # With tiles the geometry never enters the page, so how many areas it covers stops
    # being the thing that decides whether the page is openable.
    if not tiles and len(gdf) > max_areas:
        raise ValueError(f"{len(gdf):,} areas is more than `max_areas` ({max_areas:,}); a page that "
                         f"big is slow to open. Filter the data (by municipality, say), raise "
                         f"`max_areas` deliberately, or pass `tiles=True` to serve the geometry as "
                         f"vector tiles instead of carrying it.")

    cells = len(gdf) * len(variables) * max(1, len(years))
    if cells > max_cells:
        raise ValueError(f"{len(gdf):,} areas × {len(variables)} variables × {max(1, len(years))} "
                         f"years is {cells:,} values, more than `max_cells` ({max_cells:,}), and "
                         f"more than a page holds comfortably. Pass `variable` to map fewer of "
                         f"them, filter the data, or raise `max_cells` deliberately.")

    tiles_url = None
    if tiles:
        # Built over the whole country rather than over what this map draws, so that
        # every other map of the same level and year reuses it.
        archive = BoundaryTiles(wd=wd, year=boundaries_year, level=level)
        tiles_url = os.path.basename(archive)
    elif simplify_tolerance is None:
        simplify_tolerance = _default_simplify_tolerance(gdf)

    if not tiles and simplify_tolerance:
        # A degree of latitude is 111.32 km everywhere, and of longitude three
        # quarters of that at these latitudes, so a tolerance converted at the
        # latitude rate is within a quarter of what was asked for — which is all a
        # simplification tolerance ever is.
        gdf = gdf.assign(geometry=gdf.geometry.simplify(simplify_tolerance / 111320.0,
                                                        preserve_topology=True))

    # Which row of the data each area reads its values from ---------------------
    code_columns = [df[key].to_numpy() for key in keys]
    year_values = df["Year"].to_numpy() if years else None

    row_of = {}
    for position in range(len(df)):
        code = tuple(column[position] for column in code_columns)
        row_of.setdefault(code, {})[int(year_values[position]) if years else None] = position

    # The areas ---------------------------------------------------------------
    name_column = ("Municipality name" if "Municipality name" in gdf.columns else
                   "Province name" if "Province name" in gdf.columns else
                   "Autonomous community name")

    gdf_codes = [gdf[key].to_numpy() for key in keys]
    gdf_names = gdf[name_column].to_numpy()
    gdf_geometries = gdf.geometry.to_numpy()

    # The names and codes travel as their own arrays, in the order the values are
    # written in, so that a tiled page — whose features arrive carrying nothing but a
    # code — reads them the same way an embedded one does.
    features, area_rows, names, codes = [], [], [], []
    bounds = None

    for position in range(len(gdf)):
        code = tuple(column[position] for column in gdf_codes)
        rows = row_of.get(code, {})

        name = gdf_names[position]
        name = "" if name is None or (isinstance(name, float) and np.isnan(name)) else str(name)
        if level == "Census tracts":
            label = f"{name} — district {code[1]}, tract {code[2]}"
        elif level == "Districts":
            label = f"{name} — district {code[1]}"
        else:
            label = name

        if not tiles:
            features.append({
                "type": "Feature",
                "properties": {"i": len(features)},
                "geometry": _round_geometry(gdf_geometries[position], 6),
            })
        names.append(label)
        codes.append("".join(code))
        area_rows.append(rows)

        if rows:
            # Framed on the areas that carry data, so that a single mapped
            # municipality is not lost in the extent of the province it was cut from.
            area_bounds = gdf_geometries[position].bounds
            bounds = area_bounds if bounds is None else (
                min(bounds[0], area_bounds[0]), min(bounds[1], area_bounds[1]),
                max(bounds[2], area_bounds[2]), max(bounds[3], area_bounds[3]))

    if bounds is None:
        raise ValueError(f"None of the areas of the data matched a boundary of {boundaries_year}. "
                         f"Codes change from year to year — check `level`, and try a "
                         f"`boundaries_year` closer to the data.")

    mapped_codes = {tuple(column[position] for column in gdf_codes) for position in range(len(gdf))}
    unmatched = len(set(row_of) - mapped_codes)
    if unmatched:
        print(f"{unmatched:,} areas of the data have no boundary in the {boundaries_year} "
              f"cartography and are left off the map. Codes change from year to year; try a "
              f"`boundaries_year` closer to the data.", file=sys.stdout)

    # The variables -----------------------------------------------------------
    def area_column(series, key, published_year):
        """The class, or the text, of every area for one year of one variable."""
        source = series["classes"] if key == "classes" else series["texts"]
        column = []
        for rows in area_rows:
            position = rows.get(published_year)
            if position is None:
                column.append(None)
            elif key == "classes":
                value = source[position]
                column.append(None if pd.isna(value) else int(value))
            else:
                column.append(source[position])
        return column

    payload_series = []
    for name in variables:
        series = _map_series(df, name, classification, bins, palette, center)
        if slider_years:
            classes = {str(one): area_column(series, "classes", one) for one in slider_years}
            texts = {str(one): area_column(series, "texts", one) for one in slider_years}
            missing = any(value is None for column in classes.values() for value in column)
        else:
            classes = area_column(series, "classes", single_year)
            texts = area_column(series, "texts", single_year)
            missing = any(value is None for value in classes)

        # Keyed per variable, not per page: a table can publish one variable for
        # every area and another for only some of them, and the grey needs saying
        # exactly where it is drawn.
        legend = series["legend"] + ([[_MAP_NO_DATA_COLOR, "no data"]] if missing else [])

        payload_series.append({"label": series["label"], "legendTitle": series["legendTitle"],
                               "numeric": series["numeric"], "colors": series["colors"],
                               "legend": legend, "k": classes, "t": texts})

    # The page ----------------------------------------------------------------
    minx, miny, maxx, maxy = bounds

    year_text = (f"{years[0]}" if len(years) == 1 else
                 f"{years[0]}–{years[-1]}" if years else "")
    level_text = level if level != "Municipality" else "Municipalities"
    subtitle = subtitle if subtitle is not None else (
        f"{level_text}" + (f" · {year_text}" if year_text else "") +
        f" · {len(names):,} areas" +
        (" · drag the slider to change the year" if slider_years else ""))

    payload = {
        "geojson": None if tiles else {"type": "FeatureCollection", "features": features},
        "tiles": ({"url": f"../tiles/{tiles_url}/{{z}}/{{x}}/{{y}}.pbf",
                   "layer": "areas", "maxZoom": _PMTILES_MAX_ZOOM} if tiles else None),
        "names": names,
        "codes": codes,
        "series": payload_series,
        "noDataColor": _MAP_NO_DATA_COLOR,
        "noDataLabel": "no data",
        "years": [str(one) for one in slider_years],
        "level": level_text,
        "title": title,
        "subtitle": subtitle,
        "basemap": bool(basemap),
        "bounds": [[float(miny), float(minx)], [float(maxy), float(maxx)]],
    }

    source = (f'Data: <a href="https://www.ine.es">INE</a>. Boundaries: '
              f'<a href="{_INE_CARTOGRAPHY_PAGE}">INE census tract cartography, {boundaries_year}</a>'
              f'. Built with social_ES.')

    # The heading and the subtitle are also written into the page as text, so that
    # it reads as something before its script has run.
    heading = title or variables[0]

    # Compressed only when it pays for itself: a small page stays plain JSON, which
    # can be read, searched and patched in a text editor, and the base64 of a small
    # payload saves too little to be worth giving that up.
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    if len(payload_json.encode("utf-8")) >= _MAP_GZIP_THRESHOLD:
        packed = base64.b64encode(
            gzip.compress(payload_json.encode("utf-8"), 9)).decode("ascii")
        payload_block, payload_gzip_block = "null", f'"{packed}"'
    else:
        payload_block, payload_gzip_block = payload_json, "null"

    page = (_MAP_HTML_TEMPLATE
            .replace("__PAGE_TITLE__", _html_escape(heading))
            .replace("__TITLE__", _html_escape(heading))
            .replace("__SUBTITLE__", _html_escape(subtitle))
            .replace("__ARIA_LABEL__", _html_escape(f"Map of {heading} by {level_text.lower()}"))
            .replace("__VARIABLE_CONTROL__", _map_variable_control(variables))
            .replace("__YEAR_CONTROL__", _map_year_control([str(one) for one in slider_years]))
            .replace("__FOOTER__", source)
            .replace("__TILE_SCRIPT__",
                     '<script src="https://unpkg.com/leaflet.vectorgrid@1.3.0/dist/'
                     'Leaflet.VectorGrid.bundled.js"></script>' if tiles else "")
            .replace("__PAYLOAD_GZIP__", payload_gzip_block)
            .replace("__PAYLOAD__", payload_block))

    if output_file is None:
        path = path_creator("INE/Maps", wd)
        slug = re.sub(r"[^a-z0-9]+", "-", (title or variables[0]).lower()).strip("-")
        if len(variables) > 1 and title is None:
            slug = "all-variables"
        output_file = f"{path}/{slug}_{_BOUNDARY_LEVEL_FILES[level]}" + \
                      (f"_{year_text.replace('–', '-')}" if year_text else "") + ".html"

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(page)

    print(f"Map written to {output_file}", file=sys.stdout)

    return output_file
