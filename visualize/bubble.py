import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import math
import os
import numpy as np
import statsmodels.api as sm # recommended import according to the docs
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats.mstats as mstats
from common import globals as glob

def get_bubble_size(num_stores):
    size = 4 #anything <= 5 stores is 4 pixels in size
    if num_stores > 10000:
        size = 60
    elif num_stores > 2000:
        size = 30
    elif num_stores > 1000:
        size = 24
    elif num_stores > 500:
        size = 20
    elif num_stores > 100:
        size = 14  
    elif num_stores > 50:
        size = 8  
    elif num_stores > 5:
        size = 6      
    return size
    
def draw(): 
    glob.log.info('about to begin visualization for bubble chart...')

    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.COMBINED_DATASET_CSV)
    df = pd.read_csv(fname)
    hover_text = []
    bubble_size = []
    #'IT.NET.USER.P2', 'ST.INT.ARVL'
    for index, row in df.iterrows():
        text = 'Country, Continent: %s,%s<br>Internet users per 100 people: %f<br>International tourist arrival: %f<br>\
                Number of Starbucks stores: %d' %(row['name'], row['continent'], row['IT.NET.USER.P2'], row['ST.INT.ARVL'], row['Num.Starbucks.Stores'])
        hover_text.append(text)
        
        size = get_bubble_size(row['Num.Starbucks.Stores'])                                        
        bubble_size.append(size)
    
    df['text'] = hover_text
    df['size'] = bubble_size
    traces = []
    color=['rgb(93, 164, 214)', 'rgb(255, 144, 14)',  'rgb(44, 160, 101)', 'rgb(255, 65, 54)', 'rgb(0,100,0)', 'rgb(218,165,32)']
    ci = 0    
    for continent in df['continent'].unique():
        trace = go.Scatter(
            x=df['ST.INT.ARVL'][df['continent'] == continent],
            y=df['IT.NET.USER.P2'][df['continent'] == continent],
            mode='markers',
            name=continent,
            text=df['text'][df['continent'] == continent],
            marker=dict(
                symbol='circle',
                sizemode='diameter',
                #sizeref=1,
                size=df['size'][df['continent'] == continent],
                color = color[ci],
                line=dict(
                    width=2
                ),
            )
        )
        traces.append(trace)
        ci += 1
       
    data = traces
    layout = go.Layout(
        title='Starbucks Stores | Tourist Arrivals Vs Internet Users',
        xaxis=dict(
            title='International tourist arrivals',
            gridcolor='rgb(255, 255, 255)',
            #range=[10, 20],
            #type='log',
            #range=[201000,83767000],
            range=[101000,93767000],
            zerolinewidth=1,
            ticklen=5,
            gridwidth=2,
        ),
        yaxis=dict(
            title='Internet users',
            gridcolor='rgb(255, 255, 255)',
            range=[0,100],
            zerolinewidth=1,
            ticklen=5,
            gridwidth=2,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='starbucks_stores')
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.VIS_DIR, glob.STARBUCKS_BUBBLE_CHART)
    py.image.save_as(fig, filename=fname)

if __name__ == "__main__":
    glob.log.info('drawing bubble chart...')
    # execute only if run as a script
    draw(sys.argv)   