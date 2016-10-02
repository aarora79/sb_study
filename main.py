# -*- coding: utf-8 -*-
import sys
import os

from common import logger
from common import globals as glob
from wb import wb
from sb import sb

def get_data():
    #get WB data
    glob.wb['df'] = wb.get_data()
    
    #get SB data
    glob.sb['df'] = sb.get_data()
    
def check_quality_of_data():
    #check quality WB data
    glob.wb['quality'] = wb.check_quality_of_data(glob.wb['df'])
    
    #check quality SB data
    glob.sb['quality'] = sb.check_quality_of_data(glob.sb['df'])
    
def clean_data():
    #clean WB data
    glob.wb['df'] = wb.clean_data(glob.wb['df'])
    
    #clean SB data
    glob.sb['df'] = sb.clean_data(glob.sb['df'])
    
def visualize_data():
    #visualize WB data
    wb.clean_data(glob.wb['df'])
    
    #visualize SB data
    sb.clean_data(glob.sb['df'])
    
    
def main(argv):
    #intiialize logger so that we can see the traces
    try:
        glob.log = logger.init(glob.NAME_FOR_LOGGER)
    except Exception as e:
        print('failed to initialize logger, exception: ' + str(e))
        print('EXITING..')
        sys.exit(1)    
    #logging initialize, no ready to start the data science pipeline
    glob.log.info('begin SB study\n')
    
    #create output folder before anything else
    output_dir = glob.OUTPUT_DIR_NAME
    try:
        #create if not present
        if os.path.isdir(output_dir) == False:
            os.mkdir(output_dir)
    except Exception as e:
        glob.log.error('Exception occured while creating ' + output_dir + ', EXITING...')
        glob.log.error(str(e))
        sys.exit(1)
        
    #initialize the 'wb' module which is a submodule for everything we want to
    #do with the world bank data and then do the same for the 'sb' module
    wb.init()
    sb.init()
    
    #STEP 1: get the data    
    get_data()
    
    #Step 2: evaluate and clean the data
    check_quality_of_data()
    clean_data()
    
    #Step 3: some basic visualizations
    visualize_data()    
    
    #Further steps are currently TBD
    glob.log.info('all done, existing...')
               
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

