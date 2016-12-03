# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 14:59:06 2016

@author: aarora
"""

import plotly.plotly as py
from plotly.graph_objs import *
#py.sign_in('username', 'api_key')
trace1 = Scatter(
    x=['2013-12-08 22:41:59', '2014-01-01', '2014-02-01', '2014-03-01', '2014-04-01', '2014-05-01', '2014-06-01', '2014-07-01', '2014-08-01', '2014-09-01', '2014-10-01', '2014-11-01', '2014-12-01', '2015-01-01', '2015-02-01', '2015-03-01', '2015-04-01', '2015-05-01', '2015-06-01', '2015-07-01', '2015-08-01', '2015-09-01', '2015-10-01', '2015-11-01', '2015-12-01', '2016-01-01', '2016-02-01', '2016-03-01', '2016-04-01', '2016-05-01', '2016-06-01', '2016-07-01', '2016-08-01', '2016-09-01', '2016-10-01', '2016-11-01', '2016-12-01'],
    y=[29.0, 30.0, 31.0, 35.0, 39.0, 39.0, 43.0, 44.0, 48.0, 50.0, 51.0, 55.0, 55.0, 60.0, 61.0, 66.0, 66.0, 66.0, 71.0, 72.0, 74.0, 74.0, 75.0, 76.0, 77.0, 78.0, 78.0, 80.0, 81.0, 83.0, 83.0, 83.0, 83.0, 84.0, 84.0, 84.0, 85.0],
    fill='tozeroy',
    line=Line(
        shape='spline',
        smoothing=1.3,
        width=0.5
    ),
    mode='lines',
    name='IN',
    visible=True,
    xaxis='x1',
    yaxis='y1',
    )
trace2 = Scatter(
    x=['2013-12-08 22:41:59', '2014-01-01', '2014-02-01', '2014-03-01', '2014-04-01', '2014-05-01', '2014-06-01', '2014-07-01', '2014-08-01', '2014-09-01', '2014-10-01', '2014-11-01', '2014-12-01', '2015-01-01', '2015-02-01', '2015-03-01', '2015-04-01', '2015-05-01', '2015-06-01', '2015-07-01', '2015-08-01', '2015-09-01', '2015-10-01', '2015-11-01', '2015-12-01', '2016-01-01', '2016-02-01', '2016-03-01', '2016-04-01', '2016-05-01', '2016-06-01', '2016-07-01', '2016-08-01', '2016-09-01', '2016-10-01', '2016-11-01', '2016-12-01'],
    y=[27.0, 30.0, 30.0, 32.0, 33.0, 33.0, 36.0, 36.0, 36.0, 36.0, 36.0, 39.0, 39.0, 40.0, 40.0, 40.0, 42.0, 42.0, 43.0, 46.0, 46.0, 47.0, 50.0, 52.0, 53.0, 56.0, 58.0, 61.0, 62.0, 63.0, 63.0, 63.0, 63.0, 65.0, 70.0, 70.0, 71.0],
    fill='tozeroy',
    line=Line(
        shape='spline',
        smoothing=1.3,
        width=0.5
    ),
    mode='lines',
    name='IE',
    visible=True,
    xaxis='x2',
    yaxis='y2',
)
trace3 = Scatter(
    x=['2013-12-08 22:41:59', '2014-01-01', '2014-02-01', '2014-03-01', '2014-04-01', '2014-05-01', '2014-06-01', '2014-07-01', '2014-08-01', '2014-09-01', '2014-10-01', '2014-11-01', '2014-12-01', '2015-01-01', '2015-02-01', '2015-03-01', '2015-04-01', '2015-05-01', '2015-06-01', '2015-07-01', '2015-08-01', '2015-09-01', '2015-10-01', '2015-11-01', '2015-12-01', '2016-01-01', '2016-02-01', '2016-03-01', '2016-04-01', '2016-05-01', '2016-06-01', '2016-07-01', '2016-08-01', '2016-09-01', '2016-10-01', '2016-11-01', '2016-12-01'],
    y=[1140.0, 1155.0, 1214.0, 1248.0, 1261.0, 1266.0, 1307.0, 1332.0, 1378.0, 1400.0, 1429.0, 1486.0, 1534.0, 1608.0, 1644.0, 1677.0, 1679.0, 1679.0, 1746.0, 1792.0, 1826.0, 1857.0, 1931.0, 1963.0, 2002.0, 2087.0, 2133.0, 2170.0, 2197.0, 2225.0, 2282.0, 2326.0, 2339.0, 2417.0, 2467.0, 2560.0, 2561.0],
    fill='tozeroy',
    line=Line(
        shape='spline',
        smoothing=1.3,
        width=0.5
    ),
    mode='lines',
    name='CN',
    visible=True,
    xaxis='x3',
    yaxis='y3',
)

data = Data([trace1, trace2, trace3])


#data = Data([trace1, trace2, trace3])
layout = Layout(
    autosize=False,
    height=1000,
    showlegend=False,
    title='<b>Timeseries for number Starbucks stores 2013-2016</b><br>Countries with maximum percentage increase in Starbucks stores',
    width=800,
    xaxis1=XAxis(
        anchor='y1',
        autorange=True,
        domain=[0, 0.25],
        mirror=False,
        showgrid=True,
        showline=True,
        showticklabels=False,
        showticksuffix='none',
        title='IN',
        zeroline=False
    ),
    xaxis2=XAxis(
        anchor='y2',
        autorange=True,
        domain=[0.33, 0.6],
        mirror=False,
        showgrid=True,
        showline=True,
        showticklabels=False,
        showticksuffix='none',
        title='IE',
        zeroline=False
    ),
    xaxis3=XAxis(
        anchor='y3',
        autorange=True,
        domain=[0.7, 1.0],
        showgrid=True,
        showline=True,
        showticklabels=False,
        showticksuffix='none',
        title='CN',
        zeroline=False
    ),
    yaxis1=YAxis(
        anchor='x1',
        autorange=True,
        domain=[0.8, 1],
        mirror=False,
        showgrid=True,
        showline=True,
        showticklabels=True,
        showticksuffix='last',
        title='',
        type='linear',
        zeroline=False
    ),
    yaxis2=YAxis(
        anchor='x2',
        autorange=True,
        domain=[0.8, 1],
        mirror=False,
        showgrid=True,
        showline=True,
        showticklabels=True,
        showticksuffix='last',
        ticks='',
        title='',
        type='linear',
        zeroline=False
    ),
    yaxis3=YAxis(
        anchor='x3',
        autorange=True,
        domain=[0.8, 1],
        showgrid=True,
        showline=True,
        showticklabels=False,
        showticksuffix='none',
        title='',
        type='linear',
        zeroline=False
    )
)
fig = Figure(data=data, layout=layout)
plot_url = py.plot(fig)