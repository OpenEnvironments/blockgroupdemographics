# blockgroupdemographics
A combination of the TIGER/Line and ACS 5YR publications from the US Census Bureau.

## Overview
This progran combines geographic and demographic data from the U.S. Census Bureau 
to provide an obvious supplement to Open Environments Block Group publications.
These results do not reflect any proprietary or predictive model. Rather, they are
Census Bureau results with some proportions and aggregation rules applied. For additional
support or more detail, please see the Census Bureau citations below.

Geographics refer to shapefiles shared in the Census TIGER/Line publications. Block
Group areas are updated annually, with major revisions accompanying the Decennial Census
at the turn of each decade. These shapes are useful for visualizing estimates as a
map and relating geographics based upon geo-operations like overlapping. This data is
kept in a geodatabase file format and requires the geopandas package and its supporting
fiona and DAL software.

Demographics are taken from popular variables in the American Community Survey (ACS)
including age, race, income, education and family structure. This data simply requires
csv reader software or pythons pandas package.

More details on the ACS variables selected and derivation rules applied can be found in
the commentary docstrings of the get_demogs() and combine_derive() functions below.

## Citations:
---
  “TIGER/Line and TIGER-Related Products Electronic Resource: TIGER, Topologically Integrated Geographic Encoding and Referencing System.” Index of /Geo/Tiger/TIGER2019/BG, U.S. Census Bureau, 10 Feb. 2022, https://www2.census.gov/geo/tiger/TIGER2019/BG/. 
  “American Community Survey 5-Year Data (2009-2020).” Census.gov, US Census Bureau, 8 Mar. 2022, https://www.census.gov/data/developers/data-sets/acs-5year.html. 

