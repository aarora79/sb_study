# -*- coding: utf-8 -*-
import requests as req
import pandas as pd
import json
import os
import sys

import sb_check_quality as cq

from common import globals as glob

# dictionary to hold country to continent mapping, will be filled in
# get_country_to_continent_mapping function invokved automatically during init
country_to_continent_dict = {}
code_to_country_dict      = {}

#handle special cases, some of which were not in the csv file downloaded for country to code to continent mapping
special_code_to_continent_mapping = { 'TW': 'Asia', 'AW': 'South America', 'CW': 'South America', 'KP': 'Asia', 'KR': 'Asia',
                                      'VN': 'Asia', 'BN': 'Asia', 'BO': 'South America', 'PR': 'North America' }
                                      
def get_code_to_country_mapping(code_to_country_dict):
    df = None
    fname = glob.CONTRY_CODE_CSV           
            
    #now read the csv into a dataframe so that we can use it in future
    df = pd.read_csv(fname)    
    for i  in range(len(df)):
        row = df.ix[i]
        country   = row['Name']
        country = country.decode('utf-8') #handle unicode, many countries have names that do not fit into ascii
        code = row['Code']
        if code not in code_to_country_dict.keys():
            code_to_country_dict[code] = country 

    return code_to_country_dict

def get_country_to_continent_mapping(country_to_continent_dict):
    df = None
    #download from here
    #https://commondatastorage.googleapis.com/ckannet-storage/2012-07-26T090250/Countries-Continents-csv.csv
    api = glob.COUNTRY_TO_CONTINENT_MAPPING_API
    r = req.get(api)
    #if the return code is not 200 ok then its an errors
    if r.ok != True:
        glob.log.error('Error while retrieving information about country to continent, server sent status code ' + str(r.status_code))
        glob.log.error('Here is everything that was sent by the server...')
        glob.log.error(r.text)
    else:            
        #looks like we got the response
        glob.log.info('successfully received a response from the country to continent API endpoint ' + api)
        #dump the data in a csv file
        fname = glob.COUNTRY_CONTINENET_CSV
        with open(fname, 'wb') as csv_file:  
            csv_file.write(r.text)            
            
        #now read the csv into a dataframe so that we can use it in future
        df = pd.read_csv(fname)    
        for i  in range(len(df)):
            row = df.ix[i]
            country   = row['Country'].decode('utf-8')
            continent = row['Continent']
            if country not in country_to_continent_dict.keys():
                country_to_continent_dict[country] = continent  

    return country_to_continent_dict
    
def get_data():
    glob.log.info('about to get SB data...')
    df = None
    
    # Starbucks store location data is available from https://opendata.socrata.com via an API. 
    # The Socrate Open Data API (SODA) end point for this data is
    # https://opendata.socrata.com/resource/xy4y-c4mk.json
    api = glob.STARBUCKS_API_ENDPOINT + '?' + '$limit=' + str(glob.SOCRATA_LIMIT_PER_API_CALL)
    r = req.get(api)
    
    #if the return code is not 200 ok then its an errors
    if r.ok != True:
        glob.log.error('Error while retrieving information about SB, server sent status code ' + str(r.status_code))
        glob.log.error('Here is everything that was sent by the server...')
        glob.log.error(r.text)
    else:            
        #looks like we got the response
        glob.log.info('successfully received a response from the SB API endpoint ' + api)
        
        #Store the response in a dataframe
        df = pd.DataFrame(r.json())
        
        #lets see what the dataframe looks like
        glob.log.info('columns in the data frame -> ' + str(df.columns))
        glob.log.info('the dataframe contains %d rows and %d columns' %(df.shape[0], df.shape[1]))
        
        #save the dataframe to a CSV
        fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.SB_CSV_FILE)
        df.to_csv(fname, encoding='utf-8', index = False)

    return df

def check_quality_of_data(df):
    glob.log.info('about to check quality of SB data...')
    
    #overall quality metrics
    qual = cq.check(df)
    glob.log.info('======= quality metrics for starbucks data ============')
    glob.log.info(json.dumps(qual, indent=glob.INDENT_LEVEL))
    glob.log.info('=======================================================')
    return qual
 
