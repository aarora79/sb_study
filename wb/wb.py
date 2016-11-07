# -*- coding: utf-8 -*-
import requests as req
import pandas as pd
#import json
import csv
import os
import matplotlib.pyplot as plt
from pandas.tools.plotting import scatter_matrix

from common import globals as glob
from common import utils
from . import wb_check_quality as cq

def get_WDI_CSV_FILE_NAME(year):
    csv_file_name = glob.WDI_CSV_FILE 
    csv_file_name = csv_file_name.replace('__YEAR__', year)
    return csv_file_name
    
def get_wdi_name_list():
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
    return wdi_names     
    
def get_wdi_data(wdi, wdi_data, year):
    
    #example URL http://api.worldbank.org/countries/ALL/indicators/IC.REG.DURS?date=2015&format=json&per_page=10000
    #the WB_API_ENDPOINT has a token called __YEAR__ which needs to be replaced with the exact year    
    api = glob.WB_API_ENDPOINT + wdi + glob.WB_API_SUFFIX
    api = api.replace('__YEAR__', year)
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
                wdi_data[id][wdi] = ''
                
        #lets see what the dataframe looks like
        glob.log.info('got info for %d countries for indicator %s and stored it ' %(num_elems, wdi))
                
def get_data():
    glob.log.info('about to get WB data...')
    df = None
    wdi_data = {}
    
    wdi_names = get_wdi_name_list()
    #read to download data for individual indicators
    year = str(glob.WB_YEAR_LATEST)
    for wdi in wdi_names:
        get_wdi_data(wdi, wdi_data, year)
        
    csv_file_name = get_WDI_CSV_FILE_NAME(year)    
    glob.log.info('WB data downloaded, going to save it into ' + csv_file_name)
    #glob.log.info(json.dumps(wdi_data, indent=glob.INDENT_LEVEL))
    #dump the dictionary into a csv file
    utils.write_dict_to_csv(wdi_data, csv_file_name)
    
    #also save this data in dictionary form in glob because this would be useful
    #at the time of feature creation..ultimately we will recreate this dict from 
    #a csv file so that we dont have to ingest the data everytime we run this 
    #for now its ok, this will be modified in the next phase....
    glob.wb['wdi_data'] = wdi_data
    
    #now read the data from the CSV file we just wrote into a dataframe
    df = pd.read_csv(os.path.join(glob.OUTPUT_DIR_NAME, csv_file_name), encoding = 'utf-8')
    #del df['Unnamed'] #an extra column gets inserted at the end because we put a ',' after every field in the csv
    #lets see what the dataframe looks like
    glob.log.info('columns in the data frame -> ' + str(df.columns))
    glob.log.info('the dataframe contains %d rows and %d columns' %(df.shape[0], df.shape[1]))
    return df

def check_quality_of_data(df):
    glob.log.info('about to get WB data...')
    
    #overall quality metrics
    qual = cq.check(df)
    glob.log.info('======= quality metrics for WB data ============')
    #glob.log.info(json.dumps(qual, indent=glob.INDENT_LEVEL))
    glob.log.info(qual)
    glob.log.info('=======================================================')
    return qual
    
def clean_data(df, qual):
    glob.log.info('about to clean data...')
    df2 = None
    wdi_data = {}
    
    #we know that the WB data does not have values for the latest year so go with the 
    #values of the same wDI for the previous year and then merge it in the original df
    wdi_names = get_wdi_name_list()
    #read to download data for individual indicators
    year = str(glob.WB_YEAR_BEFORE_LATEST)
    for wdi in wdi_names:
        get_wdi_data(wdi, wdi_data, year)
    #glob.log.info(json.dumps(wdi_data, indent=glob.INDENT_LEVEL))
    #dump the dictionary into a csv file
    csv_file_name = get_WDI_CSV_FILE_NAME(year)    
    utils.write_dict_to_csv(wdi_data, csv_file_name)
    
    #also save this data in dictionary form in glob because this would be useful
    #at the time of feature creation..ultimately we will recreate this dict from 
    #a csv file so that we dont have to ingest the data everytime we run this 
    #for now its ok, this will be modified in the next phase....
    glob.wb['wdi_data'] = wdi_data
    
    #now read the data from the CSV file we just wrote into a dataframe
    df2 = pd.read_csv(os.path.join(glob.OUTPUT_DIR_NAME, csv_file_name), encoding = 'utf-8')  
    
    #merge the two dataframes so that the null values in the original df
    #are replaced with values from the new df
    #done like the following code but at this time this its ok..there is definitely a 
    #better less verbose way of doing this.
    glob.log.info('this is going to take about a minute.....')
    for i in range(len(df)):   #this is the df for the latest year that we had read earlier     
        country  = df.ix[i]
        country2 = df2.ix[i]
        if country['country_code'] != country2['country_code']:
            glob.log.error('%s and %s country codes do not match, skipping' %(country['country_code'], country2['country_code']))
            continue
        
        for wdi in country.keys():
            if pd.isnull(country[wdi]) == True and pd.isnull(country2[wdi]) == False:
                country[wdi] = country2[wdi]
        df.ix[i] = country
    df.to_csv(os.path.join(glob.OUTPUT_DIR_NAME, glob.WDI_CSV_FILE_AFTER_CLEANING), index=False)   

    #so we are going to do outlier detection, but we dont need to remove anything 
    #since there is nothing erroneous about the data..we use > 3rd stddev as an outlier
    #criteria which causes a few values to show up as outliers but they really arent so its ok...
    #NOTE: we use a simple statistical technique for outlier detection (i.e. outlier is anything outside
    #      3rd stddev), this works because the data we are dealing with (WDI indicators) is either
    #      coming from a uniform distribution (well defined range in which values are equally likely) or
    #      from a normal distribution (too many factors impact this, no single factor has more role than others, hence normal)
    utils.detect_outliers(df, 'WB', ['name', 'country_code'], 'name')
    
    #check improvement in data quality after cleaning
    qual = check_quality_of_data(df)     
    return df,qual

