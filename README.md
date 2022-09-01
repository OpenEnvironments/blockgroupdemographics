# blockgroupdemographics
A combination of the TIGER/Line and ACS 5YR publications from the US Census Bureau.

"""
# blockgroupdemographics
## Overview
---
This progran re-shares cartographic and demographic data from the U.S. Census Bureau 
to provide an obvious supplement to Open Environments Block Group publications.
These results do not reflect any proprietary or predictive model. Rather, they extract from
Census Bureau results with some proportions and aggregation rules applied. For additional
support or more detail, please see the Census Bureau citations below.

Cartographics refer to shapefiles shared in the Census TIGER/Line publications. Block
Group areas are updated annually, with major revisions accompanying the Decennial Census
at the turn of each decade. These shapes are useful for visualizing estimates as a
map and relating geographies based upon geo-operations like overlapping. This data is
kept in a geodatabase file format and requires the geopandas package and its supporting
fiona and DAL software.

Demographics are taken from popular variables in the American Community Survey (ACS)
including age, race, income, education and family structure. This data simply requires
csv reader software or pythons pandas package.

## Files
While the demographic data has many columns, the cartographic data has a very, very 
large column called "geometry" storing the many-point boundaries of each shape. So,
this process saves the data separately, with demographics columns in a csv file named 
YYYYblcokgroupdemographics.csv. The cartographic column, 'geometry', is shared as 
file named YYYYblockgroupdemographics-geometry.pkl. This file needs an installation 
of geopandas, fiona and DAL software.

More details on the ACS variables selected and derivation rules applied can be found in
the commentary docstrings of the functions below.

## Demonstration
```
import pandas as pd
import numpy as np
import geopandas as gpd
import geoplot

# The Block Group Voting dataset
bgv = pd.read_csv('D:\\Open Environments\\data\\Open Environments\\blockgroupvoting\\2019\\2019blockgroupvoting.csv',
                 converters={'BLOCKGROUP_GEOID': '{:0>12}'.format})
# This demographic and  derived dataset
bgd = pd.read_csv('C:\\Users\\michael\\Documents\\2019blockgroupdemographics.csv',
                 converters={'GEOID': '{:0>12}'.format}, index=False)
# The cartographic shapes of each block group
bgc = gpd.read_picle('C:\\Users\\michael\\Documents\\2019blockgroupdemographics-geometry.pkl')

# What proportion of voters voted Republican in the 2020 election
mix1 = pd.merge(bgc,bgv, left_on='GEOID', right_on="BLOCKGROUP_GEOID",  how='left')
mix2 = pd.merge(mix1,bgd, on='GEOID', how='left')
mix2["RepRate"] = mix2.REP / (mix2.REP + mix2.DEM)

geoplot.choropleth(mix2[~mix2.STATE.isin(["HI","AK"])],
                   hue="RepRate", cmap="Reds", 
                   figsize=(15,7), legend=True,
                   linewidth=0)
```

## Citations:
---
  “TIGER/Line and TIGER-Related Products Electronic Resource: TIGER, Topologically Integrated Geographic Encoding and Referencing System.” Index of /Geo/Tiger/TIGER2019/BG, U.S. Census Bureau, 10 Feb. 2022, https://www2.census.gov/geo/tiger/TIGER2019/BG/. 
  “American Community Survey 5-Year Data (2009-2020).” Census.gov, US Census Bureau, 8 Mar. 2022, https://www.census.gov/data/developers/data-sets/acs-5year.html. 
  Bryan, Michael, 2022, "U.S. Voting by Census Block Groups", https://doi.org/10.7910/DVN/NKNWBX, Harvard Dataverse, V3, UNF:6:OlQ9kJRJ1BDUEYRNlqusJA== [fileUNF]

