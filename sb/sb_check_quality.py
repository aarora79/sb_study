# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 18:36:26 2016

@author: aarora
"""
import pandas as pd

from common import globals as glob
from common import utils

#list of mandatory feature which cannot be missing from a store record
#these would be needed at the time of machine learning and cannot be 
#filled in as part of data cleaning so they need to be present
MANDATORY_FEATURES = ['store_id', 'country', 'ownership_type', 'brand']

#valid startbucks brands, as listed on http://www.starbucks.com/careers/brands
VALID_STARBUCKS_BRANDS = ['Starbucks', 'Teavana', 'La Boulange', 'Evolution Fresh', 'Seattle\'s Best Coffee', 'Tazo Tea']

def store_in_dict(d, k, key1, val1, key2, val2):
    d[k] = {}
    d[k][key1] = val1
    d[k][key2] = val2
    
def check_brand(qual, df):
    glob.log.info('checking brand validity...')
    invalid = 0
    for i in range(len(df)):
        store = df.ix[i]
        brand = store['brand']
        if brand not in VALID_STARBUCKS_BRANDS:
            glob.log.error('found an invalid brand -> ' + brand + ' for store id ' + str(store['store_id']))
            invalid += 1
    total    = len(df['brand'])
    
    qual['invalid_data']['brand'] = {}
    qual['invalid_data']['brand']['count']   = invalid   
    qual['invalid_data']['brand']['percent'] = round(100*(float(invalid/total)),
                                                        glob.PRECISION)
    return invalid
                                                        
def check_store_id(qual, df):
    glob.log.info('checking store_id uniqueness...')
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
    glob.log.info('checking lat/long values...')
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
            glob.log.error('invalid lat/long value seen %f/%f for store id %s' % (lat, long, str(store['store_id'])))
    
    qual['invalid_data']['lat_long'] = {}
    qual['invalid_data']['lat_long']['count']   = invalid_lat_long_count   
    qual['invalid_data']['lat_long']['percent'] = round(100*(float(invalid_lat_long_count)/len(df)),
                                                        glob.PRECISION)
    return invalid_lat_long_count

def check_timezone_offset(qual, df):
    glob.log.info('checking timezone offsets...')
    #find stores with invalid timezone values
    #valid timezones have offset which are multiple of 15 see https://en.wikipedia.org/wiki/UTC_offset

    ##this is not working, doing it the round about non pythonic way :(
    #invalid_tz_offset = df['current_timezone_offset'] % 15 != 0
    num_invalid_tz_offset = 0
    for i in range(len(df)):
        store = df.ix[i]
        if int(store['current_timezone_offset']) % 15 != 0:
            num_invalid_tz_offset += 1
            glob.log.info('found an invalid timezone offset -> ' + store['current_timezone_offset'] +
                          'for country ' + store['country'] + ' store id ' + str(store['store_id']))
    #num_invalid_tz_offset = sum(invalid_tz_offset)    
    
    qual['invalid_data']['current_timezone_offset'] = {}
    qual['invalid_data']['current_timezone_offset']['count']   = num_invalid_tz_offset   
    qual['invalid_data']['current_timezone_offset']['percent'] = round(100*(float(num_invalid_tz_offset)/len(df)),
                                                                       glob.PRECISION)
    return num_invalid_tz_offset

def check_timezone_name(qual, df):
    glob.log.info('checking timezone offsets...')
    #A valid timezone name must contain the term "Standard Time" or "UTC"
    num_invalid_tz_names = 0
    for i in range(len(df)):
        store = df.ix[i]
        if 'Standard Time' not in store['timezone'] and 'UTC' not in store['timezone']:
            num_invalid_tz_names += 1
            glob.log.info('found an invalid timezone -> ' + store['timezone'] +
                          'for country ' + store['country'] + ' store id ' + str(store['store_id']))
    #num_invalid_tz_offset = sum(invalid_tz_offset)    
    
    qual['invalid_data']['timezone'] = {}
    qual['invalid_data']['timezone']['count']   = num_invalid_tz_names   
    qual['invalid_data']['timezone']['percent'] = round(100*(float(num_invalid_tz_names)/len(df)), glob.PRECISION)
    return num_invalid_tz_names
        
def check_store_number(qual, df):
    glob.log.info('checking store number...')
    #store number should be of the form XXXX-YYYY (well technically this should be written in Backus-Naur form
    #but you get the idea
    num_invalid_store_number = 0
    for i in range(len(df)):        
        store = df.ix[i]
        sn = str(store['store_number'])
        #example store number is 34512-97 or 41852-735 etc
        tokens = sn.split('-')
        if len(tokens) == 1: #there was no '-' this is an invalid entry
            num_invalid_store_number += 1
            glob.log.error('invalid store number %s for store id %s' %(sn, str(store['store_id'])))
        else:
             left  = tokens[0]
             right = tokens[1]
             #now check if both left and right are numeric, if not then this is invalid
             if left.isdigit() == False or right.isdigit() == False:
                 num_invalid_store_number += 1
                 glob.log.error('invalid store number %s for store id %s' %(sn, str(store['store_id'])))
                 
    qual['invalid_data']['store_number'] = {}
    qual['invalid_data']['store_number']['count']   = num_invalid_store_number   
    qual['invalid_data']['store_number']['percent'] = round(100*(float(num_invalid_store_number)/len(df)),
                                                            glob.PRECISION)
    return num_invalid_store_number  
    
    
def check_country_code(qual, df):
    #lookup the country codes via a csv file obtained from 
    #https://raw.githubusercontent.com/datasets/country-list/master/data.csv
    glob.log.info('checking country codes...')
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
            glob.log.error('found an invalid country code -> ' + store['country'] + ' for store id ' + str(store['store_id']))
            
    qual['invalid_data']['country'] = {}
    qual['invalid_data']['country']['count']   = num_invalid_cc   
    qual['invalid_data']['country']['percent'] = round(100*(float(num_invalid_cc)/len(df)),
                                                       glob.PRECISION)
    return num_invalid_cc  
    
                                                        
def check_invalid(qual, df):
    glob.log.info('begin checks for invalid data...')
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
    
    invalid_cells += check_timezone_offset(qual, df)
    
    invalid_cells += check_country_code(qual, df)
    
    invalid_cells += check_brand(qual, df)
  
    invalid_cells += check_store_number(qual, df)
    
    invalid_cells += check_timezone_name(qual, df)
    
    invalid_cells += utils.check_as_string_wo_special_chars(qual, 'invalid_data', df, 'ownership_type', 'store_id')
    
    invalid_cells += utils.check_date(qual, 'invalid_data', df, 'first_seen')

    glob.log.info('total number of attributes checked for invalid data %d' % (len(qual['invalid_data'].keys())))
    
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
    utils.check_missing(qual, df, MANDATORY_FEATURES)
    
    #check for incorrect/invalid data
    check_invalid(qual, df)
    
    return qual