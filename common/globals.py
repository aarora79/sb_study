# -*- coding: utf-8 -*-

#global variables used across modules

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

#indentation level for pretty printing dictionaries
INDENT_LEVEL = 2
PRECISION    = 6 #for printing floating point numbers

#CSV file containing country codes, used for validation
CONTRY_CODE_CSV = 'data.csv'