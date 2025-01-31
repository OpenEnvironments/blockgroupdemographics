# blockgroupdemographics
A selection of variables from the US Census Bureau's American Community Survey 5YR and TIGER/Line publications.

## Overview
---
The U.S. Census Bureau published it's American Community Survey 5 Year with more than 37,000 variables. Most ACS advanced users will have their personal list of favorites, but this conventional wisdom is not available to occasional analysts. This publication re-shares 174 select demographic data from the U.S. Census Bureau to provide an supplement to Open Environments Block Group publications. These results do not reflect any proprietary or predictive model. Rather, they extract from Census Bureau results. For additional support or more detail, please see the Census Bureau citations below.

The first 170 demographic variables are taken from popular variables in the American Community Survey (ACS) including age, race, income, education and family structure. A full list of ACS variable names and definitions can be found in the ACS 'Table Shells' here https://www.census.gov/programs-surveys/acs/technical-documentation/table-shells.html.

The dataset includes 4 additional columns from the Census' TIGER/Line publication. See Open Environment's **2023blockgroupcartographics** publication for the shapes of each block group. For each block group, the dataset includes land area (ALAND), water area (AWATER), interpolated latitude (INTPTLAT) and longitude (INTPTLON). These are valuable for calculating population density variables which combine ACS populations and TIGER land area.

## Files
The resulting dataset is available with other block group based datasets on Harvard's Dataverse https://dataverse.harvard.edu/ in Open Environment's Block Group Dataverse https://dataverse.harvard.edu/dataverse/blockgroupdatasets/.

This data simply requires csv reader software or pythons pandas package. 

Supporting the data file, is **acsvars.csv**, a list of the Census variable names and their corresponding description. 

## Citations
---
“American Community Survey 5-Year Data (2019-2023).” Census.gov, US Census Bureau, https://www.census.gov/data/developers/data-sets/acs-5year.html. 2023 

"American Community Survey, Table Shells and Table List” Census.gov, US Census Bureau, https://www.census.gov/programs-surveys/acs/technical-documentation/table-shells.html

Python Package Index - PyPI. Python Software Foundation. "A simple wrapper for the United States Census Bureau’s API.". Retrieved from https://pypi.org/project/census/
