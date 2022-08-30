#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
# blockgroupdemographics
## Overview
---
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

"""

import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
np.seterr(divide = 'ignore') 
import psutil
import geopandas as gpd
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

print("Starting:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))

def get_demogs(frompath):
    """
    This function retrieves the following major variables from the Census' American
    Community Survey, 5-Year Estimates:
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
        B01001e44   Female 65 and 66 years                      
        B01001e45   Female 67 to 69 years                       
        B01001e46   Female 70 to 74 years                       
        B01001e47   Female 75 to 79 years                       
        B01001e48   Female 80 to 84 years                       
        B01001e49   Female 85 years and over                    
    """
    print("Pulling ACS demographics:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    # initialize
    varlist = ['X01_AGE_AND_SEX.B01003e1','X01_AGE_AND_SEX.B01001e1','X01_AGE_AND_SEX.B01001e2','X01_AGE_AND_SEX.B01001e3','X01_AGE_AND_SEX.B01001e4','X01_AGE_AND_SEX.B01001e5','X01_AGE_AND_SEX.B01001e6','X01_AGE_AND_SEX.B01001e7','X01_AGE_AND_SEX.B01001e8','X01_AGE_AND_SEX.B01001e9','X01_AGE_AND_SEX.B01001e10','X01_AGE_AND_SEX.B01001e11','X01_AGE_AND_SEX.B01001e12','X01_AGE_AND_SEX.B01001e13','X01_AGE_AND_SEX.B01001e14','X01_AGE_AND_SEX.B01001e15','X01_AGE_AND_SEX.B01001e16','X01_AGE_AND_SEX.B01001e17','X01_AGE_AND_SEX.B01001e18','X01_AGE_AND_SEX.B01001e19','X01_AGE_AND_SEX.B01001e20','X01_AGE_AND_SEX.B01001e21','X01_AGE_AND_SEX.B01001e22','X01_AGE_AND_SEX.B01001e23','X01_AGE_AND_SEX.B01001e24','X01_AGE_AND_SEX.B01001e25','X01_AGE_AND_SEX.B01001e26','X01_AGE_AND_SEX.B01001e27','X01_AGE_AND_SEX.B01001e28','X01_AGE_AND_SEX.B01001e29','X01_AGE_AND_SEX.B01001e30','X01_AGE_AND_SEX.B01001e31','X01_AGE_AND_SEX.B01001e32','X01_AGE_AND_SEX.B01001e33','X01_AGE_AND_SEX.B01001e34','X01_AGE_AND_SEX.B01001e35','X01_AGE_AND_SEX.B01001e36','X01_AGE_AND_SEX.B01001e37','X01_AGE_AND_SEX.B01001e38','X01_AGE_AND_SEX.B01001e39','X01_AGE_AND_SEX.B01001e40','X01_AGE_AND_SEX.B01001e41','X01_AGE_AND_SEX.B01001e42','X01_AGE_AND_SEX.B01001e43','X01_AGE_AND_SEX.B01001e44','X01_AGE_AND_SEX.B01001e45','X01_AGE_AND_SEX.B01001e46','X01_AGE_AND_SEX.B01001e47','X01_AGE_AND_SEX.B01001e48','X01_AGE_AND_SEX.B01001e49','X19_INCOME.B19013e1','X19_INCOME.B19001e1','X19_INCOME.B19001e2','X19_INCOME.B19001e3','X19_INCOME.B19001e4','X19_INCOME.B19001e5','X19_INCOME.B19001e6','X19_INCOME.B19001e7','X19_INCOME.B19001e8','X19_INCOME.B19001e9','X19_INCOME.B19001e10','X19_INCOME.B19001e11','X19_INCOME.B19001e12','X19_INCOME.B19001e13','X19_INCOME.B19001e14','X19_INCOME.B19001e15','X19_INCOME.B19001e16','X19_INCOME.B19001e17','X15_EDUCATIONAL_ATTAINMENT.B15003e1','X15_EDUCATIONAL_ATTAINMENT.B15003e2','X15_EDUCATIONAL_ATTAINMENT.B15003e3','X15_EDUCATIONAL_ATTAINMENT.B15003e4','X15_EDUCATIONAL_ATTAINMENT.B15003e5','X15_EDUCATIONAL_ATTAINMENT.B15003e6','X15_EDUCATIONAL_ATTAINMENT.B15003e7','X15_EDUCATIONAL_ATTAINMENT.B15003e8','X15_EDUCATIONAL_ATTAINMENT.B15003e9','X15_EDUCATIONAL_ATTAINMENT.B15003e10','X15_EDUCATIONAL_ATTAINMENT.B15003e11','X15_EDUCATIONAL_ATTAINMENT.B15003e12','X15_EDUCATIONAL_ATTAINMENT.B15003e13','X15_EDUCATIONAL_ATTAINMENT.B15003e14','X15_EDUCATIONAL_ATTAINMENT.B15003e15','X15_EDUCATIONAL_ATTAINMENT.B15003e16','X15_EDUCATIONAL_ATTAINMENT.B15003e17','X15_EDUCATIONAL_ATTAINMENT.B15003e18','X15_EDUCATIONAL_ATTAINMENT.B15003e19','X15_EDUCATIONAL_ATTAINMENT.B15003e20','X15_EDUCATIONAL_ATTAINMENT.B15003e21','X15_EDUCATIONAL_ATTAINMENT.B15003e22','X15_EDUCATIONAL_ATTAINMENT.B15003e23','X15_EDUCATIONAL_ATTAINMENT.B15003e24','X15_EDUCATIONAL_ATTAINMENT.B15003e25','X02_RACE.B02001e1','X02_RACE.B02001e2','X02_RACE.B02001e3','X02_RACE.B02001e4','X02_RACE.B02001e5','X02_RACE.B02001e6','X02_RACE.B02001e7','X02_RACE.B02001e8','X03_HISPANIC_OR_LATINO_ORIGIN.B03003e1','X03_HISPANIC_OR_LATINO_ORIGIN.B03003e2','X03_HISPANIC_OR_LATINO_ORIGIN.B03003e3','X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e1','X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e2','X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e7','X23_EMPLOYMENT_STATUS.B23025e1','X23_EMPLOYMENT_STATUS.B23025e2','X23_EMPLOYMENT_STATUS.B23025e7','X09_CHILDREN_HOUSEHOLD_RELATIONSHIP.B09019e1','X09_CHILDREN_HOUSEHOLD_RELATIONSHIP.B09018e1']
    acs = gpd.read_file(frompath,
                        layer = frompath[frompath.rfind("/")+1:frompath.rfind(".")])[["GEOID","geometry"]] 
    # Open each layer, then collect the variables in it
    for l in set([v[:v.index(".")] for v in varlist]):  # Unique layers in the var list
        print("    Opening layer",l)
        layercols = [c[c.index('.')+1:] for c in varlist if c[:c.index('.')] == l]
        layercols.extend(["GEOID"])
        layercombined = gpd.read_file(frompath, layer = l)[layercols]
        acs = acs.merge(layercombined, on='GEOID', how='left')
    acs["GEOID"] = acs.GEOID.str[-12:]  # original formats GEOID like 15000US721537506022
    return acs

def get_shapes(fromprefix):
    """
    This function reads the shapes of Block Group geographies as well as their land area
    from the Cenus' TIGER/Line publication.  The source organizes shapes state by state
    so a reference list of states, with their FIPS codes, is read from the Open Environments
    core repository.
    
    :param  fromprefix:  String containing the path where the files have been downloaded
                         from https://www2.census.gov/geo/tiger/TIGER2019/BG/ eg
                         
    :return tiger: dataframe with all states and their block groups appended.
    """
    print("Pulling TIGER/Line geographics:","Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    states = pd.read_csv("https://raw.githubusercontent.com/OpenEnvironments/core/main/states.csv")
    tiger = gpd.read_file(fromprefix+"01_bg").truncate(after=-1)
    tiger.truncate()
    for i,state in states[~states.CensusName.isna()].iterrows():
        tiger = pd.concat([tiger, \
                          gpd.read_file(fromprefix + "{:02d}".format(state["StateFIPS"]) + "_bg")],
                          axis=0)
    print("   Done:","Block Groups:",tiger.shape[0],"Mem: {:.2f}G".format(psutil.virtual_memory()[1]/1000000000))
    return tiger

def combine_derive(acs,tiger):
    """
    This function accepts dataframes with ACS and TIGER Line shapes, combines them
    on Block Group geoids, then adds derivations.
    
    :param  acs, tiger: dataframes, keyed on 12 digit block group GEOID
    :return combined: dataframe with the inputs merged columnwise with these
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
    combined = pd.merge(acs,tiger,on="GEOID",how="outer")
    print("Merge done",combined.shape)
    combined['Over65Rate'] = (combined['B01001e20'] + combined['B01001e21'] + combined['B01001e22'] + combined['B01001e23'] + combined['B01001e24'] + combined['B01001e25'] + combined['B01001e44'] + combined['B01001e45'] + combined['B01001e46'] + combined['B01001e47'] + combined['B01001e48'] + combined['B01001e49']) / (combined['B01001e2'] + combined['B01001e26'])
    combined['MinorityRate'] = 1 - (combined['B02001e2'] / combined['B02001e1'])
    combined['PopDensity'] = combined['B01001e1'] / combined['ALAND']
    combined['CollegePlusRate'] = (combined['B15003e21'] + combined['B15003e22'] + combined['B15003e23'] + combined['B15003e24'] + combined['B15003e25']) / combined['B15003e1']
    combined['EmploymentRate'] = combined['B23025e2'] / combined['B23025e1']
    combined['FamilyRate'] = combined['B11001e2'] / combined['B11001e1']
    combined['ChildrenRate'] = combined['B09018e1'] / combined['B09019e1']
    combined['Under25KRate'] = (combined['B19001e2'] + combined['B19001e3'] + combined['B19001e4'] + combined['B19001e5']) / combined['B19001e1']
    combined['logPop'] = np.log(combined.B01001e1)
    combined['logPopDensity'] = np.log(combined.PopDensity)
    combined['logLand'] = np.log(combined.ALAND)
    return combined

def put_results(combined, fn):
    """
    This function accepts a dataframe and filename prefix
    to generate a zipped CSV file (.zip) pandas pickle file (.pkl)
    with the filename prefix.
    """
    combined.to_csv(fn+'.zip',
              index=False,
              header=True,
              compression="zip",
              encoding='utf-8-sig')
    combined.to_pickle(fn+'.pkl')
    return

if __name__ == "__main__":
    acs = get_demogs("D:/Open Environments/data/census/acs/acs5/ACS_2019_5YR_BG.gdb")
    tiger = get_shapes("D:/Open Environments/data/census/tiger/2019 blockgroups/tl_2019_")
    combined = combine_derive(acs,tiger)
    put_results(combined,'blockgroupdemographics')
