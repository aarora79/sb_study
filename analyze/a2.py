# -*- coding: utf-8 -*-

import os
import numpy as np
import statsmodels.api as sm # recommended import according to the docs
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats.mstats as mstats
from common import globals as glob

from datetime import datetime, timedelta
import seaborn as sb  
sb.set_style('darkgrid')
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from dateutil.relativedelta import relativedelta
        
def get_next_month_and_year(prev_date):
    next_month = prev_date.month + 1  
    next_year  = prev_date.year
    if next_month == 13:
        next_month = 1
        next_year += 1     
    return next_year, next_month

def get_timeseries(df, dir_name, scope, scope_label, scope_list):
        #countries = ['US', 'CN', 'CA', 'IN', 'GB', 'JP', 'FR']
    #create a new df based on scope
    if scope == 'all':
        glob.log.info('scope is all so no filtering needed....')
    elif scope == 'continent':
        glob.log.info('scope is continent...')
        glob.log.info(scope_list)
        df = df[df['continent'].isin(scope_list)]    
    elif scope == 'countries':
        glob.log.info('scope is countries...')
        glob.log.info(scope_list)
        df = df[df['country'].isin(scope_list)]
    elif scope == 'US_states':
        glob.log.info('scope is US states...')
        glob.log.info(scope_list)
        df = df[(df['country'] == 'US') & (df['country_subdivision'].isin(scope_list))]
    else:
        glob.log.info('unknown scope -> %s, defaulting to scope=all' %(scope))
        
    #add a new datetime field which holds the DateTime version of the first seent field
    df['first_seen_as_dt'] = pd.to_datetime(df['first_seen'])
    start_date = min(df['first_seen_as_dt'])    
    final_date = max(df['first_seen_as_dt'])
    final_year = final_date.year
    final_month = final_date.month
    
    glob.log.info('start date: %s, final date %s' %(str(start_date), str(final_date)))
    #create a new dataframe to hold the timeseries data
    dft = pd.DataFrame(columns=['date', 'count'])
    dates  = []
    counts = []
    #add the first element
    count = len(df[df['first_seen_as_dt'] == start_date])
    dates.append(start_date)
    counts.append(float(count))
    prev_date = start_date
    
    while True:
        next_year, next_month = get_next_month_and_year(prev_date)        
        if (next_year > final_year) or  (next_year == final_year and next_month > (final_month + 1)):
            glob.log.info('reached end of timeseries data at year=%d, month=%d' %(next_year, next_month))
            break
        next_date = datetime(next_year, next_month, 1)
        count += len(df[(df['first_seen_as_dt'] > prev_date) & (df['first_seen_as_dt'] <= next_date)])
        #glob.log.info('date %s, count %d' %(next_date, count))
        dates.append(next_date)
        counts.append(float(count))
        #move to the next date
        prev_date = next_date
    
    dft['date']  = dates
    dft['count'] = counts
    fname = os.path.join(dir_name, scope_label + '_timeseries.csv')
    dft.to_csv(fname, index=False)
    dft = dft.set_index('date')
    return dft, dates
    
