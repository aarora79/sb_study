# -*- coding: utf-8 -*-
import pandas as pd
import os
from common import globals as glob
from common import utils
#from matplotlib import style
#style.use("ggplot")
from pandas.tools.plotting import scatter_matrix
from . import clustering
from . import assoc_rule_mining
from . import regression
from . import classification
import matplotlib.pyplot as plt
import scipy.stats as stats


T_TEST_ALPHA = 0.20
NAME_FOR_LOGGER_ANALYSIS_MODULE = 'SBS_ANALYSIS'
POPULATION_MULTIPLIER_FOR_STORE_DENSITY = 100000
#QUANTILES_FOR_BINNING = [0.05, 0.15, 0.20, 0.5, 0.75, 0.9]
#note this is one more than quantiles
#BIN_CATEGORY_NAMES = ['VVL', 'VL', 'L', 'M', 'H', 'VH', 'VVH'] 

QUANTILES_FOR_BINNING = [0.1, 0.20, 0.6, 0.80]
#QUANTILES_FOR_BINNING_SB_STORES = [0.3, 0.8]
#BIN_CATEGORY_NAMES_SB_STORES = ['L', 'M', 'H']
#note this is one more than quantiles
BIN_CATEGORY_NAMES =['VL', 'L', 'M', 'H', 'VH']    

def get_bins(data, quantiles):
    #set up bins using quanties 0.05, 0.15, 0.25, 0.5, 0.75, 0.9
    bins = []    
    for q in quantiles:
        bins.append(data.quantile(q))
    return bins    

def get_bin_category(value, bins, bins_categorical):
    for i in range(len(bins)):
        if value <= bins[i]:
            return bins_categorical[i]
    return bins_categorical[-1] #did not fall into any bin so it is the last one since bins are in ascending order
        
def add_derived_features(df, df_SB):
    #we want to add the following features
    #number of starbucks stores
    #categorization of number of starbucks stores VL, L, M, H, VH
    #number of starbucks stores on airports
    #Exists in multiple cities
    #Ownership model

    num_sb_total             = []
    num_sb_on_airports       = []
    exists_in_multiple_cities= []
    ownership_type_mixed     = []  
    multiple_brands          = []
    continent                = []
    
    #df is the combined df, already only contains countries with starbucks
    for i in range(len(df)):
        country = df.iloc[i]
        cc = country['country_code']
        
        #number of starbucks
        store_count = df_SB['country'].value_counts()[cc]
        num_sb_total.append(store_count)
        #how many on airports          
        num_sb_on_airports.append(sum(df_SB[df_SB['country'] == cc]['on_airport']))
        
        #all of these follow the same format, basically check if more than 1 unique value
        exists_in_multiple_cities.append(str(len(df_SB[df_SB['country'] == cc]['city'].unique()) > 1))
        multiple_brands.append(str(len(df_SB[df_SB['country'] == cc]['brand'].unique()) > 1))
        ownership_type_mixed.append(str(len(df_SB[df_SB['country'] == cc]['ownership_type'].unique()) > 1))
        
        #continent        
        continent.append(df_SB[df_SB['country'] == cc]['continent'].iloc[0])  
        
    #all set to add the new columns
    #add categorical fields for international tourist arrival
    bins = get_bins(df['ST.INT.ARVL'], QUANTILES_FOR_BINNING)
    df['ST.INT.ARVL.Categorical'] = [get_bin_category(n, bins, BIN_CATEGORY_NAMES) for n in df['ST.INT.ARVL']]
           
    #add a categorical field for population      
    bins = get_bins(df['SP.POP.TOTL'], QUANTILES_FOR_BINNING)
    df['SP.POP.TOTL.Categorical'] = [get_bin_category(n, bins, BIN_CATEGORY_NAMES) for n in df['SP.POP.TOTL']]
        
    df['Num.Starbucks.Stores']             = num_sb_total
    bins = get_bins(df['Num.Starbucks.Stores'], QUANTILES_FOR_BINNING)
    df['Num.Starbucks.Stores.Categorical'] = [get_bin_category(n, bins, BIN_CATEGORY_NAMES) for n in df['Num.Starbucks.Stores']]
    
    #SBSD -> Starbucks store density i.e. number of Starbucks store per 100,000 people    
    df['Starbucks.Store.Density'] = (df['Num.Starbucks.Stores']*POPULATION_MULTIPLIER_FOR_STORE_DENSITY)/df['SP.POP.TOTL']    
    bins = get_bins(df['Starbucks.Store.Density'], QUANTILES_FOR_BINNING)
    df['Starbucks.Store.Density.Categorical'] = [get_bin_category(n, bins, BIN_CATEGORY_NAMES) for n in df['Starbucks.Store.Density']]
    
    df['Num.Starbucks.Stores.On.Airports'] = num_sb_on_airports
    df['Exists.In.Multiple.Cities']        = exists_in_multiple_cities
    df['Ownership.Type.Mixed']             = ownership_type_mixed
    df['continent']                        = continent 
    df['MultipleBrands']                   = multiple_brands    
    
    
        
         
    return df
    
