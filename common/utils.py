# -*- coding: utf-8 -*-
import os
import string
import json
import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr
from dateutil.parser import parse
from common import globals as glob

SPECIAL_CHARS = string.punctuation.replace("_", "")
SPECIAL_CHARS = string.punctuation.replace("-", "")
SPECIAL_CHARS = set(SPECIAL_CHARS)

def get_quality_summary(qual):
    summary = {}
    #we are only intrested in the dqs (data quality score) under each category
    for q in qual.keys():
        summary[q] = {}
        summary[q]['dqs'] = qual[q]['dqs']
    return summary
    
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
        row = df.ix[i]
        val = str(row[field])
        try:
            float(val)
        except Exception as e:
            num_invalid += 1
            glob.log.error('found an invalid %s -> %s' % (field, str(row[field])))
    
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
    if mandatory_feature_list_provided == True:
        adjusted_raw_score = round(100 - ((float(mandatory_cells_empty_count)/total_cell_count)))
    else:
        #in case no mandatory features were provided then adjusted score is same as raw score
        adjusted_raw_score = raw_score
        
    qual['missing_data']['dqs'] = {}
    qual['missing_data']['dqs']['raw_score']      = raw_score
    qual['missing_data']['dqs']['adjusted_score'] = adjusted_raw_score 
    
    return qual

    
def write_dict_to_csv(data_dict, fname):
    fname = os.path.join(glob.OUTPUT_DIR_NAME, fname) 
    glob.log.info('going to write dictionary to ' + fname)
    #glob.log.info(json.dumps(data_dict, indent=glob.INDENT_LEVEL))
    with open(fname, 'w') as csv_file:  
        #write the header row
        line = '\"country_code\",' #first column is country code
        #now the indicators
        #get all the keys from the first dictionary, they are the same for all dictionaries
        #this is a python3 thing because we would get a dict_keys, we convert it into a list
        #and then the first element of the list we access and then get the keys from there
        #this is specific to the WB data dictionary so this function shouldnt technically be
        #in utils.py, but ok..
        key_list = data_dict[list(data_dict.keys())[0]].keys()

        for k in key_list:
            line = encode_str_in_csv(line, k)
            
        #remove the last ',' from the end
        line = line[:-1]
        line += '\n'    
        #read to write header row
        csv_file.write(line) 
            
        #access dictionary by dictionary or rather country by country
        for k in data_dict.keys():
            #start with an empty line to write
            line = ''
            d = data_dict[k] #this dictionary represents one country
            line = encode_str_in_csv(line, k) #country code
            key_count = 0
            
            for k2 in d.keys(): #indicators within a country
                
                val = d[k2]
                if k2 != 'name': #name key already holds a string   
                    val = str(val)
                #if there is single quote in the name then rmeove it, caused problem    
                #when reading the file back
                val = val.replace('’', '')    
                #put the key in quotes, as some keys/values could have spaces    
                line = encode_str_in_csv(line, val) #value of individual indicators  
                key_count += 1                     
            glob.log.info('country %s, indicators %d' %(k, key_count))
            #write to csv
            #remove the last ',' from the end
            line = line[:-1]
            line += '\n' 
            #glob.log.info(line)
            #ignore any non-ascii characters, this is needed because certain country names
            #have non utf-8 characters..they were causing an exception..
            #line = line.encode('ascii', 'ignore')
            csv_file.write(str(line))    