def add_continent_name(df):
    #for each country provided as code in SB data first find out the actual name
    #then lookup that name in the other dictionary to find out the continent
    continent_list = []
    for i  in range(len(df)):
        row = df.ix[i]
        country_code = row['country']
        continent_name = 'unknown'
        #step 1: find the country name  
        #glob.log.info('looking up country code ' + country_code)
        if country_code in code_to_country_dict.keys():
            country_name = code_to_country_dict[country_code]
            #glob.log.info('looking up country name ' + country_name)
            #now for step 2: check the name in the country name to continent dictionary
            
            if country_name in country_to_continent_dict.keys():
                #found it, return continent name
                continent_name = country_to_continent_dict[country_name]
            #special check for some countries which were not found in regular mapping
            if country_code in special_code_to_continent_mapping.keys():
                continent_name = special_code_to_continent_mapping[country_code]
        #whether we could find a name or not, append it to the list as we have to add this as a 
        #column to the dataframe
        continent_list.append(continent_name)  
        
    #we are ready with the continent list now, add it to the dataframe as a new column
    df['continent'] = continent_list
    return df    
    
def add_is_airport_feature(df):
    #for each store look for the terms Terminal, Airport or Arpt    in the street_combined and name fields
    #due to lack of time i cannot do this right way right now..have registed with the IATA website
    #and will replace this code with an IATA API which finds the nearest Airport within a given input radius
    #provided lat/long , so for stores located on airport terminals we can radius is 1mile or maybe say stores
    #within a 5mile radius of an airport are considered as stores on airports...anyway for now just do the easy check
    #IATA API to be used is https://iatacodes.org/api/v6/nearby?api_key=MY-KEY&lat=32.03856277&lng=118.8665009&distance=5

    AIRPORT_KEYWORDS = [ u'Airport', u'Arpt', u'Terminal']
    on_airport_list = []
    for i  in range(len(df)):
        row = df.ix[i]
        name = row['name']
        street_combined = row['street_combined']
        on_airport = False
        for k in AIRPORT_KEYWORDS:
            try:     
                if k in name or k in street_combined:
                    on_airport = True
            except Exception as e:
                glob.log.error('could not check name %s street %s for airport because it is probably in unicode' % (name, street_combined))
        on_airport_list.append(on_airport)  
    #we are ready with the onairport list now, add it to the dataframe as a new column
    df['on_airport'] = on_airport_list
    return df    

def add_eodb_feature(df):
    #join this data with with the WB data for intresting features...
    #ease of doing business is certainly one..to answer questions like what %
    #of starbucks stores exist in countries with very high ease of doing business
    #we could make a histogram of the distribution of stores in countries with EODB
    #between 1 - 10 (1 = highest), 11 - 20..and so on ..i think  until 130-140 

    #we will add a new column which will be the EODB index obtained from WB data
    eodb_index_list = []
    for i  in range(len(df)):
        row = df.ix[i]
        code = row['country']
        eodb = 0 #place holder for unknown, 0 is not a valid value
        if code in glob.wb['wdi_data'].keys():
            #country code found in WB data, we can find the indicator value now
            #for a list of all WDI (World Development Indicators) used in this 
            #package..look at WDI_Series.csv file in the root directoryof the package
            eodb = glob.wb['wdi_data'][code]['IC.BUS.EASE.XQ']
        eodb_index_list.append(eodb)
        
    #we are ready with the onairport list now, add it to the dataframe as a new column
    df['eodb_index'] = eodb_index_list
    return df    
        
def create_features(df):
    glob.log.info('adding new features...')
    #we are going to add the following features
    #1. continent name
    df = add_continent_name(df)
    
    #is this a store on an airport
    df = add_is_airport_feature(df)
    
    #what is the ease of doing business in the country in which this store is located
    df = add_eodb_feature(df)
    
    #all features added, create an updated CSV file with new features
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.SB_CSV_FILE_W_FEATURES)
    df.to_csv(fname, encoding='utf-8', index = False)
        
def clean_data(df):
    glob.log.info('about to clean data...')
    return df

def visualize_data(df):
    glob.log.info('about to visualize SB data...')


def init():
    global country_to_continent_dict
    global code_to_country_dict
    #well we need some more data for feature generation, like country to continent mapping for example
    country_to_continent_dict = get_country_to_continent_mapping(country_to_continent_dict)   
    if len(country_to_continent_dict.keys()) == 0:
        #failed to get conuntry to continent mapping, exit now
        glob.log.error('failed to create a dictionary for country to continent mapping, exiting...')
        sys.exit(1)
    
    #we also need country code to country name mapping
    code_to_country_dict = get_code_to_country_mapping(code_to_country_dict)   
    if len(code_to_country_dict.keys()) == 0:
        #failed to get code to country mapping, exit now
        glob.log.error('failed to create a dictionary for code to country mapping, exiting...')
        sys.exit(1)
        
    glob.log.info('SB module init complete')

