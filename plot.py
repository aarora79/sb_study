"""
Thanks Josh Hemann for the example
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import pandas as pd
## numpy is used for creating fake data
import numpy as np 
import matplotlib as mpl 
import os

## agg backend is used to create plot as a .png file
mpl.use('agg')

import matplotlib.pyplot as plt 
fname = os.path.join('.', 'output', 'WDI_SB.csv')
df = pd.read_csv(fname)
data_to_plot = []
continents = df['continent'].unique()
for c in continents:
    ## combine these different collections into a list    
    data_to_plot.append(df[df['continent'] == c]['Num.Starbucks.Stores'].values) 

# Create a figure instance
fig = plt.figure(1, figsize=(9, 6))

# Create an axes instance
ax = fig.add_subplot(111)
print(continents)

ax.set_yscale("log", nonposy='clip')

# Create the boxplot
bp = ax.boxplot(data_to_plot, labels=continents)

# Save the figure
fig.savefig('boxplot.png', bbox_inches='tight')