def do_eda(df, filename, ds_name, categorial_feature_list, excluded_list):
    glob.log.info('about to do some EDA (exploratory data analysis) on %s data...' %(ds_name))
    eda_dict = { 'feature': [], 'mean': [], 'mode':[], 'median':[], 'stddev':[]}
    #except for country code all fields are numeric and we can calculate
    #mean, median and sd
    for col in df.columns:
        if col in excluded_list:
            continue
        eda_dict['feature'].append(col)
        if col in categorial_feature_list:
            #calc mode by first storing in a categorical series
            s = pd.Categorical(df[col], categories=df[col].unique())
            cc = s.value_counts() 
            pd.Series.sort(cc, inplace=True, ascending=False)
            #what if there are two modes...just handle one case..doesnt happen in our dataset anyway
            #if cc.ix[cc.index[0]] == cc.ix[cc.index[1]]:
            #    mode = cc.index[0] + ',' + cc.index[1]
            #    glob.log.info('there are more than 1 modes for %s[%s]' %(ds_name, col))
            #else:
            #    mode = cc.index[0]
            mode_str = str(cc.index[0]) + ':' + str(cc.ix[cc.index[0]]) 
            eda_dict['mode'].append(mode_str)
            eda_dict['mean'].append(0)
            eda_dict['median'].append(0)
            eda_dict['stddev'].append(0)
        else:
            #calc other descriptive stats
            eda_dict['mode'].append(0)
            eda_dict['mean'].append(df[col].mean())
            eda_dict['median'].append(df[col].median())
            eda_dict['stddev'].append(np.sqrt(df[col].var()))
    eda_df = pd.DataFrame(eda_dict)
    eda_df.to_csv(filename, index=False, encoding='utf-8') 
    try:
        glob.log.info(eda_df)
    except Exception as e:
        glob.log.error('Exception while logging eda_df: ' + str(e))

def detect_outliers(df, ds_name, excluded_col_list, key_col_name):
    glob.log.info('Detecting outliers for %s dataset' %(ds_name))
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, ds_name + '_' + glob.OUTLIERS_CSV)
    f = open(fname, 'w')
    f.write('dataset,entry,field,value,3rdStdDev\n')
    for col in df.columns:
        if col in excluded_col_list:
            continue
        #refer to the column as a series, just for ease of understanding
        S = df[col]
        # we want to say anything outside of the 3rd standard deviation is an outlier...
        outliers = S[((S-S.mean()).abs()>3*S.std())] 
        if len(outliers) > 0:
            #print out the outliers
            sigma = S.std()
            for i in outliers.index:
                entry = df.iloc[i]
                glob.log.error('[%s] for entry %s, field %s has value %f which is outside the 3rd stddev(%f)'
                               %(ds_name, entry[key_col_name], col, entry[col], 3*sigma))
                f.write('%s,%s,%s,%f,%f\n' %(ds_name, entry[key_col_name], col, entry[col], 3*sigma))  
    f.close()                
        
def calc_r(ds_name, fname, df, feature_list):
    glob.log.info('Calculating r for %s dataset' %(ds_name))
    f = open(fname, 'w')
    f.write('Dataset,feature1,feature2,r\n')
    #remove all NA values as pearsons needs to have both series of the same size
    df2 = df[feature_list].dropna()
    #calculate perason coefficient for all possible combinations
    for i in range(len(feature_list)-1):  
        for j in range(i+1, len(feature_list)):
            r = pearsonr(df2[feature_list[i]], df2[feature_list[j]])[0]
            glob.log.info('Pearson coeff(r) for %s and %s is %f' %(feature_list[i], feature_list[j], r))
            f.write('%s,%s,%s,%f\n' %(ds_name,feature_list[i], feature_list[j], r))
    f.close()        

def calc_dqs(df):
    df_temp = pd.isnull(df)
    num_cells = df_temp.shape[0]*df_temp.shape[1]
    empty_cells = 0
    for c in df_temp.columns:     
        empty_cells += sum(df_temp[c])
    dqs = ((num_cells-empty_cells)*100)/num_cells
    glob.log.info('data quality score for dataset is %f' %(dqs)) 
    return dqs

def get_numeric_feature_list(df, excluded_feature_list):    
    numeric_features = []
    for col in df.columns:
        try:
            x=df[col].iloc[0] 
            float(x)#typecast the data to float to test if it is numeric
        except:
            glob.log.info('%s is not a numeric feature, ignoring' %(col))
        else:
            if col not in excluded_feature_list:
                numeric_features.append(col)    
    return numeric_features       