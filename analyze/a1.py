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

def draw_hist(df, country):
    plt.cla()
    plt.figure(1, figsize=(9, 6))
    x = df[country].dropna().values   
    bins = np.linspace(0, (max(x)), (max(x)/BIN_SIZE))    
    #plt.hist(x, bins, alpha=0.5, label=[country])
    sns.distplot(x, bins=bins, kde=False, fit=stats.erlang);
    plt.legend(loc='upper right')
    
    dname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', country)
    os.makedirs(dname, exist_ok=True)
    fname = os.path.join(dname, 'stores_hist.png')
    plt.savefig(fname)

def draw_ecdf(df, country):    
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
    dname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', country)
    os.makedirs(dname, exist_ok=True)
    fname = os.path.join(dname, 'stores_ecdf.png')
    plt.savefig(fname)

def draw_combined_hist(df, countries)    :
    #make a combined histogram    
    plt.cla()    
    plt.figure(1, figsize=(5, 3))   
    
    TRIM = 0.05
    m = 0    
    for c in countries:
        x = df[c].dropna().values
        x=mstats.winsorize(x,(0, TRIM))
        if max(x) > m:
            m = max(x)        
    for c in countries:
        x = df[c].dropna().values
        x=mstats.winsorize(x,(0, TRIM))
        bins = np.linspace(0, m, m)   
        plt.hist(x, bins, alpha=0.5, label=c)
    
    plt.legend(loc='upper right')
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', 'hist.png')
    plt.savefig(fname)
    plt.show()

def draw_combined_boxplot(df):
    plt.cla()
    # Create the boxplot
    plt.figure(1, figsize=(9, 6))
    TRIM=95
    #for c in df.columns[1:]:
    #    x = df[c].dropna().values
    #    p = np.percentile(x, TRIM)
    #    df[df[c] > p]=p
        #df[c] = mstats.winsorize(x,(0, TRIM))
    #    print(df[c])
    ax = df.boxplot(return_type='axes')
    #ax.set_yscale("log", nonposy='clip')
    # Save the figure
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, 'more', 'boxplot.png')
    plt.savefig(fname)        
           
def explore_distribution_across_countries(df):
    countries = ['US', 'CN', 'CA', 'IN', 'GB', 'JP', 'FR']
    
    df3 = pd.DataFrame(columns=countries)
    
    #kind of kludgy way of doing this but ok..
    max_l = 0
    for country in countries:
        df2 = df[df['country'] == country]
        distribution = df2['city'].value_counts()
        l = len(distribution)
        if l > max_l:
            max_l = l
            
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
    for country in countries:        
        draw_hist(df3, country)
        draw_ecdf(df3, country)       
    
    #combined histogram
    draw_combined_hist(df3, countries)
    
    #make a boxplot
    draw_combined_boxplot(df3)
           
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
