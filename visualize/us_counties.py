# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 00:55:49 2016

@author: aarora
"""

import os
import numpy as np
import statsmodels.api as sm # recommended import according to the docs
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats.mstats as mstats
import ast
import requests as req
import sys
from datetime import datetime

def run(argv):
    county_store_data = {}
    county_store_names= {}
    
    count = 1
    df = pd.read_csv('SB_data_w_features.csv')
    for i in range(len(df)):
        store = df.ix[i]
        if store['country'] != 'US':
            continue
        location = store['coordinates']
        location = ast.literal_eval(location)    
        
        api = 'http://data.fcc.gov/api/block/find?format=json&latitude=%f&longitude=%f' %(float(location['latitude']), float(location['longitude']))
        r = req.get(api)         
        if r.ok == True:
            if count % 100 == 0:
                print('[%s] success[%d]: %s' %(str(datetime.now()),count,api))
            count += 1
            resp = r.json()
            #print(resp)
            code = resp['County']['FIPS']
            if code not in county_store_data.keys():                 
                county_store_data [code] = 1
                county_store_names[code] = resp['County']['name'] + ', ' + resp['State']['code']
            else:
                county_store_data[code] += 1       
        else:
            print('error while downloading data')
                
    df = pd.DataFrame(columns=['county_FIPS_code', 'name', 'count'])
    df['county_FIPS_code'] = county_store_data.keys()
    df['name']  = [county_store_names[k] for  k in county_store_names.keys()]
    df['count'] = [county_store_data[k] for  k in county_store_data.keys()]
    df.to_csv('us_counties_starbucks_stores.csv', index=False)
                               
                
if __name__ == "__main__":
    print('This module is run only as a standalone module.\n')
    print('This is needed to map the location of every Startbucks store in the U.S. to a county name')
    print('and then create a CSV file called \"us_counties_starbucks_stores.csv\" which lists every')
    print('U.S. county with the number of Starbucks stores it has.')
    print('This module require the \"SB_data_w_features.csv\" to be present in the same directory so')
    print('that the location i.e. latitude and longitude of the Starbucks stores can be obtained.')
    # execute only if run as a script
    #run(sys.argv)   