def create_features(df):
    glob.log.info('about to create features ...')
    #use binning to create a new columns, lets do this for 'IC.BUS.EASE.XQ' which 
    #represents ease of doing business. It is  value from 1 to 180 something..1 being highest
    #lets create bins as follows..note here the bins are being created using context specific
    #information i.e. we know these are good bins for this feature because we know that from
    #knowing what this feature means (rather than say some statistical criterion)
    
    #lets categorize the index into categories
    #VH (Very High): 1 to 10 [both inclusive]
    #H  (High): 11 to 30 [both inclusive]
    #M  (Medium): 31 to 90 [both inclusive]
    #L  (low): 91 to 130 [ both inclusive]
    #VL (Very Low): >= 131 
    
    #bins = [1, 20, 80, 1000]
    bins = [1, 11, 31, 91, 131, 1000] #the last number i.e. 1000 is just an arbitrary high val that
                                      #will never be reached, just meant to be a catch all
    feature_name = 'Ease.Of.Doing.Business'
    group_names = ['VeryHigh', 'High', 'Medium', 'Low', 'VeryLow']
    #group_names = ['High', 'Medium', 'Low']
    df[feature_name] = pd.cut(df['IC.BUS.EASE.XQ'], bins, labels=group_names) 
    
    #after adding this bin, print out the head of the df
    glob.log.info('Updated WB dataframe after adding new feature %s' %(feature_name))
    glob.log.info(df.head())
    #all features added, create an updated CSV file with new features
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.WB_CSV_FILE_W_FEATURES)
    df.to_csv(fname, encoding='utf-8', index = False)
    return df
    
def visualize_data(df):
    glob.log.info('about to visualize WB data...')

def do_eda(df):
    #no categorical variables as the only non-numeric field is country and we know
    #we only have one row per country..exclude the name field also for the same reason
    utils.do_eda(df, os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.WB_EDA_CSV_FILE_NAME),
                 'WB', ['Ease.Of.Doing.Business'], ['country_code', 'name'])
    
    #histograms of 3 features 
    #IC.BUS.EASE.XQ is ease of doing business
    #SP.URB.GROW is rate of urban population growth
    #WP15163_4.1 % of 15+ age group population which uses mobile phones for financial transactions
    feature_list = ['IC.BUS.EASE.XQ', 'SP.URB.GROW', 'WP15163_4.1']
    plt.figure()
    df[feature_list].hist()
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.WB_HISTOGRAM)
    plt.savefig(fname)
    
    #scatter matrix for features that could be related
    #SL.GDP.PCAP.EM.KD is GDP per person employed (constant 2011 PPP $)
    #IT.NET.USER.P2: number of people per 100 people who have used internet via any medium in last 12 months
    feature_list = ['IC.BUS.EASE.XQ', 'SL.GDP.PCAP.EM.KD', 'IT.NET.USER.P2']    
    scatter_matrix(df[feature_list])
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.WB_SCATTER_MATRIX)
    plt.savefig(fname)
    
    #now calculate Pearson's corelation coeff, to do that first we need to create a np array
    #such that we include data only for countries where all 3 features are available
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.WB_PEARSON_CSV)
    utils.calc_r('WB', fname, df, feature_list)
    
def init():
    #nothing for now
    glob.log.info('WB module init complete')
    