import pandas as pd
from io import StringIO
import os
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import numpy as np

# Generic utils

def get_links_that_contain(regexp, html):

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile(regexp)}):
        links.append(link.get('href'))

    return (links)


def is_number(s):
    if s is None or isinstance(s, float) and s != s:  # Check for None or NaN
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def fetch_data(url,separation=";",type=None):
    r = requests.get(url)
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


# Gather functions for Spanish National Statistics datasets

def INERentalDistributionAtlas(path, municipality_code, years):

    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):

        print("Reading the metadata to gather the INE Rental Distribution Atlas", file=sys.stdout)
        req = requests.get('https://www.ine.es/dynt3/inebase/en/index.htm?padre=7132',
                           headers={'User-Agent': 'Mozilla/5.0'})
        urls = get_links_that_contain("capsel", req.text)
        g_ids = []

        for url in urls:
            req = requests.get(f'https://www.ine.es/dynt3/inebase/en/index.htm{url}',
                               headers={'User-Agent': 'Mozilla/5.0'})
            x = [re.search(r'(t=)(?P<x>\w+)(&L)', link).group('x') for link in
                 get_links_that_contain("Export", req.text)]
            g_ids.append(x)

        g_urls = [[f"https://www.ine.es/jaxiT3/files/t/en/csv_bd/{id}.csv?nocab=1" for id in ids] for ids in g_ids]
        g_df = pd.DataFrame()

        for urls in tqdm(g_urls, desc="Downloading files from INE by provinces..."):
            df = pd.DataFrame()
            for url in urls:
                r = requests.get(url)
                r.encoding = 'utf-8'
                df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8")
                df_["Municipality name"] = df_["Municipalities"].astype(str).str[6:]
                df_["Municipality code"] = df_["Municipalities"].astype(str).str[:5]
                df_["District code"] = df_["Distritos"].astype(str).str[5:7]
                df_["Section code"] = df_["Sections"].astype(str).str[7:10]
                try:
                    df_["Year"] = df_["Periodo"]
                except KeyError:
                    df_["Year"] = df_["Period"]
                df_["Value"] = df_["Total"]
                df_["Value"] = pd.to_numeric(df_["Total"].astype(str).str.replace('.', '').str.replace(',', '.'), errors="coerce")
                df_ = df_.sort_values(by='Value', na_position='last')
                df_ = df_.drop(columns=["Municipalities","Distritos","Sections","Periodo","Total"])
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
                                    ['Municipality name', 'Municipality code', 'District code', 'Section code', 'Year']],
                         columns= [col for col in df_.columns if col not in
                                    ['Municipality name', 'Municipality code', 'District code', 'Section code', 'Year', 'Value']],
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
                    merge_on = ['Municipality name', 'Municipality code', 'District code', 'Section code', 'Year']
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

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    g_df["Country code"] = "ES"
    g_df["Province code"] = g_df["Municipality code"].str[:2]
    municipality = g_df[pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    districts = districts[districts.columns[districts.notna().any()]]
    sections = g_df[-pd.isna(g_df["District code"]) & -pd.isna(g_df["Section code"])]
    sections = sections[sections.columns[sections.notna().any()]]

    return ({
        "Municipality": municipality,
        "Districts": districts,
        "Sections": sections
    })

def INEPopulationAnualCensus(path,municipality_code,years):
    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):

        print("Reading the metadata to gather the INE population and household anual census", file=sys.stdout)
        base_link = "https://www.ine.es/dynt3/inebase/es/index.htm"
        sections_link = "?padre=10358"
        req = requests.get(f"{base_link}{sections_link}", headers={'User-Agent': 'Chrome/51.0.2704.103'})
        sections_link = get_links_that_contain("capsel", req.text)[-1]
        req = requests.get(f"{base_link}{sections_link}",headers={'User-Agent': 'Chrome/51.0.2704.103'})
        urls = get_links_that_contain("capsel", req.text)
        urls = urls[urls.index(sections_link)+1:]
        g_ids = []

        for url in urls:
            req = requests.get(f'{base_link}{url}',headers={'User-Agent': 'Mozilla/5'})
            x = [re.search(r'(tpx=)(?P<x>\w+)(&L)', link).group('x') for link in
                 get_links_that_contain("Export", req.text)]
            g_ids.append(x)

        g_urls = [[f"https://www.ine.es/jaxi/files/tpx/es/csv_bd/{id}.csv?nocab=1" for id in ids] for ids in g_ids]
        g_df = pd.DataFrame()
        year = 2021

        for urls in tqdm(g_urls, desc="Downloading files from INE by year..."):

            df = pd.DataFrame()

            for url in urls:

                r = requests.get(url)
                r.encoding = 'utf-8'
                df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", dtype={3:'str',6:'str'})
                df.to_csv("census.csv")
                cols = df_.columns
                if all([col in cols for col in ['Total Nacional', 'Provincias', 'Municipios', 'Secciones']]):
                    df_['Provincias'] = df_['Provincias'].fillna(df_['Total Nacional'])
                    df_['Municipios'] = df_['Municipios'].fillna(df_['Provincias'])
                    df_['Secciones'] = df_['Secciones'].fillna(df_['Municipios'])
                    df_ = df_.drop(columns = ['Total Nacional', 'Provincias', 'Municipios'])
                    cols = df_.columns

                allcols = {
                    "Sección censal": "Location",
                    "Secciones": "Location",
                    "Sexo": "Sex",
                    "Lugar de nacimiento (España/extranjero)": "Place of birth",
                    "Nacionalidad (española/extranjera)": "Nationality",
                    "Relación entre lugar de nacimiento y lugar de residencia": "Detailed place of birth",
                    "Total": "Value",
                    "Edad (grupos quinquenales)": "Age"
                }

                df_ = df_.rename(columns={col:allcols[col] for col in cols})
                cols = df_.columns

                if "Sex" in cols:
                    df_["Sex"] = df_["Sex"].replace({
                        "Hombre": "Males",
                        "Mujer": "Females",
                        "Ambos sexos": "Total"
                    })

                if "Place of birth" in cols:
                    df_["Place of birth"] = df_["Place of birth"].replace({
                        "España": "Spain",
                        "Extranjero": "Foreign country"
                    })

                if "Nationality" in cols:
                    df_["Nationality"] = df_["Nationality"].replace({
                        "Española": "Spanish",
                        "Extranjera": "Foreign"
                    })

                if "Detailed place of birth" in cols:
                    df_["Detailed place of birth"] = df_["Detailed place of birth"].replace({
                        "Mismo municipio": "Born in the same municipality",
                        "Distinto municipio de la misma provincia": "Born in a municipality of the same province",
                        "Distinta provincia de la misma comunidad": "Born in a municipality of the same autonomous community",
                        "Distinta comunidad": "Born in a municipality of another autonomous community",
                        "Nacido en el extranjero": "Born in another country"
                    })

                if "Age" in cols:
                    df_["Age"] = df_["Age"].str.replace("De ","").\
                        str.replace(" años","").\
                        str.replace(" a ","-").\
                        str.replace(" y más","").\
                        str.replace("100",">99")

                df_["Year"] = year
                df_["Value name"] = "Population"
                df_["Value"] = pd.to_numeric(df_["Value"].astype(str).str.replace(',', '').str.replace('.', ''), errors="coerce")

                df_ = pd.pivot(df_,
                               index=[col for col in df_.columns if col in
                                      ['Location', 'Year']],
                               columns=[col for col in df_.columns if col not in
                                        ['Location', 'Year', 'Value']],
                               values="Value")

                subgroups = ["Nationality", "Age", "Sex", "Place of birth", "Detailed place of birth"]
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
                df_.to_csv('census2.csv')
                df.to_csv('census1.csv')
                if len(df)>0:
                    df = pd.merge(df,df_[[col for col in df_.columns if col not in df.columns or col=="Location"]],
                                  on="Location")
                else:
                    df = df_

            year = year + 1
            if len(g_df)>0:
                g_df = pd.concat([g_df,df[g_df.columns]])
            else:
                g_df = df

        g_df["Country code"] = "ES"
        g_df["Location"] = g_df["Location"].replace({"Total Nacional":""})
        g_df["Province code"] = np.where(g_df["Location"].str[0].apply(is_number), g_df["Location"].str[0:2], np.nan)
        g_df["Municipality code"] = np.where(g_df["Location"].str[2].apply(is_number), g_df["Location"].str[0:5], np.nan)
        g_df["District code"] = np.where(g_df["Location"].str[5].apply(is_number), g_df["Location"].str[5:7], np.nan)
        g_df["Section code"] = np.where(g_df["Location"].str[7].apply(is_number), g_df["Location"].str[7:10], np.nan)
        g_df = g_df.drop(columns=["Location"])

        district = g_df.groupby(["Country code", "Province code", "Municipality code", "District code", "Year"])[
            [col for col in g_df.columns if col not in ["Country code", "Province code", "Municipality code", "District code", "Year","Section code"]]
            ].sum()
        district["Section code"] = np.nan
        district = district.set_index("Section code", append=True)
        district = district.reset_index()
        g_df = pd.concat([g_df[district.columns], district])

        g_df.to_csv(filename,sep="\t", index=False)

    else:
        g_df = pd.read_csv(filename, sep="\t")

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    # national = g_df[pd.isna(g_df["Province code"]) & pd.isna(g_df["Municipality code"]) & pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    # national = national[national.columns[national.notna().any()]]
    # province = g_df[-pd.isna(g_df["Province code"]) & pd.isna(g_df["Municipality code"]) & pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    # province = province[province.columns[province.notna().any()]]
    municipality = g_df[-pd.isna(g_df["Province code"]) & -pd.isna(g_df["Municipality code"]) & pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["Province code"]) & -pd.isna(g_df["Municipality code"]) & -pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    districts = districts[districts.columns[districts.notna().any()]]
    sections = g_df[-pd.isna(g_df["Province code"]) & -pd.isna(g_df["Municipality code"]) & -pd.isna(g_df["District code"]) & -pd.isna(g_df["Section code"])]
    sections = sections[sections.columns[sections.notna().any()]]

    return ({
        # "National": national,
        # "Province": province,
        "Municipality": municipality,
        "Districts": districts,
        "Sections": sections
    })


