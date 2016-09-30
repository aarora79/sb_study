# -*- coding: utf-8 -*-

#global variables used across modules

#dictionaries for starbucks and WB data, empty for now
wb = {}
sb = {} 

#global logger used by all modules and submodules
lg = None

#name to be used for logging module
NAME_FOR_LOGGER = 'SBS'

#API end points
#Starbucks API via SOCRATA
STARBUCKS_API_ENDPOINT = 'https://opendata.socrata.com/resource/xy4y-c4mk.json'
SOCRATA_LIMIT_PER_API_CALL = 50000 #as per the documentation, this is the limit
                                   #of the number of records per call