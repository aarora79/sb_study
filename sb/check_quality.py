# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 18:36:26 2016

@author: aarora
"""
import pandas as pd

from common import globals as glob

#list of mandatory feature which cannot be missing from a store record
#these would be needed at the time of machine learning and cannot be 
#filled in as part of data cleaning so they need to be present
MANDATORY_FEATURES = ['store_id', 'country', 'ownership_type', 'brand']

def store_in_dict(d, k, key1, val1, key2, val2):
    d[k] = {}
    d[k][key1] = val1
    d[k][key2] = val2
    
def check_missing(qual, df):
    qual['missing_data'] = {}
    
    #check missing fraction of missing rows in each column and also overall
    total_cell_count = df.shape[0] * df.shape[1] #rows x columns
    total_empty_cells = 0
    mandatory_cells_empty_count = 0 #count of empty cells in mandatory columns
    
    for col in df.columns:
        #find out the number of columns that are empty, the idea is that
        #we would end up with a TRUE/FALSE array and then summing it up
        #gives the count of FALSE or empty cells
        empty_cells        = df[col].isnull()
        num_empty_cells    = sum(empty_cells)
        total_empty_cells += num_empty_cells
        total_cells        = len(empty_cells)
        
        if col in MANDATORY_FEATURES:
            mandatory_cells_empty_count += num_empty_cells
        
        fraction_empty  = 100*(float(num_empty_cells)/(total_cells))
        #store this info in the dict if there were any empty cells
        if num_empty_cells != 0:
            store_in_dict(qual['missing_data'], col, 'percent',
                          round(fraction_empty, glob.PRECISION), 
                          'count', num_empty_cells)
        
    #overall empty cell fraction
    fraction_empty = 100*(float(total_empty_cells)/(total_cell_count))
    store_in_dict(qual['missing_data'], 'overall', 'percent',
                  round(fraction_empty, glob.PRECISION), 
                  'count', total_empty_cells)
    
    #calculate two data quality scores; a raw score calculated simply as
    # 1 - (total missing values/total values) and an adjusted score which
    #is calculated based on missing values that really matter i.e. which would
    #cause the entire row to get discarded.
    raw_score = round(100 - fraction_empty, glob.PRECISION)
    adjusted_raw_score = round(100 - ((float(mandatory_cells_empty_count)/total_cell_count)))
    qual['missing_data']['dqs'] = {}
    qual['missing_data']['dqs']['raw_score']      = raw_score
    qual['missing_data']['dqs']['adjusted_score'] = adjusted_raw_score 
    
    return qual

def check_store_id(qual, df):
    #all store id's that are unique are correct, all others are considered invalid
    num_uniq = len(df['store_id'].unique())
    total    = len(df['store_id'])
    num_non_unique = total - num_uniq
    
    qual['invalid_data']['store_id'] = {}
    qual['invalid_data']['store_id']['count']   = num_non_unique   
    qual['invalid_data']['store_id']['percent'] = round(100*(float(num_non_unique/total)),
                                                        glob.PRECISION)
    return num_non_unique

def check_lat_long(qual, df):
    #find stores with invalid latitude or longitude values
    #valid latitude is >=-90 to <=90 and valid longitude >=-180 and <=180
    invalid_lat_long_count = 0
    for i in range(len(df)):
        store = df.ix[i]
        lat  = float(store['latitude'])
        long = float(store['longitude']) 
        lat_valid =  (lat >= -90 and lat <= 90)
        long_valid = (long >= -180 and long <= 180)
        if lat_valid == False or long_valid == False:
            invalid_lat_long_count += 1
    
    qual['invalid_data']['lat_long'] = {}
    qual['invalid_data']['lat_long']['count']   = invalid_lat_long_count   
    qual['invalid_data']['lat_long']['percent'] = round(100*(float(invalid_lat_long_count)/len(df)),
                                                        glob.PRECISION)
    return invalid_lat_long_count

def check_timezone(qual, df):
    #find stores with invalid timezone values
    #valid timezones have offset which are multiple of 15 see https://en.wikipedia.org/wiki/UTC_offset

    ##this is not working, doing it the round about non pythonic way :(
    #invalid_tz_offset = df['current_timezone_offset'] % 15 != 0
    num_invalid_tz_offset = 0
    for i in range(len(df)):
        store = df.ix[i]
        if int(store['current_timezone_offset']) % 15 != 0:
            num_invalid_tz_offset += 1
    #num_invalid_tz_offset = sum(invalid_tz_offset)    
    
    qual['invalid_data']['current_timezone_offset'] = {}
    qual['invalid_data']['current_timezone_offset']['count']   = num_invalid_tz_offset   
    qual['invalid_data']['current_timezone_offset']['percent'] = round(100*(float(num_invalid_tz_offset)/len(df)),
                                                                       glob.PRECISION)
    return num_invalid_tz_offset

def check_country_code(qual, df):
    #lookup the country codes via a csv file obtained from 
    #https://raw.githubusercontent.com/datasets/country-list/master/data.csv
    cc_df = pd.read_csv(glob.CONTRY_CODE_CSV)
    num_invalid_cc = 0
    for i in range(len(df)):
        num_occurances = 0
        store = df.ix[i]
        #check if the country code occurs in the master country code list
        #count the number of occurances, we need at least 1 occurance for the 
        #country code to be valid
        num_occurances = sum(cc_df['Code'] == store['country'])
        if num_occurances == 0:
            num_invalid_cc += 1
            
    qual['invalid_data']['country'] = {}
    qual['invalid_data']['country']['count']   = num_invalid_cc   
    qual['invalid_data']['country']['percent'] = round(100*(float(num_invalid_cc)/len(df)),
                                                       glob.PRECISION)
    return num_invalid_cc  
    
                                                        
def check_invalid(qual, df):
    #we can do a bunch of checks here....
    #1. store_id has to be unique, obviously.
    #2. lat/long have to be valid.
    #3. Timzones have to be valid.
    #4. Country codes have to be valid.
    # The score is finally calculated as count of 1 - (all invalid values/all values)
    # calculated for each of the features being validated as well as for the 
    # overall dataset
    qual['invalid_data'] = {}
    invalid_cells = 0
    total_cell_count = df.shape[0] * df.shape[1] #rows x columns
    
    invalid_cells += check_store_id(qual, df)

    invalid_cells += check_lat_long(qual, df)    
    
    invalid_cells += check_timezone(qual, df)
    
    invalid_cells += check_country_code(qual, df)

    fraction_invalid = (100 * float(invalid_cells)/total_cell_count)
    score = round(100 - fraction_invalid, glob.PRECISION)
    qual['invalid_data']['dqs'] = {}
    #raw score and adjusted score are the same, no difference as we are only
    #looking at features of intrest
    qual['invalid_data']['dqs']['raw_score']      = score
    qual['invalid_data']['dqs']['adjusted_score'] = score
                                                          
    
def check(df):
    #store various quality parameters in a dictionary
    qual = {}
    
    #check for missing data
    check_missing(qual, df)
    
    #check for incorrect/invalid data
    check_invalid(qual, df)
    
    return qual