def INEHouseholdsPriceIndex(path):

    filename = f"{path}/df.tsv"


    if not os.path.exists(filename):

        r = requests.get("https://www.ine.es/jaxiT3/files/t/en/csv_bd/25171.csv?nocab=1")
        r.encoding = 'utf-8'
        df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8", dtype={3: 'str', 6: 'str'})
        df_ = df_[df_["Indices and rates"]=="Index"]
        df_["Country code"] = "ES"
        df_["Autonomous Communities and Cities"] = df_["Autonomous Communities and Cities"].str[:2]
        df_["Year"] = df_["Periodo"].str[:4].astype(int)
        df_["Quarter"] = df_["Periodo"].str[4:].replace({
            "QI": 1,
            "QII": 2,
            "QIII": 3,
            "QIV": 4
        })
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
        df_prov = pd.read_csv(filename, sep="\t")

    return ({
            "Province": df_prov
        })


def INEEssentialCharacteristicsOfPopulationAndHouseholds(path,municipality_code = None):
    # Year 2021, more info:
    # https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177092&menu=resultados&idp=1254735572981

    base_link = "https://www.ine.es/dynt3/inebase/en/index.htm"
    links_to_obtain_ids = {
        # "People": {
        #     "Mobility": "?padre=8983&capsel=8987",
        #     "FamilyDynamics": "?padre=8988&capsel=8992",
        #     "SocialSupport": "?padre=8993&capsel=8997",
        #     "FamilyOrigin": "?padre=8998&capsel=9002",
        #     "ContactWithNewTechnologies": "?padre=9003&capsel=9007",
        #     "LanguageKnowledge": "?padre=9008&capsel=9031"
        # },
        # "Homes": {
        #     "FamilyUnit": "?padre=9545&capsel=9549",
        #     "OneSinglePerson": "?padre=9550&capsel=9554",
        #     "Couples": "?padre=9555&capsel=9559",
        #     "Monoparental": "?padre=9560&capsel=9564",
        #     "SizeCharacteristics": "?padre=9565&capsel=9569",
        #     "Ownership": "?padre=9570&capsel=9574",
        #     "SecondHomes": "?padre=9575&capsel=9579",
        #     "Vehicles": "?padre=9580&capsel=9584",
        #     "WasteSeparation": "?padre=9585&capsel=9589",
        #     "DomesticServices": "?padre=9590&capsel=9594"
        # },
        "Households": {
            "Installations": "?padre=9595&capsel=9599",
            "MainHouseholdSizes": "?padre=9600&capsel=9604",
            "MainHouseholdContexts": "?padre=9605&capsel=9609",
            "AccessibilityAndConservation": "?padre=9610&capsel=9614",
            "BuildingInstallation": "?padre=9615&capsel=9619"
        }
    }

    filename = f"{path}/df.tsv"


    if not os.path.exists(filename):

        print("Reading the metadata to gather the INE essential characteristics of population and households", file=sys.stdout)

        for related_to, sections_dict in links_to_obtain_ids.items():
            # related_to, sections_dict = list(links_to_obtain_ids.items())[0]
            for subject, sections_link in sections_dict.items():
                # subject, sections_link = list(sections_dict.items())[0]
                req = requests.get(f"{base_link}{sections_link}",headers={'User-Agent': 'Chrome/51.0.2704.103'})
                ids = [re.search(r'(tpx=)(?P<x>\w+)(&L)', link).group('x') for link in
                 get_links_that_contain("dlgExport", req.text)]
                urls = [f"https://www.ine.es/jaxi/files/tpx/en/csv_bd/{id}.csv?nocab=1" for id in ids]

                df_BuildingTypeAndYearOfConstruction = None
                dfNetIncomes = None
                dfHouseholdComposition = None
                dfHouseholdArea= None

                for url in urls:
                    # url = urls[14]
                    r = requests.get(url)
                    r.encoding = 'utf-8'
                    df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8")
                    if (df_.columns.isin(["Municipios","Tipo de edificio","Año de construcción del edificio"]).sum()==3):
                        if df_BuildingTypeAndYearOfConstruction is None:
                            df_BuildingTypeAndYearOfConstruction = df_
                        else:
                            df_BuildingTypeAndYearOfConstruction = df_BuildingTypeAndYearOfConstruction.merge(df_)
                    elif (df_.columns.isin(['Municipios', 'Nivel de ingresos mensuales netos del hogar']).sum()==2):
                        if dfNetIncomes is None:
                            dfNetIncomes = df_
                        else:
                            dfNetIncomes = dfNetIncomes.merge(df_)
                    elif (df_.columns.isin(['Municipios', 'Número de miembros del hogar']).sum()==2):
                        if dfHouseholdComposition is None:
                            dfHouseholdComposition = df_
                        else:
                            dfHouseholdComposition = dfHouseholdComposition.merge(df_)
                    elif (df_.columns.isin(['Municipios', 'Superficie útil de la vivienda']).sum()==2):
                        if dfHouseholdArea is None:
                            dfHouseholdArea = df_
                        else:
                            dfHouseholdArea = dfHouseholdArea.merge(df_)

                    df_.to_csv("test.csv", index=False)


