# -*- coding: utf-8 -*-
import os
#global variables used across modules

__VERSION__      = '0.1'
__AUTHOR__       = 'Amit Arora'
__AUTHOR_EMAIL__ = 'aa1603@georgetown.edu'
__PROJECT_NAME_SHORT__ = 'SBS' #Starbucks Study
__PROJECT_NAME_LONG__ = 'A data science tale about a coffee company'

#folder for storing all the output data
OUTPUT_DIR_NAME = os.path.join('.', 'output')

#file to store the data quality score
DSQ_CSV = 'dqs.csv'

#dictionaries for starbucks and WB data, empty for now
wb = {}
sb = {} 

#global logger used by all modules and submodules
log = None

#name to be used for logging module
NAME_FOR_LOGGER = 'SBS'

#API end points
#Starbucks API via SOCRATA
STARBUCKS_API_ENDPOINT = 'https://opendata.socrata.com/resource/xy4y-c4mk.json'
SOCRATA_LIMIT_PER_API_CALL = 50000 #as per the documentation, this is the limit
                                   #of the number of records per call
SB_CSV_FILE = 'SB_data_as_downloaded.csv'  #csv file containing data as downloaded
SB_CSV_FILE_W_FEATURES = 'SB_data_w_features.csv' #csv file with new features added

#country to continent mapping
COUNTRY_TO_CONTINENT_MAPPING_API = 'https://commondatastorage.googleapis.com/ckannet-storage/2012-07-26T090250/Countries-Continents-csv.csv'
COUNTRY_CONTINENET_CSV = 'countries.csv'

#indentation level for pretty printing dictionaries
INDENT_LEVEL = 2
PRECISION    = 6 #for printing floating point numbers

#CSV file containing country codes, used for validation
CONTRY_CODE_CSV = 'data.csv'

#World Bandk development indicators, selected, stored in a csv file
WDI_FILE_NAME = 'WDI_Series.csv'
WB_API_ENDPOINT = 'http://api.worldbank.org/countries/ALL/indicators/'
WB_API_SUFFIX   = '?date=2015&format=json&per_page=10000' #get all data for 2015
                                                          #that is the newest available data
WDI_CSV_FILE    = 'WDI_data_as_downloaded.csv'  #csv file containing data as downloaded