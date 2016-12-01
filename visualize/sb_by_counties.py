# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 18:45:19 2016

@author: aarora
"""
import os
import csv
from bs4 import BeautifulSoup
from common import globals as glob
# Map colors
### GRAYSCALE
# colors = ["#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525"]
# colors = ["#f7f7f7", "#d9d9d9", "#bdbdbd", "#969696", "#636363", "#252525"]
# colors = ["#f7f7f7", "#cccccc", "#969696", "#525252"]

### REDS
# colors = ["#FFF5F0", "#FEE0D2", "#FCBBA1", "#FC9272", "#FB6A4A", "#EF3B2C", "#CB181D", "#99000D"]
# colors = ["#fee5d9", "#fcbba1", "#fc9272", "#fb6a4a", "#de2d26", "#a50f15"]
# colors = ["#FEE5D9", "#FCAE91", "#FB6A4A", "#CB181D"]

### Y/OR/RED
# colors = ["#FFFFCC", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#B10026"]
# colors = ["#FFFFB2", "#FED976", "#FEB24C", "#FD8D3C", "#F03B20", "#BD0026"]




def draw():
    # Read in stores rates
    stores = {}
    min_value = 100; max_value = 0
    reader = csv.reader(open(glob.US_COUNTIES_STARBUCKS_STORES), delimiter=",")
    for row in reader:
        try:
            full_fips = row[0]
            number = float( row[2] )
            stores[full_fips] = number
            if number > max_value:
                max_value = number
            if number < min_value:
                min_value = number
        except Exception as e:
            print(e)
            pass
    
    
    ### Purple/Red color scheme. Replace line below with colors above to try others.
    colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
    
    
    # Load the SVG map
    svg = open('counties2.svg', 'r').read()
    soup = BeautifulSoup(svg, 'lxml')
    paths = soup.findAll('path')
    #print(stores)
    # Change colors accordingly
    path_style = 'font-size:12px;fill-rule:nonzero;stroke:#000000;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel;fill:'
    for p in paths:
        
        if p['id'] not in ["State_Lines", "separator"]:
            #print('going to check for %s' %(p['id']))
            try:
                count = stores[p['id']]
                #print('rate %d id %s' %(rate, p['id']))
            except:
                count = 0
                
            if count > 300:
                color_class = 5
            elif count > 150:
                color_class = 4
            elif count > 50:
                color_class = 3
            elif count > 15:
                color_class = 2
            elif count >= 1:
                color_class = 1
            else:
                color_class = 0
    
    
            color = colors[color_class]
            p['style'] = path_style + color
            children = p.findChildren()
            for child in children:
                child.string = child.string + '\nCount: ' + str(int(count))
            #print(child.string + ' Count: ' + str(int(count)))
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.VIS_DIR, glob.US_COUNTIES_STARBUCKS_STORES_HMAP)
    f = open(fname, 'w')
    f.write(soup.prettify())
    f.close()