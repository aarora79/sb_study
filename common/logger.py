# -*- coding: utf-8 -*-

import logging
import logging.config
import os

#import globals as glob
from . import globals as glob
def init(name):
    logger = logging.getLogger(name)
    name += '.log'
    log_file_name = os.path.join(glob.OUTPUT_DIR_NAME, name)
    
    handler = logging.FileHandler(log_file_name, 'w') #erase previous file if any
    #formatter = logging.Formatter('%(asctime)s %(name)-3s %(levelname)-7s %(message)s')
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(filename)s:%(lineno)d,%(levelname)s, %(message)s','%m-%d %H:%M:%S')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    #add a console handler as well, it is nice to see messages at both places
    handler = logging.StreamHandler()
    #formatter = logging.Formatter('%(asctime)s %(name)-3s %(levelname)-7s %(message)s')
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(filename)s:%(lineno)d,%(levelname)s, %(message)s','%m-%d %H:%M:%S')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    #logger.info('initialized logger...')
    return logger