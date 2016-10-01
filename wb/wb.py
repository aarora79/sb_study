# -*- coding: utf-8 -*-
import requests as req
import pandas as pd
import numpy as np
import json
import csv

from common import globals as glob

def get_wdi_data(wdi, wdi_data):
    
    #example URL http://api.worldbank.org/countries/ALL/indicators/IC.REG.DURS?date=2015&format=json&per_page=10000
    api = glob.WB_API_ENDPOINT + wdi + glob.WB_API_SUFFIX
    r = req.get(api)
    
    #if the return code is not 200 ok then its an errors
    if r.ok != True:
        glob.log.error('Error while retrieving information about WDI %s, server sent status code %d' %(wdi, r.status_code))
        glob.log.error('Here is everything that was sent by the server...')
        glob.log.error(r.text)
    else:            
        #looks like we got the response
        glob.log.info('successfully received a response from the WB API endpoint ' + api)
        
        #parse out the response. The response is a json array by country
        #we want to get the {country, value} tuple and store it in the input dict
        # the format is such that data if intrest starts from the second element in the json
        # see response to example URL mentioned above
        resp = r.json()[1]
        num_elems = len(resp)
        for i in range(num_elems):
            elem = resp[i]
            id = elem['country']['id']
            if id not in wdi_data.keys():                
                wdi_data[id] = {}
                wdi_data[id]['name'] = elem['country']['value']
                
            #check if the value is valid or null, if null then put a np.Nan
            if pd.notnull(elem['value']):
                wdi_data[id][wdi] = float(elem['value']) #everything we are intrested in is a number
            else:
                wdi_data[id][wdi] = np.nan
                
        #lets see what the dataframe looks like
        glob.log.info('got info for %d countries for indicator %s and stored it ' %(num_elems, wdi))
        
def get_data():
    glob.log.info('about to get WB data...')
    df = None
    wdi_data = {}
    
    #first read the indicators which need to be retrieved. These have been selected offline
    #and stored in a file called WDI_Series.csv. Refer to 
    #https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information. 
    #The API end point for all the World Development Indicators (WDI) is 
    #http://api.worldbank.org/indicators?format=json. 
    count = 0
    #create a list of WDI indicators and add each indicator parsed from the file to this list
    wdi_names = []
    with open(glob.WDI_FILE_NAME) as csvfile:
        wdi_list = csv.reader(csvfile)
        for row in wdi_list:
            wdi_names.append(row[0])
            count += 1   
            
    glob.log.info('total number of indicators %d' %(count))
    
    #read to download data for indiviaul indicators
    for wdi in wdi_names:
        get_wdi_data(wdi, wdi_data)
        
    glob.log.info('======= World Bank data ============')
    glob.log.info(json.dumps(wdi_data, indent=glob.INDENT_LEVEL))
    glob.log.info('=======================================================')
    return df

def check_quality_of_data(df):
    glob.log.info('about to get WB data...')
    
def clean_data(df):
    glob.log.info('about to clean data...')

def visualize_data(df):
    glob.log.info('about to visualize WB data...')


def init():
    #nothing for now
    glob.log.info('WB module init complete')
    