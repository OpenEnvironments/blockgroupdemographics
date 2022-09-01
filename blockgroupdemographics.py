#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
                 converters={'GEOID': '{:0>12}'.format})
# The cartographic shapes of each block group
bgc = pd.read_pickle('C:\\Users\\michael\\Documents\\2019blockgroupdemographics-geometry.pkl')

# What proportion of voters voted Republican in the 2020 election
mix1 = pd.merge(bgc,bgv, left_on='GEOID', right_on="BLOCKGROUP_GEOID",  how='left')
mix2 = pd.merge(mix1,bgd, on='GEOID', how='left')
mix2["RepRate"] = mix2.REP / (mix2.REP + mix2.DEM)

geoplot.choropleth(mix2[(~mix2.STATE.isin(["HI","AK"])) # exclude Alaska & Hawaii visually
                       & (mix2.B01001e1 < 5000)],       # exclude the extreme 1%
                   hue="B01001e1", cmap="Reds", 
                   figsize=(15,7), legend=True,
                   linewidth=0)
```

## Citations:
---
  “TIGER/Line and TIGER-Related Products Electronic Resource: TIGER, Topologically Integrated Geographic Encoding and Referencing System.” Index of /Geo/Tiger/TIGER2019/BG, U.S. Census Bureau, 10 Feb. 2022, https://www2.census.gov/geo/tiger/TIGER2019/BG/. 
  “American Community Survey 5-Year Data (2009-2020).” Census.gov, US Census Bureau, 8 Mar. 2022, https://www.census.gov/data/developers/data-sets/acs-5year.html. 
  Bryan, Michael, 2022, "U.S. Voting by Census Block Groups", https://doi.org/10.7910/DVN/NKNWBX, Harvard Dataverse, V3, UNF:6:OlQ9kJRJ1BDUEYRNlqusJA== [fileUNF]
"""

import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
np.seterr(divide = 'ignore') 
import psutil
import geopandas as gpd
import geoplot
import logging

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
fileHandler = logging.FileHandler("blockgroupdemographics.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
logging.basicConfig(level=logging.DEBUG)


def get_demogs(frompath):
    """
    This function retrieves the following major variables from the Census' American
    Community Survey, 5-Year Estimates available here
    https://www2.census.gov/geo/tiger/TIGER_DP/2019ACS/:
        B01003e1    Population total                        B19013e1    Median Household Income                 B02001e1    Race basis                          
        B01001e1    Population total (within Age Sex)       B19001e1    Income basis                            B02001e2    White alone                         
        B01001e2    Male                                    B19001e2    Less than $10 000                       B02001e3    Black or African American alone     
        B01001e3    Male Under 5 years                      B19001e3    $10 000 to $14 999                      B02001e4    American Indian and Alaskative alone
        B01001e4    Male 5 to 9 years                       B19001e4    $15 000 to $19 999                      B02001e5    Asian alone                         
        B01001e5    Male 10 to 14 years                     B19001e5    $20 000 to $24 999                      B02001e6    Native Hawaiian and Other Pacific Is
        B01001e6    Male 15 to 17 years                     B19001e6    $25 000 to $29 999                      B02001e7    Some other race alone               
        B01001e7    Male 18 and 19 years                    B19001e7    $30 000 to $34 999                      B02001e8    Two or more races                   
        B01001e8    Male 20 years                           B19001e8    $35 000 to $39 999                      B03003e1    Hispanic basis                      
        B01001e9    Male 21 years                           B19001e9    $40 000 to $44 999                      B03003e2    Not Hispanic basis                  
        B01001e10   Male 22 to 24 years                     B19001e10   $45 000 to $49 999                      B03003e3    Hispanic or Latino basis            
        B01001e11   Male 25 to 29 years                     B19001e11   $50 000 to $59 999                      B11001e1    Household Type basis                
        B01001e12   Male 30 to 34 years                     B19001e12   $60 000 to $74 999                      B11001e2    Family Households                   
        B01001e13   Male 35 to 39 years                     B19001e13   $75 000 to $99 999                      B11001e7    Nonfamily Households                
        B01001e14   Male 40 to 44 years                     B19001e14   $100 000 to $124 999                    B23025e1    Employment Status basis             
        B01001e15   Male 45 to 49 years                     B19001e15   $125 000 to $149 999                    B23025e2    Employment in the labor force       
        B01001e16   Male 50 to 54 years                     B19001e16   $150 000 to $199 999                    B23025e7    Employment not in the labor force   
        B01001e17   Male 55 to 59 years                     B19001e17   $200 000 or more                        B09019e1    Household basis for Presence of Chil
        B01001e18   Male 60 and 61 years                    B15003e1    Education attainment basis              B09018e1    Presence of children                
        B01001e19   Male 62 to 64 years                     B15003e2    No schooling completed                  
        B01001e20   Male 65 and 66 years                    B15003e3    Nursery school                          
        B01001e21   Male 67 to 69 years                     B15003e4    Kindergarten                            
        B01001e22   Male 70 to 74 years                     B15003e5    1st grade                               
        B01001e23   Male 75 to 79 years                     B15003e6    2nd grade                               
        B01001e24   Male 80 to 84 years                     B15003e7    3rd grade                               
        B01001e25   Male 85 years and over                  B15003e8    4th grade                               
        B01001e26   Female                                  B15003e9    5th grade                               
        B01001e27   Female Under 5 years                    B15003e10   6th grade                               
        B01001e28   Female 5 to 9 years                     B15003e11   7th grade                               
        B01001e29   Female 10 to 14 years                   B15003e12   8th grade                               
        B01001e30   Female 15 to 17 years                   B15003e13   9th grade                               
        B01001e31   Female 18 and 19 years                  B15003e14   10th grade                              
        B01001e32   Female 20 years                         B15003e15   11th grade                              
        B01001e33   Female 21 years                         B15003e16   12th grade no diploma                   
        B01001e34   Female 22 to 24 years                   B15003e17   Regular high school diploma             
        B01001e35   Female 25 to 29 years                   B15003e18   GED or alternative credential           
        B01001e36   Female 30 to 34 years                   B15003e19   Some college less than 1 year           
        B01001e37   Female 35 to 39 years                   B15003e20   Some college 1 or more years no degr    
        B01001e38   Female 40 to 44 years                   B15003e21   Associates degree                       
        B01001e39   Female 45 to 49 years                   B15003e22   Bachelors degree                        
        B01001e40   Female 50 to 54 years                   B15003e23   Masters degree                          
        B01001e41   Female 55 to 59 years                   B15003e24   Professional school degree              
        B01001e42   Female 60 and 61 years                  B15003e25   Doctorate degree                        
        B01001e43   Female 62 to 64 years                       
        B01001e44   Female 65 and 66 years                  ALAND       Land area of the block group in square meters
        B01001e45   Female 67 to 69 years                   AWATER      Water area of the block group in square meters        
        B01001e46   Female 70 to 74 years                   INTPTLAT    Longitude of the internal point (centroid)
        B01001e47   Female 75 to 79 years                   INTPTLON    Latitude of the internal point (centroid)
        B01001e48   Female 80 to 84 years                       
        B01001e49   Female 85 years and over                    
    """
    print("Pulling ACS demographics:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    # initialize
    varlist = ['X01_AGE_AND_SEX.B01003e1','X01_AGE_AND_SEX.B01001e1','X01_AGE_AND_SEX.B01001e2','X01_AGE_AND_SEX.B01001e3','X01_AGE_AND_SEX.B01001e4','X01_AGE_AND_SEX.B01001e5','X01_AGE_AND_SEX.B01001e6','X01_AGE_AND_SEX.B01001e7','X01_AGE_AND_SEX.B01001e8','X01_AGE_AND_SEX.B01001e9','X01_AGE_AND_SEX.B01001e10','X01_AGE_AND_SEX.B01001e11','X01_AGE_AND_SEX.B01001e12','X01_AGE_AND_SEX.B01001e13','X01_AGE_AND_SEX.B01001e14','X01_AGE_AND_SEX.B01001e15','X01_AGE_AND_SEX.B01001e16','X01_AGE_AND_SEX.B01001e17','X01_AGE_AND_SEX.B01001e18','X01_AGE_AND_SEX.B01001e19','X01_AGE_AND_SEX.B01001e20','X01_AGE_AND_SEX.B01001e21','X01_AGE_AND_SEX.B01001e22','X01_AGE_AND_SEX.B01001e23','X01_AGE_AND_SEX.B01001e24','X01_AGE_AND_SEX.B01001e25','X01_AGE_AND_SEX.B01001e26','X01_AGE_AND_SEX.B01001e27','X01_AGE_AND_SEX.B01001e28','X01_AGE_AND_SEX.B01001e29','X01_AGE_AND_SEX.B01001e30','X01_AGE_AND_SEX.B01001e31','X01_AGE_AND_SEX.B01001e32','X01_AGE_AND_SEX.B01001e33','X01_AGE_AND_SEX.B01001e34','X01_AGE_AND_SEX.B01001e35','X01_AGE_AND_SEX.B01001e36','X01_AGE_AND_SEX.B01001e37','X01_AGE_AND_SEX.B01001e38','X01_AGE_AND_SEX.B01001e39','X01_AGE_AND_SEX.B01001e40','X01_AGE_AND_SEX.B01001e41','X01_AGE_AND_SEX.B01001e42','X01_AGE_AND_SEX.B01001e43','X01_AGE_AND_SEX.B01001e44','X01_AGE_AND_SEX.B01001e45','X01_AGE_AND_SEX.B01001e46','X01_AGE_AND_SEX.B01001e47','X01_AGE_AND_SEX.B01001e48','X01_AGE_AND_SEX.B01001e49','X19_INCOME.B19013e1','X19_INCOME.B19001e1','X19_INCOME.B19001e2','X19_INCOME.B19001e3','X19_INCOME.B19001e4','X19_INCOME.B19001e5','X19_INCOME.B19001e6','X19_INCOME.B19001e7','X19_INCOME.B19001e8','X19_INCOME.B19001e9','X19_INCOME.B19001e10','X19_INCOME.B19001e11','X19_INCOME.B19001e12','X19_INCOME.B19001e13','X19_INCOME.B19001e14','X19_INCOME.B19001e15','X19_INCOME.B19001e16','X19_INCOME.B19001e17','X15_EDUCATIONAL_ATTAINMENT.B15003e1','X15_EDUCATIONAL_ATTAINMENT.B15003e2','X15_EDUCATIONAL_ATTAINMENT.B15003e3','X15_EDUCATIONAL_ATTAINMENT.B15003e4','X15_EDUCATIONAL_ATTAINMENT.B15003e5','X15_EDUCATIONAL_ATTAINMENT.B15003e6','X15_EDUCATIONAL_ATTAINMENT.B15003e7','X15_EDUCATIONAL_ATTAINMENT.B15003e8','X15_EDUCATIONAL_ATTAINMENT.B15003e9','X15_EDUCATIONAL_ATTAINMENT.B15003e10','X15_EDUCATIONAL_ATTAINMENT.B15003e11','X15_EDUCATIONAL_ATTAINMENT.B15003e12','X15_EDUCATIONAL_ATTAINMENT.B15003e13','X15_EDUCATIONAL_ATTAINMENT.B15003e14','X15_EDUCATIONAL_ATTAINMENT.B15003e15','X15_EDUCATIONAL_ATTAINMENT.B15003e16','X15_EDUCATIONAL_ATTAINMENT.B15003e17','X15_EDUCATIONAL_ATTAINMENT.B15003e18','X15_EDUCATIONAL_ATTAINMENT.B15003e19','X15_EDUCATIONAL_ATTAINMENT.B15003e20','X15_EDUCATIONAL_ATTAINMENT.B15003e21','X15_EDUCATIONAL_ATTAINMENT.B15003e22','X15_EDUCATIONAL_ATTAINMENT.B15003e23','X15_EDUCATIONAL_ATTAINMENT.B15003e24','X15_EDUCATIONAL_ATTAINMENT.B15003e25','X02_RACE.B02001e1','X02_RACE.B02001e2','X02_RACE.B02001e3','X02_RACE.B02001e4','X02_RACE.B02001e5','X02_RACE.B02001e6','X02_RACE.B02001e7','X02_RACE.B02001e8','X03_HISPANIC_OR_LATINO_ORIGIN.B03003e1','X03_HISPANIC_OR_LATINO_ORIGIN.B03003e2','X03_HISPANIC_OR_LATINO_ORIGIN.B03003e3','X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e1','X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e2','X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e7','X23_EMPLOYMENT_STATUS.B23025e1','X23_EMPLOYMENT_STATUS.B23025e2','X23_EMPLOYMENT_STATUS.B23025e7','X09_CHILDREN_HOUSEHOLD_RELATIONSHIP.B09019e1','X09_CHILDREN_HOUSEHOLD_RELATIONSHIP.B09018e1',
              'ACS_2019_5YR_BG.ALAND', 'ACS_2019_5YR_BG.AWATER', 'ACS_2019_5YR_BG.INTPTLAT', 'ACS_2019_5YR_BG.INTPTLON']
    acs = gpd.read_file(frompath,
          layer = frompath[frompath.rfind("/")+1:frompath.rfind(".")])[["GEOID","geometry"]] 
    acs["GEOID"] = acs.GEOID.str[-12:]  # original formats GEOID like 15000US721537506022
    # Open each layer, then collect the variables in it
    for l in set([v[:v.index(".")] for v in varlist]):  # Unique layers in the var list
        print("    Opening layer",l)
        layercols = [c[c.index('.')+1:] for c in varlist if c[:c.index('.')] == l]
        layercols.extend(["GEOID"])
        layercombined = gpd.read_file(frompath, layer = l)[layercols]
        layercombined["GEOID"] = layercombined.GEOID.str[-12:]  # original formats GEOID like 15000US721537506022
        acs = acs.merge(layercombined, on='GEOID', how='left')
    return acs

def derive_elements(df):
    """
    This function accepts dataframes with ACS and TIGER Line shapes, combines them
    on Block Group geoids, then adds derivations.
    
    :param  acs, tiger: dataframes, keyed on 12 digit block group GEOID
    :return df: dataframe with the inputs merged columnwise with these
            derivations applied:
            
        Over65Rate        proportion of population with age over 65
        MinorityRate      proportion of population that has race other than White Alone
        PopDensity        population per square meter of land in the Block Group
        CollegePlusRate   proportion of population with at least a college degree
        EmploymentRate    proportion of employed population to total population
        FamilyRate        proportion of households that are Family (rather than non-family)
        ChildrenRate      proportion of households with children present
        Under25KRate      proportion of households with income under $25K
        logPop            natural log of total population
        logPopDensity     natural log of population density
        logLand           natural log of the land area (sq meters) of the Block Group
    """
    print("Combining and calculating derivations:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    df['Over65Rate'] = (df['B01001e20'] + df['B01001e21'] + df['B01001e22'] + df['B01001e23'] + df['B01001e24'] + df['B01001e25'] + df['B01001e44'] + df['B01001e45'] + df['B01001e46'] + df['B01001e47'] + df['B01001e48'] + df['B01001e49']) / (df['B01001e2'] + df['B01001e26'])
    df['MinorityRate'] = 1 - (df['B02001e2'] / df['B02001e1'])
    df['PopDensity'] = df['B01001e1'] / (df['ALAND'] + df['AWATER'])
    df['CollegePlusRate'] = (df['B15003e21'] + df['B15003e22'] + df['B15003e23'] + df['B15003e24'] + df['B15003e25']) / df['B15003e1']
    df['EmploymentRate'] = df['B23025e2'] / df['B23025e1']
    df['FamilyRate'] = df['B11001e2'] / df['B11001e1']
    df['ChildrenRate'] = df['B09018e1'] / df['B09019e1']
    df['Under25KRate'] = (df['B19001e2'] + df['B19001e3'] + df['B19001e4'] + df['B19001e5']) / df['B19001e1']
    df['logPop'] = np.log(df.B01001e1)
    df['logPopDensity'] = np.log(df.PopDensity)
    df['logLand'] = np.log(df.ALAND)
    return df

def put_results(df, fn):
    """
    This function accepts a geodataframe and filename prefix
    to generate a zipped CSV file (.zip) pandas pickle file (.pkl)
    with the filename prefix.
    """
    print("Writing to files:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    df.drop("geometry",axis=1).to_csv(fn+'.csv', index=False)
    df[["GEOID","geometry"]].to_pickle(fn+"-geometry.pkl") 
    return

if __name__ == "__main__":
    # This run refers to 2019 and my local file paths; replace as appropriate 
    print("Starting:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    acs = get_demogs("D:/Open Environments/data/census/acs/acs5/ACS_2019_5YR_BG.gdb")
    complete = derive_elements(acs)
    put_results(complete,'2019blockgroupdemographics')
    print("Done:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