def INEMunicipalityNamesToMunicipalityCodes():

    df = pd.read_excel("https://www.ine.es/daco/daco42/codmun/diccionario24.xlsx", header=1)
    df['Municipality code'] = df['CPRO'].astype(int).apply(lambda x: f"{x:02d}") +\
                              df['CMUN'].astype(int).apply(lambda x: f"{x:03d}")
    df.rename(columns = {'NOMBRE':'Municipality name'}, inplace=True)
    df.drop(columns = ["CODAUTO","CPRO","CMUN","DC"],inplace=True)

    return df


def INEAggregatedElectricityConsumption(path,municipality_code = None):
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

        g_df.to_csv(filename,sep="\t", index=False)

    else:
        g_df = pd.read_csv(filename,sep="\t",dtype={0:str,1:str,2:str})

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    municipality = g_df[-pd.isna(g_df["Municipality code"]) & pd.isna(g_df["District code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["Municipality code"]) & -pd.isna(g_df["District code"])]
    districts = districts[districts.columns[districts.notna().any()]]

    return ({
        "Municipality": municipality,
        "Districts": districts
    })

def INECensus2021(path,municipality_code = None):
    DATA_CENSO2021 = "https://www.ine.es/censos2021/C2021_Indicadores.csv"

    censo_ingestion_urls = {
        'Tamaño del hogar': {
            'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/59543.csv?nocab=1',
            'by':'Municipio',
            'filter': lambda df: df.loc[(df['Municipality code'] != 'Total')],
            'columns': {
                'rename':{'1 persona':'Households with 1 person', '2 personas':'Households with 2 people','3 personas':'Households with 3 people', '4 personas':'Households of 4 people', '5 o más personas':'Households of 5 or more people','Total (tamaño del hogar)': 'Total Households'}
            }
        },
        'Tipo de vivienda (principal o no)': {
            'url': 'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/59525.csv?nocab=1',
            'by':'Municipio',
            'filter': lambda df: df.loc[(df['Municipality code'] != 'Total')],
            'columns': {
                'rename':{'Total':'Total Homes', 'Vivienda no principal':'Non-main Homes','Vivienda principal':'Main Homes'}
            }
        },
        'Edad en grandes grupos': {
            'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55242.csv',
            'by':'Municipio de residencia',
            'columns':{
                'aggregate':{
                    'Population': lambda df: df.sum(axis=1,numeric_only=True),
                    'Percentage of people between 16 (inclusive) and 64 (inclusive) years': lambda df: df['16-64']/ df['Population'],
                    'Percentage of people over 64 years of age': lambda df: df['65 o más']/ df['Population'],
                    'Percentage of people under 16 years': lambda df: df['Menos de 16']/ df['Population'],
                }
            },
            'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') &  (df['Nacionalidad (española/extranjera)'] == 'TOTAL')& (df['Sexo'] == 'Ambos sexos')],
        },
        'Sexo': {
            'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55242.csv',
            'by':'Municipio de residencia',
            'columns':{
                'aggregate':{
                    'Percentage of women': lambda df: df['Mujeres']/ df['Ambos sexos'],
                    'Percentage of men': lambda df: df['Hombres']/ df['Ambos sexos'],
                }
            },
            'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Edad en grandes grupos'] == 'TOTAL') & (df['Nacionalidad (española/extranjera)'] == 'TOTAL') ],
        },
        'Nacionalidad (española/extranjera)': {
            'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55242.csv',
            'by':'Municipio de residencia',
            'columns':{
                'aggregate':{
                    'Percentage foreigners': lambda df: df['Extranjera']/ df['TOTAL'],
                }
            },
            'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Edad en grandes grupos'] == 'TOTAL') & (df['Sexo'] == 'Ambos sexos') ],
        },
        'Unidades de medida': {
            'url':'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55245.csv?nocab=1',
            'by':'Municipio de residencia',
            'filter': lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Nacionalidad (española/extranjera)'] == 'TOTAL') & (df['Sexo'] == 'Ambos sexos')],
            'columns':{
                'rename':{'Edad media':'Average age'}
            },
        },
        'País de nacimiento (grandes grupos)': {
            'url': 'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55243.csv?nocab=1',
            'by':'Municipio de residencia',
            'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Sexo'] == 'Ambos sexos') ],
            'columns': {
                'aggregate':{'Percentage of people born abroad': lambda df: 1 - (df['España'] / df['TOTAL'])}
            },
            
        },
        'Nivel de estudios (grado)': {
            'url': 'https://www.ine.es/jaxi/files/tpx/en/csv_bdsc/55249.csv?nocab=1',
            'by':'Municipio de residencia',
            'filter':lambda df: df.loc[(df['Municipality code'] != 'Total') & (df['Nacionalidad (española/extranjera)'] == 'TOTAL') & (df['Sexo'] == 'Ambos sexos') ],
            'columns': {
                'aggregate':{'Percentage of people with higher education (esreal_cneda=08 09 10 11 12) on population aged 16 and over': lambda df: df['Educación Superior']/(df['TOTAL'] - df['No aplicable (menor de 15 años)'])}
            },

        } 
    }
    filename = f"{path}/df.tsv"


    if not os.path.exists(filename):
        print("Downloading Censo 2021..")
        # Downloading Censo 2021
        g_df = fetch_data(DATA_CENSO2021,separation=",",type=str)
        g_df['cmun'] = g_df['cpro'] + g_df['cmun']
        column_names = {'cmun':'Municipality code','dist':'District code', 'secc': 'Section code', 't1_1': 'Total People', 't2_1': 'Percentage of women', 't2_2': 'Percentage of men', 't3_1': 'Average age', 't4_1': 'Percentage of people under 16 years', 't4_2': 'Percentage of people between 16 (inclusive) and 64 (inclusive) years', 't4_3': 'Percentage of people over 64 years of age', 't5_1': 'Percentage foreigners', 't6_1': 'Percentage of people born abroad', 't7_1': 'Percentage of people pursuing higher education (escur =08 09 10 11 12 ) of the population aged 16 and over', 't8_1': 'Percentage of people pursuing university studies ( escur = 09 10 11 12) on population aged 16 and over', 't9_1': 'Percentage of people with higher education (esreal_cneda=08 09 10 11 12) on population aged 16 and over', 't10_1': 'Percentage of population unemployment over active population= Unemployed /Active', 't11_1': 'Percentage of employed population over population aged 16 and over =Employed/ Population 16 and +', 't12_1': 'Percentage of active population over population aged 16 and over= Active / Population 16 and +', 't13_1': 'Percentage of disability pensioner population over population aged 16 and over = Disability pensioners / Population 16 and +', 't14_1': 'Percentage of retirement pensioner population over population 16 and over=Retirement pensioners / Population 16 and +', 't15_1': 'Percentage of population in another situation of inactivity over population 16 and over=Population in another situation of inactivity / Population 16 and +', 't16_1' : 'Percentage of student population over population 16 and over = Students / Population 16 and +', 't17_1': 'Percentage of people with single marital status', 't17_2': 'Percentage of people with married marital status', 't17_3': 'Percentage of people with marital status widowed', 't17_4': 'Percentage of people for whom their marital status is not stated', 't17_5': 'Percentage of people with marital status legally separated or divorced', 't18_1': 'Total Homes', 't19_1': 'Main Homes', 't19_2': 'Non-main Homes', 't20_1': 'Owned Homes', 't20_2': 'Rental Homes', 't20_3' : 'Homes in another type of tenure regime', 't21_1': 'Total Households', 't22_1': 'Households with 1 person', 't22_2': 'Households with 2 people', 't22_3': 'Households with 3 people', 't22_4': 'Households of 4 people', 't22_5': 'Households of 5 or more people'}
        g_df.rename(columns=column_names,inplace=True)
        g_df.drop(columns=['ccaa','cpro'],inplace=True)

        # Integrating data sources at municipal level to fill the missing information (1363 rows). This can be done since all the municipalities with missing values were found to have unique districts.
        for x in censo_ingestion_urls:
            data= fetch_data(censo_ingestion_urls[x]['url'])
            data['Municipality code'] = data[censo_ingestion_urls[x]['by']].str[:5]
            data = censo_ingestion_urls[x]['filter'](data)
            data = data.pivot(index=['Municipality code'], columns=x, values='Total').reset_index()
            for op_code, operations in censo_ingestion_urls[x]['columns'].items():
                operation_dict.get(op_code)(data,operations)
            
            # Fill missing values (data ingestion)
            g_df = g_df.set_index('Municipality code').fillna(data.set_index('Municipality code')).reset_index()

        g_df.to_csv(filename,sep="\t", index=False)

    else:
        g_df = pd.read_csv(filename,sep="\t",dtype={0:str,1:str,2:str})

    if municipality_code is not None:
        if type(municipality_code) == str:
            g_df = g_df[(g_df["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            g_df = g_df[g_df["Municipality code"].isin(municipality_code)]

    g_df["Country code"] = "ES"
    g_df["Province code"] = g_df["Municipality code"].str[:2]

    municipality = g_df[pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = g_df[-pd.isna(g_df["District code"]) & pd.isna(g_df["Section code"])]
    districts = districts[districts.columns[districts.notna().any()]]
    sections = g_df[-pd.isna(g_df["District code"]) & -pd.isna(g_df["Section code"])]
    sections = sections[sections.columns[sections.notna().any()]]

    return ({
        "Municipality": municipality,
        "Districts": districts,
        "Sections": sections
    })

def INEHouseholdsRentalPriceIndex(path,municipality_code = None):
    filename = f"{path}/df.tsv"

    if not os.path.exists(filename):
        r = requests.get("https://www.ine.es/jaxiT3/files/t/es/csv_bd/59061.csv?nocab=1")
        r.encoding = 'utf-8'
        df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8")
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
        df_ = pd.read_csv(filename, sep="\t")

    if municipality_code is not None:
        if type(municipality_code) == str:
            df_ = df_[(df_["Municipality code"] == municipality_code).values]
        elif type(municipality_code) == list:
            df_ = df_[df_["Municipality code"].isin(municipality_code)]

    df_["Country code"] = "ES"
    df_["Province code"] = df_["Municipality code"].str[:2]

    municipality = df_[-pd.isna(df_["Municipality code"]) & pd.isna(
        df_["District code"])]
    municipality = municipality[municipality.columns[municipality.notna().any()]]
    districts = df_[-pd.isna(df_["Municipality code"]) & -pd.isna(df_["District code"])]
    districts = districts[districts.columns[districts.notna().any()]]

    return ({
        "Municipality": municipality,
        "Districts": districts
    })

def INEConsumerPriceIndex(path):

    filename = f"{path}/df.tsv"


    if not os.path.exists(filename):
        r = requests.get("https://www.ine.es/jaxiT3/files/t/es/csv_bd/23708.csv?nocab=1")
        r.encoding = 'utf-8'
        df_ = pd.read_csv(StringIO(r.text), sep="\t", encoding="utf-8")
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
        df_ = pd.read_csv(filename, sep="\t")

    return ({
        "National": df_
    })