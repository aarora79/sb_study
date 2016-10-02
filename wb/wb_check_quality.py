# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 11:20:28 2016

@author: aarora
"""
import pandas as pd

from common import globals as glob
from common import utils

#list of mandatory feature which cannot be missing from a  record
#these would be needed at the time of machine learning and cannot be 
#filled in as part of data cleaning so they need to be present
#empty for now for WB data but would be updated; empty list means all features are mandatory
MANDATORY_FEATURES = []

def check_invalid(qual, df):
    glob.log.info('begin checks for invalid data...')
    #we can do a bunch of checks here....
    #all fields excepts the 'name' and 'country' field are numberic so do a check for that
    #and then do a simple check that country (2 char code) is not numer and does not contain
    #special characters..maybe also do a check to see if the numberic value is an outlier i.e.
    #is outside say 3rd standard deviation
    
    # The score is finally calculated as count of 1 - (all invalid values/all values)
    # calculated for each of the features being validated as well as for the 
    # overall dataset
    qual['invalid_data'] = {}
    invalid_cells = 0
    total_cell_count = df.shape[0] * df.shape[1] #rows x columns
    
    #these two columns are string type so skip them while doing numeric validation
    str_columns = ['name', 'country_code']
    for col in df.columns:
        if col not in str_columns:
            #validate column data for being numeric
            invalid_cells += utils.check_as_numeric(qual, 'invalid_data', df, col)
    #now validate the string type columns
    #validate column data for being a string without special characters
    # dont validate country names as it cound contain special characters like apostrophe...we could work around that
    #but skipping that for now        
    invalid_cells += utils.check_as_string_wo_special_chars(qual, 'invalid_data', df, 'country_code', 'country_code')
            
    glob.log.info('total number of attributes checked for invalid data %d' % (len(qual['invalid_data'])))
    
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
    utils.check_missing(qual, df)
    
    #check for incorrect/invalid data
    check_invalid(qual, df)
    
    return qual