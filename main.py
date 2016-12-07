# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd

from common import logger
from common import globals as glob
from common import utils
from wb import wb
from sb import sb
from analyze import analyze
from analyze import a1,a2
from visualize import visualize,bubble,sb_by_counties

ID_RS = 'Invalid_Data_Raw_Score'
ID_AS = 'Invalid_Data_Adjusted_Score'
MD_RS = 'Missing_Data_Raw_Score'
MD_AS = 'Missing_Data_Adjusted_Score'
CS    = 'Combined_Score'
DS    = 'Datasource'
ID    = 'invalid_data'
MD    = 'missing_data'
DQS   = 'dqs'
RS    = 'raw_score'
AS    = 'adjusted_score'

def print_dqs(fname):
    #print dqs
    wb_summary = utils.get_quality_summary(glob.wb['quality']) 
    glob.log.info('WB data quality score is: ')
    glob.log.info(wb_summary)

    #print dqs
    sb_summary = utils.get_quality_summary(glob.sb['quality']) 
    glob.log.info('Starbucks data quality score is: ')
    glob.log.info(sb_summary)
    
    #store everything in a CSV for easy post processing/display
    columns = [DS, CS, ID_RS, ID_AS, MD_RS, MD_AS]
    df = pd.DataFrame(columns = columns)
    df[DS] = ['WorldBank', 'Starbucks']
    df[CS] = [(wb_summary[ID][DQS][AS] + wb_summary[MD][DQS][AS])/2,
              (sb_summary[ID][DQS][AS] + sb_summary[MD][DQS][AS])/2]
    df[ID_RS] = [wb_summary[ID][DQS][RS], sb_summary[ID][DQS][RS]]
    df[ID_AS] = [wb_summary[ID][DQS][AS], sb_summary[ID][DQS][AS]]    
    df[MD_RS] = [wb_summary[MD][DQS][RS], sb_summary[MD][DQS][RS]]
    df[MD_AS] = [wb_summary[MD][DQS][AS], sb_summary[MD][DQS][AS]]    

    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.DQS_DIR, fname)    
    df.to_csv(fname, index = False)
    
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
    
    #print the data quality score
    print_dqs(glob.DQS_CSV)
    
    
def clean_data():
    #clean WB data
    glob.wb['df'], glob.wb['quality'] = wb.clean_data(glob.wb['df'], glob.wb['quality'])
    
    #clean SB data
    glob.sb['df'], glob.sb['quality']= sb.clean_data(glob.sb['df'], glob.sb['quality'])
    
    #print the data quality score
    print_dqs(glob.DQS_AFTER_CLEANINIG_CSV)

def create_features():
    #feature creation for WB data
    glob.wb['df'] = wb.create_features(glob.wb['df'])

    #feature creation for SB data, feature creation for SB is the real thing
    #because that ultimately feeds into our problem statement, WB data is a helper
    #data which will be joined with the SB data in future phases of this project
    glob.sb['df'] = sb.create_features(glob.sb['df'])    
    
def visualize_data():
    #invoke the visualization module
    visualize.draw()
    
def do_eda():
    #EDA for WB data
    wb.do_eda(glob.wb['df'])
    
    #EDA SB data
    sb.do_eda(glob.sb['df'])
    
def print_banner():
    glob.log.info('-------------------------------------------------------------------------')
    glob.log.info('%s v%s: %s' %(glob.__PROJECT_NAME_SHORT__, glob.__VERSION__, glob.__PROJECT_NAME_LONG__))  
    glob.log.info('Author: %s, %s' %(glob.__AUTHOR__, glob.__AUTHOR_EMAIL__))
    glob.log.info('-------------------------------------------------------------------------')
    
def main(argv):
    #create output folder before anything else
    output_dir = glob.OUTPUT_DIR_NAME
    try:
        #create if not present
        if os.path.isdir(output_dir) == False:
            os.mkdir(output_dir)
    except Exception as e:
        print('Exception occured while creating ' + output_dir + ', EXITING...')
        print(str(e))
        sys.exit(1)
    
    #separate dir for association, clustering, classification
    for d in [glob.ASSOCIATON_DIR, glob.CLUSTERING_DIR, glob.CLASSIFICATION_DIR, glob.REGRESSION_DIR,
              glob.DQS_DIR, glob.SCATTER_DIR, glob.EDA_DIR, glob.VIS_DIR, glob.TSA_DIR]:
        result_dir = os.path.join(glob.OUTPUT_DIR_NAME, d)
        try:
            #create if not present
            if os.path.isdir(result_dir) == False:
                os.mkdir(result_dir)
        except Exception as e:
            print('Exception occured while creating ' + result_dir + ', EXITING...')
            print(str(e))
            sys.exit(1)    
        
    #intiialize logger so that we can see the traces
    try:
        glob.log = logger.init(glob.NAME_FOR_LOGGER)
    except Exception as e:
        print('failed to initialize logger, exception: ' + str(e))
        print('EXITING..')
        sys.exit(1)    
    #logging initialize, no ready to start the data science pipeline
    print_banner()    
    #if only running in analysis mode then assume all csv files are there
    #just run the analysis and exit
    if len(argv) >= 2:
        mode = argv[1]
        if mode == '-a':
            glob.log.info('Begin SB analysis, logs available on console and in %s' %(os.path.join(glob.OUTPUT_DIR_NAME, 'SBS.log')))
            analyze.run()
            a1.run()
            a2.run()
            sys.exit(0) ## all done
        if mode == '-a1':
            glob.log.info('Begin SB additional analysis, logs available on console and in %s' %(os.path.join(glob.OUTPUT_DIR_NAME, 'SBS.log')))
            a1.run()
            sys.exit(0) ## all done    
        if mode == '-a2':
            glob.log.info('Begin SB additional analysis, logs available on console and in %s' %(os.path.join(glob.OUTPUT_DIR_NAME, 'SBS.log')))
            a2.run()
            sys.exit(0) ## all done   
        else:    
            glob.log.info('Begin SB visualizations, logs available on console and in %s' %(os.path.join(glob.OUTPUT_DIR_NAME, 'SBS.log')))
            visualize_data()
            sys.exit(0) ## all done
    
    glob.log.info('Begin SB study, logs available on console and in %s' %(os.path.join(glob.OUTPUT_DIR_NAME, 'SBS.log')))
    
       
    #initialize the 'wb' module which is a submodule for everything we want to
    #do with the world bank data and then do the same for the 'sb' module
    wb.init()
    sb.init()
    
    #STEP 1: get the data    
    get_data()
    
    #Step 2: evaluate and clean the data
    check_quality_of_data()
    clean_data()
    
    #step 2.5 feature creation and EDA
    create_features()
    #do EDA
    do_eda()
    
    #Step 3: analyze
    glob.log.info('Begin SB analysis, logs available on console and in %s' %(os.path.join(glob.OUTPUT_DIR_NAME, 'SBS.log')))
    analyze.run()
    a1.run()
    a2.run()
        
    #Step 3.5: TBD
    visualize_data()    
    
    #Further steps are currently TBD
    glob.log.info('all done, existing...')
               
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

