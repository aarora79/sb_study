# -*- coding: utf-8 -*-

import os
import numpy as np
import statsmodels.api as sm # recommended import according to the docs
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats.mstats as mstats
from common import globals as glob
import seaborn as sns
sns.set(color_codes=True)
from scipy import stats

BIN_SIZE = 5

def draw_hist(df, country, name):
    plt.cla()
    plt.figure(1, figsize=(9, 6))
    x = df[country].dropna().values   
    bins = np.linspace(0, (max(x)), (max(x)/BIN_SIZE))    
    #plt.hist(x, bins, alpha=0.5, label=[country])
    sns.distplot(x, bins=bins, kde=False, fit=stats.erlang);
    plt.legend(loc='upper right')
    plt.title('Histogram for distribution of Starbucks stores across cities in ' + name)
    
    dname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', country)
    os.makedirs(dname, exist_ok=True)
    fname = os.path.join(dname, 'stores_hist.png')
    plt.savefig(fname)

def draw_ecdf(df, country, name):    
    #ecdf  
    # Create a figure instance
    plt.cla()
    plt.figure(1, figsize=(9, 6))
    x = df[country].dropna().values  
    ecdf = sm.distributions.ECDF(x)        
    y = ecdf(x)
    plt.step(x, y)
    ax = plt.gca()
    ax.grid(True)
    major_ticks = np.arange(0, 1, 0.1)                                              
    #minor_ticks = np.arange(0, 101, 5)      
    ax.set_yticks(major_ticks)                                                       
    #ax.set_yticks(minor_ticks, minor=True)  
    major_ticks = np.arange(0, max(x), BIN_SIZE*5)  
    ax.set_xticks(major_ticks)   
    plt.title('ECDF for distribution of Starbucks stores across cities in ' + name)
    dname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', country)
    os.makedirs(dname, exist_ok=True)
    fname = os.path.join(dname, 'stores_ecdf.png')
    plt.savefig(fname)

def draw_combined_hist(df, countries, country_names, winsorize=False):
    #make a combined histogram    
    plt.cla()    
    plt.figure(1, figsize=(5, 3))   
    
    TRIM = 0.05 if winsorize == True else 0.0
    m = 0   
    #get the max value amongsts all series that we are going to plot
    for c in countries:
        x = df[c].dropna().values
        x=mstats.winsorize(x,(0, TRIM))
        if max(x) > m:
            m = max(x)      
    #we have the max value, now plot each series, bins are decided based on max
    i = 0        
    for c in countries:
        x = df[c].dropna().values
        x=mstats.winsorize(x,(0, TRIM))
        bins = np.linspace(0, m, m)   
        plt.hist(x, bins, alpha=0.5, label=country_names[i])
        i += 1
    
    plt.legend(loc='upper right')
    plt.title('Histogram for distribution of Starbucks stores\n across cities in a country')
    name = 'hist.png' if winsorize == False else 'winsorized_hist.png'
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', name)
    plt.savefig(fname)
    #plt.show()

def draw_combined_boxplot(df, countries, country_names, winsorize=False):
    plt.cla()
    # Create the boxplot
    plt.figure(1, figsize=(5, 6))
    TRIM = 0.05 if winsorize == True else 0.0
    data = []
    for c in countries:
        x = df[c].dropna().values
        x = mstats.winsorize(x,(0, TRIM))
        data.append(x)
    plt.boxplot(data, labels=country_names, whis='range') 
    plt.title('Boxplot for distribution of Starbucks stores\n across cities in a country')
    #plt.xticks(rotation = 45)

    # Save the figure
    name = 'boxplot.png' if winsorize == False else 'winsorized_boxplot.png'
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', name)
    plt.savefig(fname)        
           
def explore_distribution_across_countries(df):
    countries = ['US', 'GB', 'AE', 'KW', 'KR', 'CA']
                 
    country_names = ['United States',        'United Kingdom', 
                     'UAE', 'Kuwait', 
                     'Republic of Korea',    'Canada']   
                     
    df3 = pd.DataFrame(columns=countries)
    
    #kind of kludgy way of doing this but ok..
    max_l = 0
    city_w_max_stores = []
    count_in_city_w_max_stores = []
    for country in countries:
        df2 = df[df['country'] == country]
        distribution = df2['city'].value_counts()
        l = len(distribution)
        if l > max_l:
            max_l = l   
        glob.log.info('Max number of stores (%s, %d)' %(distribution.index[0], distribution.ix[0])) 
        city_w_max_stores.append(distribution.index[0])
        count_in_city_w_max_stores.append(distribution.ix[0])
    df_temp = pd.DataFrame(columns = ['country', 'city_with_most_starbucks_stores', 'count_in_city_with_most_stores'])
    df_temp['country'] = country_names
    df_temp['city_with_most_starbucks_stores'] = city_w_max_stores
    df_temp['count_in_city_with_most_stores'] = count_in_city_w_max_stores
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', 'cities_withmost_stores.csv')
    df_temp.to_csv(fname, index=False, encoding='utf-8')    
    
    for country in countries:
        df2 = df[df['country'] == country]
        distribution = df2['city'].value_counts()
        #df3 = pd.DataFrame(columns=['stores'])
        values = distribution.values
        if len(values) < max_l:
            padding = max_l - len(values)
            values = np.append(values, np.repeat(np.nan, padding))
            
        df3[country] = values
        
    #now make plots for individual countries  and combinations  
    #histogram
    i = 0    
    for country in countries:        
        draw_hist(df3, country, country_names[i])
        draw_ecdf(df3, country, country_names[i])    
        i += 1
    
    #combined histogram, followed by a winsorized version
    draw_combined_hist(df3, countries, country_names)
    draw_combined_hist(df3, countries, country_names, True)
    
    #make a boxplot,followed by a winsorized version
    draw_combined_boxplot(df3, countries, country_names)
    draw_combined_boxplot(df3, countries, country_names, True)
           
def run():
    glob.log.info('about to begin additional analysis...')
    
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.COMBINED_DATASET_CSV)
    df_combined = pd.read_csv(fname)

    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.SB_CSV_FILE_W_FEATURES)
    df_sb = pd.read_csv(fname)
    
    explore_distribution_across_countries(df_sb)
    
if __name__ == "__main__":
    # execute only if run as a script
    run(sys.argv)   
