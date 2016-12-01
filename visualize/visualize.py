# -*- coding: utf-8 -*-
import pandas as pd
import os
from common import globals as glob
from . import locations
from . import sb_by_counties
from . import bubble
import numpy as np
import pandas as pd
from scipy import stats, integrate
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)

def parametric_fit(df):
    store_count_per_city = df['city'].value_counts()
    sns.distplot(store_count_per_city, kde=False, fit=stats.erlang);
    plt.show()
    
def density_plot(df):
    #first lets get IC.IMP.COST.CD and IC.BUS.EASE.XQ
    #p1 = 'IC.IMP.COST.CD'
    p1 = 'NE.CON.PETC.ZS'
    p2 = 'IC.BUS.EASE.XQ'
    
    data = { p1: [], p2: [] }
    
    for i in range(len(df)):
        country = df.ix[i]
        data[p1] += [country[p1]]*country['Num.Starbucks.Stores']
        data[p2] += [country[p2]]*country['Num.Starbucks.Stores']
    
    df2 = pd.DataFrame(data)
    sns.jointplot(x=p1, y=p2, data=df2)
    plt.show()
           
        
def draw():
    glob.log.info('about to begin making visualizations...')
    
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.COMBINED_DATASET_CSV)
    df_combined = pd.read_csv(fname)

    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.SB_CSV_FILE_W_FEATURES)
    df_sb = pd.read_csv(fname)
    
    #parameteric fit
    #parametric_fit(df_sb)
    
    density_plot(df_combined)
    
    #plot locations around the world
    locations.draw(df_combined, df_sb)
    
    #US counties heatmap
    sb_by_counties.draw()
    
    #bubble chart
    bubble.draw()
    