def combine_datasets():
    glob.log.info('combining datasets...')
    #read WB final
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.WB_CSV_FILE_W_FEATURES)
    df_WB = pd.read_csv(fname)

    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.SB_CSV_FILE_W_FEATURES)
    df_SB = pd.read_csv(fname)
    
    #create a new dataset, by only keeping those countries that have a starbucks store
    countries_w_sb = df_SB['country'].unique()
    df = df_WB[df_WB['country_code'].isin(countries_w_sb)]
    
    #now is a good time to check data quality score
    dqs = utils.calc_dqs(df)
    
    return df, dqs, df_WB, df_SB 
    
def clean_combined_dataset(df):
    ###############################################################
    #CLEANING STRATEGY 1: remove features which are less than 90% full
    ###############################################################
    #now remove the columns that are less than FEATURE_DENSITY_THRESHOLD (90%) full
    for col in df.columns:
        density = (df[col].count())/(len(df))
        if density < glob.FEATURE_DENSITY_THRESHOLD:
            glob.log.info('%s is only %f full, dropping it...' %(col, density*100))
            df = df.drop(col, 1)
     
    ###############################################################
    #CLEANING STRATEGY 2: replace empty cells with mean of the column
    #                     this is ok because we visually inspected the 
    #                     data and everything seemed to look like either
    #                     a uniform of normal distribution     
    ###############################################################    
    df = df.fillna(df.mean())
    
    #check dqs again to see improvement
    dqs = utils.calc_dqs(df)
    
    return df, dqs

    

            
def run_t_test(df):
    df_vh = df[(df['ST.INT.ARVL.Categorical'] == 'VH')]['Num.Starbucks.Stores']
    df_row = df[(df['ST.INT.ARVL.Categorical'] == 'H') | (df['ST.INT.ARVL.Categorical'] == 'M') | (df['ST.INT.ARVL.Categorical'] == 'VL') | (df['ST.INT.ARVL.Categorical'] == 'L')]['Num.Starbucks.Stores']
    
    result = stats.ttest_ind(a = df_vh, b = df_row, equal_var = False)
    glob.log.info(result)
    if result.pvalue < T_TEST_ALPHA:
        glob.log.info('Null hypothesis for %s rejected because p value is of %f is less than 0.95' %('ST.INT.ARVL.Categorical', result.pvalue))
    else:
        glob.log.info('Null hypothesis for %s accepted because p value is of %f is greater than equal to 0.95' %('ST.INT.ARVL.Categorical', result.pvalue))
    #store t-test results in a file
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.REGRESSION_DIR, glob.T_TEST_RESULT) 
    f = open(fname, 'w')
    f.write('\"Hypothesis\",\"No difference between average number of Starbucks stores in countries with Very high and high number of international tourist Vs Rest of the world\"\n')
    f.write('\"T-statistic, p-value\",\"%f,%f\"\n' %(result.statistic, result.pvalue))
    f.close()
    
def do_eda(df):
    feature_list = ['Num.Starbucks.Stores', 'IT.NET.USER.P2', 'ST.INT.ARVL', 'SP.POP.TOTL']
    
    #calc Pearson's r for some important features to see if there is a relationship
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.COMBINED_R)
    utils.calc_r('combined', fname, df, feature_list)
    
    #make a scatter matrix for the combined dataset just to see histograms and relationship
    #between some important features 
    scatter_matrix(df[feature_list], diagonal='kde')
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.COMBINED_SCATTER_MATRIX)
    plt.savefig(fname)
    plt.clf()
    
    #also a histogram would be nice, since we used kernel density estimator in the scatter matrix
    df[feature_list].hist()
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.EDA_DIR, glob.COMBINED_HISTOGRAM)
    plt.savefig(fname)
    plt.clf()
    
    #make a scatter plot for everything
    numeric_features = []
    for col in df.columns:
        try:
            x=df[col].iloc[0] 
            float(x)#typecast the data to float to test if it is numeric
        except:
            glob.log.info('%s is not a numeric feature, ignoring' %(col))
        else:
            numeric_features.append(col)
    glob.log.info('making scatter plots for Num.Starbucks.Stores w.r.t to all WDI indicators...(could take a minute)')         
    #df = df[df['country_code'] != 'US']    
    for col in numeric_features:
        plt.figure()
        fname = os.path.join(glob.OUTPUT_DIR_NAME, 'scatter', col + '.png')
        df.plot.scatter(col, 'Num.Starbucks.Stores')
        plt.savefig(fname)
        plt.close('all')
        
def run():
    glob.log.info('Begin SB + WB data analysis..')
    glob.log.info('run analysis...')
    df,dqs1,df_WB,df_SB = combine_datasets()
    
    df,dqs2 = clean_combined_dataset(df)
    
    #add derived features from SB dataset
    df = add_derived_features(df, df_SB)
    
    #all done , store it in a csv
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.COMBINED_DATASET_CSV)
    glob.log.info('writing the combined WB and SB dataset to a file')
    glob.log.info(df.head())
    df.to_csv(fname, index=False)    
    
    #log the dqs to a file for easy access later on if needed
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.DQS_DIR, 'dqs_combined_dataset.csv')
    f = open(fname, 'w')
    f.write('dataset,before_cleaing, after_cleaning\n')
    f.write('WDI+SB,%f,%f' %(dqs1,dqs2))
    f.close()
    
    #EDA on the combined dataset
    do_eda(df)
    
    #Clustering
    clustering.run(df)
    
    #association rule mining
    assoc_rule_mining.run(df)
    
    #t-test
    run_t_test(df)
    
    #run linear and polynomial regression, multivariate as well     
    regression.run(df)
    
    #classification and done...
    classification.run(df)
    