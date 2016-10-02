# -*- coding: utf-8 -*-
import os
from common import globals as glob

def encode_str_in_csv(line, s):
    line += '\"' + s + '\"' + ','
    return line
    
def write_dict_to_csv(dict, fname):
    fname = os.path.join(glob.OUTPUT_DIR_NAME, fname) 
    glob.log.info('going to write dictionary to ' + fname)
    with open(fname, 'wb') as csv_file:  
        #write the header row
        line = '\"CountryCode\",' #first column is country code
        #now the indicators
        #get all the keys from the first dictionary, they are the same for all dictionaries
        for k in dict[dict.keys()[0]].keys():
            #put the key in quotes, as some keys/values could have spaces
            line = encode_str_in_csv(line, k)
        line += '\n'    
        #read to write header row
        csv_file.write(line) 
            
        #access dictionary by dictionary
        for k in dict.keys():
            #start with an empty line to write
            line = ''
            d = dict[k]
            line = encode_str_in_csv(line, k) #country code
            key_count = 0
            glob.log.info('country '  + line)
            for k2 in d.keys():
                #glob.log.info(k2 + ' '  + str(d[k2]))
                val = d[k2]
                if k2 != 'name': #name key already holds a string   
                    val = str(val)
                #put the key in quotes, as some keys/values could have spaces    
                line = encode_str_in_csv(line, val) #value of individual indicators  
                key_count += 1                     
            glob.log.info('country %s, indicators %d' %(k, key_count))
            #write to csv
            line += '\n' 
            #ignore any non-ascii characters, this is needed because certain country names
            #have non utf-8 characters..they were causing an exception..
            line = line.encode('ascii', 'ignore')
            csv_file.write(line)    