# -*- coding: utf-8 -*-
from common import globals as glob
import os
from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool,
  HoverTool, ResetTool, NumeralTickFormatter, PrintfTickFormatter
)
from collections import OrderedDict
import ast
from bokeh.layouts import row, widgetbox
from bokeh.models import CustomJS, Slider
import sys
import numpy as np
from sklearn.preprocessing import normalize
#https://github.com/bokeh/bokeh/issues/2964
MILLION = 1000000
BILLION = 1000000000
def normalize2(x):
    x=np.array(x)
    x=normalize(x[:,np.newaxis], axis=0).ravel()
    return x
    
def get_store_info(df_sb, combined):
    lat = []
    lon = []
    city = []
    name = []
    eodb =[]
    tourists=[]
    tech_exports =[]
    inet_users =[]
    for i in range(len(df_sb)):
        #read location and convert to dictionary
        store = df_sb.ix[i]
        location = store['coordinates']
        try:
            location = ast.literal_eval(location)
            
            lat.append(location['latitude'])
            lon.append(location['longitude'])
            city.append(store['city'])
            name.append(store['name'])
            country = store['country']
            #glob.log.info(country)
            #glob.log.info(df_combined[df_combined['country_code'] == country]['IC.BUS.EASE.XQ'])
            #special handling for Taiwan since it does not exist in WB data
            if country == 'TW':
                eb = 0
                t  = 0
                te = 0
                iu  = 0
            else:    
                eb = combined[country]['IC.BUS.EASE.XQ']
                t  = round(combined[country]['ST.INT.ARVL']/MILLION,2)
                te = round(combined[country]['TX.VAL.TECH.CD']/BILLION,2)
                iu = round(combined[country]['IT.NET.USER.P2'],2)
                
            #glob.log.info(store['country'] + ' --  ' + str(e1))
            eodb.append(eb)
            tourists.append(t)
            tech_exports.append(te)
            inet_users.append(iu)
            
        except Exception as e:
            glob.log.error('Exception while reading lat/long value: ' + str(e))
            #sys.exit(1)
    #normalize some of the fields  
    #tourists=normalize2(tourists)
    #print(max(tourists))
    #tech_exports=normalize2(tech_exports)
    #print(max(tech_exports))
    #inet_users=normalize2(inet_users)
    #print(max(inet_users))
    
    return lat,lon,city,name,eodb,tourists,tech_exports,inet_users

def combined_df_to_dictionary(df):
    d = {}
    for i in range(len(df)):
        country = df.ix[i]
        cc = country['country_code']
        d[cc]={}
        for k in country.keys():
            d[cc][k]=country[k]
    return d        
        
def draw(df_combined, df_sb):
    glob.log.info('creation visualization for starbucks locations around the world...')
    
    #convert combined df to dictionary for faster lookup
    combined_data = combined_df_to_dictionary(df_combined)
    #get lat long
    lat,lon,city,name,eodb,tourists,tech_exports,inet_users = get_store_info(df_sb, combined_data)
    
    
    #set gmap lat/long options to 0 to display the whole world, zoom level 2 works good
    map_options = GMapOptions(lat=0, lng=0, map_type="satellite", zoom=2)
    
    # Google Maps now requires an API key. You can find out how to get one here:
    # https://developers.google.com/maps/documentation/javascript/get-api-key
    API_KEY = "AIzaSyCuT2x39k1XNwp7NdjxfRZKYWSNLm5zcJY"
    
    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(),
        map_options=map_options,
        api_key=API_KEY, plot_width=1050, plot_height=510,
        #tools="pan,wheel_zoom,box_zoom,reset,hover,save"
    )
    plot.title.text = "Starbucks locations around the world"
    
    source_copy = ColumnDataSource(
        data=dict(
            lat=lat,
            lon=lon,
            city=city,
            name=name,
            eodb=eodb,
            tourists=tourists,
            tech_exports=tech_exports,
            inet_users=inet_users            
        ),
    )
    source = ColumnDataSource(
        data=dict(
            lat=lat,
            lon=lon,
            city=city,
            name=name,
            eodb=eodb,
            tourists=tourists,
            tech_exports=tech_exports,
            inet_users=inet_users             
        ),
    )
    
    circle = Circle(x="lon", y="lat", size=2, fill_color="brown", fill_alpha=0.8, line_color=None)
    plot.add_glyph(source, circle)
    
    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), HoverTool(), 
	    ResetTool())
    
    callback = CustomJS(args=dict(source=source,source_copy=source_copy), code="""
    var eodb_input           = eodb.value;
    var tourists_input       = tourists.value;
    var tech_exports_input   = tech_exports.value;
    var inet_users_input     = inet_users.value;
    var data             = source.data;
    data['lat']          = []
    data['lon']          = []
    data['city']         = []
    data['name']         = []
    data['eodb']         = []
    data['tourists']     = []
    data['inet_users']       = []
    data['tech_exports']     = []
    
    for (i = 0; i < source_copy['data']['lat'].length; i++) {
        if((source_copy['data']['eodb'][i] <= eodb_input) &&
           (source_copy['data']['tourists'][i] <= tourists_input) &&
           (source_copy['data']['tech_exports'][i] <= tech_exports_input) &&
           (source_copy['data']['inet_users'][i] <= inet_users_input))
           {
            data['lat'].push(source_copy['data']['lat'][i])
            data['lon'].push(source_copy['data']['lon'][i])
            data['city'].push(source_copy['data']['city'][i])
            data['name'].push(source_copy['data']['name'][i])
            data['eodb'].push(source_copy['data']['eodb'][i])  
            data['tourists'].push(source_copy['data']['tourists'][i]) 
            
        }
    }
    
    
    source.trigger('change');
    """)
    
    
    eodb_slider = Slider(start=0, end=200, value=200, step=1,
                           title="Ease of doing business", callback=callback)
    callback.args["eodb"] = eodb_slider
    
    steps=(max(tourists)-min(tourists))/10
    tourists_slider = Slider(start=min(tourists), end=max(tourists), value=max(tourists), step=steps,
                           title="International tourists arrival (in millions)", callback=callback)
    callback.args["tourists"] = tourists_slider
    
    steps=(max(tech_exports)-min(tech_exports))/10
    tech_exports_slider = Slider(start=min(tech_exports), end=max(tech_exports), value=max(tech_exports), step=steps,
                           title="High-technology exports (in billions of US$)", callback=callback)
    callback.args["tech_exports"] = tech_exports_slider
    
    steps=(max(inet_users)-min(inet_users))/10
    inet_users_slider = Slider(start=min(inet_users), end=max(inet_users), value=max(inet_users), step=steps,
                           title="Internet users per 100 people", callback=callback)
    callback.args["inet_users"] = inet_users_slider
    
    
    #ready to set the hover test
    hover = plot.select(dict(type=HoverTool)) 
    hover.tooltips = OrderedDict([
    ("name", "@name"),
    ("city", "@city")
    ])
    
    #layout = row(plot, widgetbox(eodb_slider, tourists_slider, tech_exports_slider, inet_users_slider))
    layout = row(plot)
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.VIS_DIR, glob.LOCATIONS)
    output_file(fname)
    show(layout)