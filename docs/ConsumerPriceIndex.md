# `ConsumerPriceIndex`

**Consumer price index (2015 base)**

Monthly CPI for Spain on the 2015 base, broken down by COICOP consumption class: the general index alongside food and drink, tobacco, clothing, housing costs (rent, electricity, gas, water), household goods, health, transport, communications, recreation, education, restaurants and hotels, and other services.

**Source:** [Índice de Precios de Consumo, base 2015 (INE)](https://www.ine.es/dyngs/INEbase/en/operacion.htm?c=Estadistica_C&cid=1254736176802&menu=ultiDatos&idp=1254735976607)

```python
INE.ConsumerPriceIndex(wd, years=None)
```

## What it returns

| Key | Rows | Columns | Years |
|---|---:|---:|---|
| `National` | 348 | 104 | 1997–2025 |

## Parameters

```
wd : str
    Working directory the downloaded data is cached under. The first call
    downloads from INE, later ones read the local copy.
years : list of int, optional
    Restrict the result to these years.
```

## Notes

- National only — INE publishes the regional breakdown as a separate operation.
- Rows are one per year and month, which is what makes this the deflator for the nominal money in `HouseholdIncomeDistributionAtlas` and the two price indices.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

cpi = INE.ConsumerPriceIndex(wd=wd, years=[2023, 2024])
cpi["National"][["Year", "Month", "General index"]]
```

## Reference

<details><summary>Columns of `National` (104)</summary>

- `Country code`
- `Year`
- `Month`
- `CPI 2015 base ~ Class:0111 Bread and cereals`
- `CPI 2015 base ~ Class:0112 Meat`
- `CPI 2015 base ~ Class:0113 Fish and seafood`
- `CPI 2015 base ~ Class:0114 Milk, cheese and eggs`
- `CPI 2015 base ~ Class:0115 Oils and fats`
- `CPI 2015 base ~ Class:0116 Fruits`
- `CPI 2015 base ~ Class:0117 Pulses and vegetables`
- `CPI 2015 base ~ Class:0118 Sugar, jam, honey, chocolate and confectionery`
- `CPI 2015 base ~ Class:0119 Other food products`
- `CPI 2015 base ~ Class:0121 Coffee, tea and cocoa`
- `CPI 2015 base ~ Class:0122 Mineral waters, soft drinks, fruit and vegetable juices`
- `CPI 2015 base ~ Class:0211 Distilled beverages`
- `CPI 2015 base ~ Class:0212 Wine`
- `CPI 2015 base ~ Class:0213 Beer`
- `CPI 2015 base ~ Class:0220 Tobacco`
- `CPI 2015 base ~ Class:0312 Clothing`
- `CPI 2015 base ~ Class:0313 Other articles of clothing and haberdashery`
- `CPI 2015 base ~ Class:0314 Cleaning, repair and hire of clothing`
- `CPI 2015 base ~ Class:0321 Footwear`
- `CPI 2015 base ~ Class:0322 Repair and hire of footwear`
- `CPI 2015 base ~ Class:0411 Renting of main dwelling `
- `CPI 2015 base ~ Class:0412 Other rentals`
- `CPI 2015 base ~ Class:0431 Materials for the maintenance and repair of the dwelling`
- `CPI 2015 base ~ Class:0432 Services for the maintenance and repair of the dwelling`
- `CPI 2015 base ~ Class:0441 Water supply`
- `CPI 2015 base ~ Class:0442 Refuse collection`
- `CPI 2015 base ~ Class:0443 Sewerage`
- `CPI 2015 base ~ Class:0444 Other services related to housing`
- `CPI 2015 base ~ Class:0451 Electricity`
- `CPI 2015 base ~ Class:0452 Gas`
- `CPI 2015 base ~ Class:0453 Liquid fuels`
- `CPI 2015 base ~ Class:0511 Furniture and furnishings`
- `CPI 2015 base ~ Class:0512 Carpets and other floor coverings`
- `CPI 2015 base ~ Class:0520 Household textiles`
- `CPI 2015 base ~ Class:0531 Major household appliances, electric or otherwise`
- `CPI 2015 base ~ Class:0532 Small household appliances`
- `CPI 2015 base ~ Class:0533 Repair of household appliances`
- `CPI 2015 base ~ Class:0540 Glassware, tableware and household utensils`
- `CPI 2015 base ~ Class:0551 Large tools and equipment`
- `CPI 2015 base ~ Class:0552 Small tools and accessories`
- `CPI 2015 base ~ Class:0561 Non-durable household goods`
- `CPI 2015 base ~ Class:0562 Domestic and other household services`
- `CPI 2015 base ~ Class:0611 Pharmaceutical products`
- `CPI 2015 base ~ Class:0612 Other medical products`
- `CPI 2015 base ~ Class:0613 Therapeutic appliances and equipment`
- `CPI 2015 base ~ Class:0621 Medical services`
- `CPI 2015 base ~ Class:0622 Dental services`
- `CPI 2015 base ~ Class:0623 Paramedical services`
- `CPI 2015 base ~ Class:0630 Hospital services`
- `CPI 2015 base ~ Class:0711 Motor vehicles`
- `CPI 2015 base ~ Class:0712 Motorcycles`
- `CPI 2015 base ~ Class:0713 Bicycles`
- `CPI 2015 base ~ Class:0721 Spare parts and accessories for personal vehicles`
- `CPI 2015 base ~ Class:0722 Fuels and lubricants for personal vehicles`
- `CPI 2015 base ~ Class:0723 Maintenance and repair of personal motor vehicles`
- `CPI 2015 base ~ Class:0724 Other services relating to personal motor vehicles`
- `CPI 2015 base ~ Class:0731 Passenger transport by rail`
- `CPI 2015 base ~ Class:0732 Passenger transport by road`
- `CPI 2015 base ~ Class:0733 Passenger transport by air`
- `CPI 2015 base ~ Class:0734 Passenger transport by sea and inland waterways`
- `CPI 2015 base ~ Class:0735 Combined passenger transport`
- `CPI 2015 base ~ Class:0736 Other transport services`
- `CPI 2015 base ~ Class:0810 Postal services`
- `CPI 2015 base ~ Class:0820 Telephone and facsimile equipment`
- `CPI 2015 base ~ Class:0830 Telephone and facsimile services`
- `CPI 2015 base ~ Class:0911 Equipment for the reception, recording and reproduction of sound and images`
- `CPI 2015 base ~ Class:0912 Photographic and cinematographic equipment and optical instruments`
- `CPI 2015 base ~ Class:0913 Information processing equipment`
- `CPI 2015 base ~ Class:0914 Image, sound and data media`
- `CPI 2015 base ~ Class:0922 Musical instruments and major durables for indoor entertainment`
- `CPI 2015 base ~ Class:0931 Games, toys and hobbies`
- `CPI 2015 base ~ Class:0932 Equipment for sports, camping and outdoor recreation`
- `CPI 2015 base ~ Class:0933 Gardening, plants and flowers`
- `CPI 2015 base ~ Class:0934 Pets and related products`
- `CPI 2015 base ~ Class:0935 Veterinary and other services for domestic animals`
- `CPI 2015 base ~ Class:0941 Recreational and sporting services`
- `CPI 2015 base ~ Class:0942 Cultural services`
- `CPI 2015 base ~ Class:0951 Books`
- `CPI 2015 base ~ Class:0952 Press`
- `CPI 2015 base ~ Class:0954 Stationery and drawing materials`
- `CPI 2015 base ~ Class:0960 Package tours`
- `CPI 2015 base ~ Class:1010 Pre-primary and primary education`
- `CPI 2015 base ~ Class:1020 Secondary education`
- `CPI 2015 base ~ Class:1040 Higher education`
- `CPI 2015 base ~ Class:1050 Education not defined by level`
- `CPI 2015 base ~ Class:1111 Catering`
- `CPI 2015 base ~ Class:1112 Canteens`
- `CPI 2015 base ~ Class:1120 Accommodation services`
- `CPI 2015 base ~ Class:1211 Hairdressing and beauty parlours`
- `CPI 2015 base ~ Class:1212 Electrical appliances for personal care`
- `CPI 2015 base ~ Class:1213 Other appliances, articles and products for personal care`
- `CPI 2015 base ~ Class:1231 Jewellery, costume jewellery and watches`
- `CPI 2015 base ~ Class:1232 Other personal effects`
- `CPI 2015 base ~ Class:1240 Social protection`
- `CPI 2015 base ~ Class:1252 Insurance related to housing`
- `CPI 2015 base ~ Class:1253 Health-related insurance`
- `CPI 2015 base ~ Class:1254 Transport related insurance`
- `CPI 2015 base ~ Class:1255 Other insurance`
- `CPI 2015 base ~ Class:1262 Other financial services`
- `CPI 2015 base ~ Class:1270 Other services`
- `CPI 2015 base ~ Class:General`

</details>


---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
