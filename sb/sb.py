# -*- coding: utf-8 -*-
import requests as req
import pandas as pd

from common import globals as glob

def get_data():
    glob.lg.info('about to get SB data...')
    df = None
    
    # Starbucks store location data is available from https://opendata.socrata.com via an API. 
    # The Socrate Open Data API (SODA) end point for this data is
    # https://opendata.socrata.com/resource/xy4y-c4mk.json
    api = glob.STARBUCKS_API_ENDPOINT + '?' + '$limit=' + str(glob.SOCRATA_LIMIT_PER_API_CALL)
    r = req.get(api)
    
    #if the return code is not 200 ok then its an errors
    if r.ok != True:
        glob.lg.error('Error while retrieving information about SB, server sent status code ' + str(r.status_code))
        glob.lg.error('Here is everything that was sent by the server...')
        glob.lg.error(r.text)
    else:            
        #looks like we got the response
        glob.lg.info('successfully received a response from the SB API endpoint ' + api)
        
        #Store the response in a dataframe
        df = pd.DataFrame(r.json())
        
        #lets see what the dataframe looks like
        glob.lg.info('shape of the dataframe: ' + str(df.shape))
        glob.lg.info('the dataframe contains the following columns ' + str(df.columns))
        
    return df

def check_quality_of_data(df):
    glob.lg.info('about to get SB data...')
    
def clean_data(df):
    glob.lg.info('about to clean data...')

def visualize_data(df):
    glob.lg.info('about to visualize SB data...')


def init():
    #nothing for now
    glob.lg.info('SB module init complete')

