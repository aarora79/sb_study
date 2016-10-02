# -*- coding: utf-8 -*-
import os
import string
from dateutil.parser import parse
from common import globals as glob

SPECIAL_CHARS = string.punctuation.replace("_", "")
SPECIAL_CHARS = string.punctuation.replace("-", "")
SPECIAL_CHARS = set(SPECIAL_CHARS)

def contains_special_chars(word):   
    #glob.log.info(word)
    if any(char in SPECIAL_CHARS for char in word):
        return True
    else:
        return False
    
def encode_str_in_csv(line, s):
    line += '\"' + s + '\"' + ','
    return line

def store_in_dict(d, k, key1, val1, key2, val2):
    d[k] = {}
    d[k][key1] = val1
    d[k][key2] = val2
    
def check_date(qual, category, df, field):
    glob.log.info('checking %s ...' %(field))
    #just a simple check to validate date
    num_invalid = 0
    for i in range(len(df)):
        store = df.ix[i]
        try:
            parse(store[field])
        except Exception as e:
            num_invalid += 1
            glob.log.error('found an invalid %s -> %s for store id %s' % (field, str(store[field]), str(store['store_id']))) 
            glob.log.error(str(e))
            
    qual[category][field] = {}
    qual[category][field]['count']   = num_invalid   
    qual[category][field]['percent'] = round(100*(float(num_invalid)/len(df)), glob.PRECISION)
    return num_invalid
    
    
def check_as_string_wo_special_chars(qual, category, df, field, prim_key_field):
    glob.log.info('checking %s ...' %(field))
    #just a simple check to say should not contain any special characters
    num_invalid = 0
    for i in range(len(df)):
        store = df.ix[i]
        if contains_special_chars(str(store[field])) == True:
            num_invalid += 1
            glob.log.error('found an invalid %s -> %s for store id %s' % (field, str(store[field]), str(store[prim_key_field]))) 
    
    qual[category][field] = {}
    qual[category][field]['count']   = num_invalid   
    qual[category][field]['percent'] = round(100*(float(num_invalid)/len(df)), glob.PRECISION)
    return num_invalid

def check_as_numeric(qual, category, df, field):
    glob.log.info('checking %s ...' %(field))
    #just a simple check to say field should be numeric
    num_invalid = 0
    for i in range(len(df)):
        store = df.ix[i]
        val = str(store[field])
        try:
            float(val)
        except Exception as e:
            num_invalid += 1
            glob.log.error('found an invalid %s -> %s for store id %s' % (field, str(store[field]), str(store['store_id']))) 
    
    qual[category][field] = {}
    qual[category][field]['count']   = num_invalid   
    qual[category][field]['percent'] = round(100*(float(num_invalid)/len(df)), glob.PRECISION)
    return num_invalid  
    
def check_missing(qual, df, mf = []):
    glob.log.info('checking missing data...')
    qual['missing_data'] = {}
    
    #check missing fraction of missing rows in each column and also overall
    total_cell_count = df.shape[0] * df.shape[1] #rows x columns
    total_empty_cells = 0
    mandatory_cells_empty_count = 0 #count of empty cells in mandatory columns
    mandatory_feature_list_provided = (True if len(mf) != 0 else False)
    
    for col in df.columns:
        #find out the number of columns that are empty, the idea is that
        #we would end up with a TRUE/FALSE array and then summing it up
        #gives the count of FALSE or empty cells
        empty_cells        = df[col].isnull()
        num_empty_cells    = sum(empty_cells)
        total_empty_cells += num_empty_cells
        total_cells        = len(empty_cells)

        #if mandatory feature list provided then check if this feature is mandatory  
        #if no specific list is provided then consider all features as mandatory      
        if mandatory_feature_list_provided == True:
            if col in mf:
                mandatory_cells_empty_count += num_empty_cells
        else:
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

    
def write_dict_to_csv(dict, fname):
    fname = os.path.join(glob.OUTPUT_DIR_NAME, fname) 
    glob.log.info('going to write dictionary to ' + fname)
    with open(fname, 'wb') as csv_file:  
        #write the header row
        line = '\"country_code\",' #first column is country code
        #now the indicators
        #get all the keys from the first dictionary, they are the same for all dictionaries
        for k in dict[dict.keys()[0]].keys():
            #put the key in quotes, as some keys/values could have spaces
            line = encode_str_in_csv(line, k)
        #remove the last ',' from the end
        line = line[:-1]
        line += '\n'    
        #read to write header row
        csv_file.write(line) 
            
        #access dictionary by dictionary
        for k in dict.keys():
            #start with an empty line to write
            line = ''
            d = dict[k]
            line = encode_str_in_csv(line, k) #country code
            key_count = 0
            
            for k2 in d.keys():
                
                val = d[k2]
                if k2 != 'name': #name key already holds a string   
                    val = str(val)
                #put the key in quotes, as some keys/values could have spaces    
                line = encode_str_in_csv(line, val) #value of individual indicators  
                key_count += 1                     
            glob.log.info('country %s, indicators %d' %(k, key_count))
            #write to csv
            #remove the last ',' from the end
            line = line[:-1]
            line += '\n' 
            #ignore any non-ascii characters, this is needed because certain country names
            #have non utf-8 characters..they were causing an exception..
            line = line.encode('ascii', 'ignore')
            csv_file.write(line)    