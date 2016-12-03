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
    #p2 = 'IC.BUS.EASE.XQ'
    p1 = 'ST.INT.ARVL'
    p2 = 'IT.NET.USER.P2'
    
    data = { p1: [], p2: [] }
    
    for i in range(len(df)):
        country = df.ix[i]
        data[p1] += [country[p1]]*country['Num.Starbucks.Stores']
        data[p2] += [country[p2]]*country['Num.Starbucks.Stores']
    
    #df2 = pd.DataFrame(data)
    #sns.jointplot(x=p1, y=p2, data=df2, kind='kde')
    #plt.show()
    
    import plotly.plotly as py
    import plotly.graph_objs as go
    x = data[p1]
    y = data[p2]
    
    trace1 = go.Scatter(
        x=x, y=y, mode='markers', name='points',
        marker=dict(color='rgb(102,0,0)', size=2, opacity=0.4)
    )
    trace2 = go.Histogram2dcontour(
        x=x, y=y, name='density', ncontours=20,
        colorscale='Hot', reversescale=True, showscale=False
    )
    trace3 = go.Histogram(
        x=x, name='x density',
        marker=dict(color='rgb(102,0,0)'),
        yaxis='y2'
    )
    trace4 = go.Histogram(
        y=y, name='y density', marker=dict(color='rgb(102,0,0)'),
        xaxis='x2'
    )
    data = [trace1, trace2, trace3, trace4]
    
    layout = go.Layout(
        showlegend=False,
        autosize=False,
        width=600,
        height=550,
        xaxis=dict(
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        margin=dict(
            t=50
        ),
        hovermode='closest',
        bargap=0,
        xaxis2=dict(
            domain=[0.85, 1],
            showgrid=False,
            zeroline=False
        ),
        yaxis2=dict(
            domain=[0.85, 1],
            showgrid=False,
            zeroline=False
        )
    )
    
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='2dhistogram-2d-density-plot-subplots')       
        
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
    
