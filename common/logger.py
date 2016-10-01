# -*- coding: utf-8 -*-

import logging
import logging.config

def init(name):
    logger = logging.getLogger(name)
    
    log_file_name = name + '.log'
    handler = logging.FileHandler(log_file_name, 'w') #erase previous file if any
    #formatter = logging.Formatter('%(asctime)s %(name)-3s %(levelname)-7s %(message)s')
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(filename)s:%(lineno)d,%(levelname)s, %(message)s','%m-%d %H:%M:%S')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    #logger.info('initialized logger...')
    return logger