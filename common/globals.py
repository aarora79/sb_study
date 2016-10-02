# -*- coding: utf-8 -*-
import os
#global variables used across modules

#folder for storing all the output data
OUTPUT_DIR_NAME = os.path.join('.', 'output')

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