def explore_timeseries(df, scope, scope_label, scope_list, order=(2, 1, 2)):    
    #create subdir for the scope so that all plots can be kept in that directory
    dir_name = os.path.join(glob.OUTPUT_DIR_NAME, glob.TSA_DIR, scope_label)
    os.makedirs(dir_name, exist_ok = True)
    
    #et the series to be analyzed    
    dft, dates = get_timeseries(df, dir_name, scope, scope_label, scope_list)
    
    #plot it 
    dft['count'].plot(figsize=(16, 12))  
    fname = os.path.join(dir_name, 'num_stores.png')
    plt.savefig(fname)
    
    decomposition = seasonal_decompose(dft['count'], model='additive', freq=5)  
    fig = plt.figure()  
    fig = decomposition.plot()  
    fname = os.path.join(dir_name, 'decomposition.png')
    plt.savefig(fname)
    
    #store the df column as a time series, for easier processing
    ts = dft['count']    
    #take a log of the series and then a difference of the logs, this is needed
    #to make the series stationary
    ts_log = np.log(dft['count'])
    ts_log_diff = ts_log - ts_log.shift()
    
    #we choose the ARIMA model on the log of the series
    model = ARIMA(ts_log, order=order)  
    results_ARIMA = model.fit(disp=-1)  
    
    #plot the differences and overlay the fitted values to get a sense
    #of how good the model is
    fig = plt.figure()  
    plt.plot(ts_log_diff)
    plt.plot(results_ARIMA.fittedvalues, color='red')
    plt.title('RSS: %.4f'% sum((results_ARIMA.fittedvalues-ts_log_diff)**2))
    fname = os.path.join(dir_name, 'log_diff_and_fitted_values.png')
    plt.savefig(fname)
    
    #now begin converting the fitted values into the original scale
    predictions_ARIMA_diff = pd.Series(results_ARIMA.fittedvalues, copy=True)    
    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()    
    
    #retrieve the log of the predicted values by adding the cumulative sum to the original
    #starting value
    predictions_ARIMA_log = pd.Series(ts_log.ix[0], index=ts_log.index)    
    predictions_ARIMA_log = predictions_ARIMA_log.add(predictions_ARIMA_diff_cumsum,fill_value=0)
    
    #all done, now recreate the entire series to the original scale
    fig = plt.figure()  
    predictions_ARIMA = np.exp(predictions_ARIMA_log)
    ax=plt.gca()
    plt.plot(ts, label='Actual')
    plt.ylabel('Number of stores')
    ax = predictions_ARIMA.plot(ax=ax, style='r--', label='Predicted');
    plt.title('RMSE: %.4f'% np.sqrt(sum((predictions_ARIMA-ts)**2)/len(ts)))
    ax.legend()
    fname = os.path.join(dir_name, 'orig_with_fitted_values.png')
    plt.savefig(fname)
    
    #create dates for the next one year
    next_year, next_month = get_next_month_and_year(dates[-1])
    start = datetime(next_year, next_month, 1)
    date_list = [start + relativedelta(months=x) for x in range(0,12)]
    future = pd.DataFrame(index=date_list, columns= dft.columns)
    original_len_of_ts = len(dft)
    dft = pd.concat([dft, future])
    #for some reason we have to provide the start and end as integers
    #and only then it works...dates as strings do not work, so we do this
    #roundabout thing of providing integers as index and then changing the
    #index to date strings once we have the predicted values..
    #we predict next 12 months of data
    predict_counts = results_ARIMA.predict(start=original_len_of_ts-1, end=original_len_of_ts+10, dynamic=True)
    predict_counts.index = date_list
    predict_counts = results_ARIMA.fittedvalues.append(predict_counts)    
    
    predictions_ARIMA_diff = pd.Series(predict_counts, copy=True)
    
    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()

    ts_log = np.log(dft['count'])
    predictions_ARIMA_log = pd.Series(ts_log.ix[0], index=ts_log.index)
    predictions_ARIMA_log = predictions_ARIMA_log.add(predictions_ARIMA_diff_cumsum,fill_value=0)
    
    predictions_ARIMA = np.exp(predictions_ARIMA_log)
    
    fig = plt.figure()
    ax=plt.gca()
    plt.plot(ts, label='Actual')
    plt.ylabel('Number of stores')
    ax = predictions_ARIMA.plot(ax=ax, style='r--', label='Predicted');
    plt.title('Forecasted number of stores')
    ax.legend()
    fname = os.path.join(dir_name, 'orig_with_predicted_values.png')
    plt.savefig(fname)
    plt.close('all')
    
    fname = os.path.join(dir_name, scope_label + '_timeseries_w_predictions.csv')
    predictions_ARIMA.to_csv(fname, index_label='date', header=True)
    
def run():
    glob.log.info('about to begin additional analysis...')

    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.SB_CSV_FILE_W_FEATURES)
    df_sb = pd.read_csv(fname)
    
    #explore the following combinations
    explore_timeseries(df_sb, 'all', 'World', None, (2, 1, 1)) #the entire world
                                                               #found by trial and error -> 2,1,1 works better
    
    explore_timeseries(df_sb, 'continent', 'Africa', ['Africa']) #the continent of Africa
    
    explore_timeseries(df_sb, 'US_states', 'US_NY', ['NY']) #the state of New York
    
    explore_timeseries(df_sb, 'countries', 'IN', ['IN'])   #India
    
    explore_timeseries(df_sb, 'countries', 'GB', ['GB']) #the U.K.
    
    explore_timeseries(df_sb, 'countries', 'US_CN', ['US', 'CN']) #the U.S. and China combined
    
if __name__ == "__main__":
    # execute only if run as a script
    run(sys.argv)   
