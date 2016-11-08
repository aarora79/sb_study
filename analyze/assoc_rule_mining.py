# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 13:43:45 2016

@author: aarora
"""

import pandas as pd
import os
from common import globals as glob

MIN_CONFIDENCE = 0.25
MIN_SUPPORT_LIST = [0.05, 0.07, 0.1]

def mine_rule_2_features(df, feature1, feature2, feature1_shortname, feature2_shortname, assoc_rules):
    #find the frequency of all possible pairs of values of these features
    #a simple loop will suffice
    feature1_values = df[feature1].unique()
    for f1 in feature1_values:        
        support_for_feature1 = (len(df[df[feature1] == f1]))/len(df)
        x = df[df[feature1] == f1][feature2].value_counts()
        for i in x.index:            
            freq = x[i]
            support_for_rule = freq/len(df)
            confidence = support_for_rule/support_for_feature1
            feature1_str = feature1_shortname + '_' + f1
            feature2_str = feature2_shortname + '_' + i
            rule_str = 'R:({%s})->%s' %(feature1_str, feature2_str)
            assoc_rules['rule'].append(rule_str)
            assoc_rules['frequency'].append(freq)
            assoc_rules['support'].append(support_for_rule)
            assoc_rules['confidence'].append(confidence)
    return assoc_rules        
    
def mine_association_rules_2_features(df, feature1, feature2, feature1_shortname, feature2_shortname):
    glob.log.info('mining association rules for %s and %s' %(feature1, feature2))
    #create a dictionary for storing the results, would make it easier to convert it to a dataframe
    #and write to a file also
    assoc_rules = { 'rule': [], 'frequency': [], 'support': [], 'confidence': [] }
    
    #first mine rules in feature1->feature2 direction and then in the reverse direction
    assoc_rules = mine_rule_2_features(df, feature1, feature2, feature1_shortname, feature2_shortname, assoc_rules)
    assoc_rules = mine_rule_2_features(df, feature2, feature1, feature2_shortname, feature1_shortname, assoc_rules)
    
    #now put this in a dataframe for ease of analysis
    df_assoc_rules = pd.DataFrame(assoc_rules, columns=['rule', 'frequency', 'support', 'confidence'])
    
    #ok we are ready now for some analysis on the association rules..
    #use min support as say [0.05, 0.1, 0.15] and min confidence as say 0.25 to filter out the important rules
    min_confidence = MIN_CONFIDENCE   
    for min_support in MIN_SUPPORT_LIST:
        filter_name = 'min_support_%s_and_min_confidence_%s' %(min_support, min_confidence)
        #filer out the rules and store them in a separate csv file for easy asscess
        df_temp = df_assoc_rules[(df_assoc_rules['support'] >= min_support) & (df_assoc_rules['confidence'] >= min_confidence)]
        fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.ASSOCIATON_DIR, glob.ASSOCIATION_RULES_2_FEATURES_AFTER_FILTERING)
        fname = fname.replace('__FILTER_STRING__', filter_name)
        df_temp.to_csv(fname, index=False)   
        
    #write the unfiltered list to csv as well...
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.ASSOCIATON_DIR, glob.ASSOCIATION_RULES_2_FEATURES)
    df_assoc_rules.to_csv(fname, index=False)   
    glob.log.info('written all association rules with 2 features to %s' %(fname))
    

def mine_rule_3_features(df, feature1, feature2, feature3, 
                         feature1_shortname, feature2_shortname, feature3_shortname, assoc_rules):
    #find the frequency of all possible pairs of values of these features
    #a simple loop will suffice
    feature1_values = df[feature1].unique()
    feature2_values = df[feature2].unique()
    
    for f1 in feature1_values:
        df_level1 = df[df[feature1] == f1]
        for f2 in feature2_values:
            df_level2 = df_level1[df_level1[feature2] == f2]
            support_for_feature1_and_2 = len(df_level2)/len(df)
            x = df_level2[feature3].value_counts()
            for i in x.index:            
                freq = x[i]
                support_for_rule = freq/len(df)
                confidence = support_for_rule/support_for_feature1_and_2
                feature1_str = feature1_shortname + '_' + f1
                feature2_str = feature2_shortname + '_' + f2
                feature3_str = feature3_shortname + '_' + i
                rule_str = 'R:({%s,%s})->%s' %(feature1_str, feature2_str, feature3_str)
                assoc_rules['rule'].append(rule_str)
                assoc_rules['frequency'].append(freq)
                assoc_rules['support'].append(support_for_rule)
                assoc_rules['confidence'].append(confidence)
    return assoc_rules  
        
    
def mine_association_rules_3_features(df, feature1, feature2, feature3, 
                                      feature1_shortname, feature2_shortname, feature3_shortname):
    glob.log.info('mining association rules for 3 features %s,%s -> %s' %(feature1, feature2, feature3))
    #create a dictionary for storing the results, would make it easier to convert it to a dataframe
    #and write to a file also
    assoc_rules = { 'rule': [], 'frequency': [], 'support': [], 'confidence': [] }
    
    #first mine rules in feature1->feature2 direction and then in the reverse direction
    assoc_rules = mine_rule_3_features(df, feature1, feature2, feature3, feature1_shortname, feature2_shortname, feature3_shortname, assoc_rules)
    
    #now put this in a dataframe for ease of analysis
    df_assoc_rules = pd.DataFrame(assoc_rules, columns=['rule', 'frequency', 'support', 'confidence'])
    
    #ok we are ready now for some analysis on the association rules..
    #use min support as say [0.05, 0.1, 0.15] and min confidence as say 0.25 to filter out the important rules
    min_confidence = MIN_CONFIDENCE   
    for min_support in MIN_SUPPORT_LIST:
        filter_name = 'min_support_%s_and_min_confidence_%s' %(min_support, min_confidence)
        #filer out the rules and store them in a separate csv file for easy asscess
        df_temp = df_assoc_rules[(df_assoc_rules['support'] >= min_support) & (df_assoc_rules['confidence'] >= min_confidence)]
        fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.ASSOCIATON_DIR, glob.ASSOCIATION_RULES_3_FEATURES_AFTER_FILTERING)
        fname = fname.replace('__FILTER_STRING__', filter_name)
        df_temp.to_csv(fname, index=False)   
        
    #write the unfiltered list to csv as well...
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.ASSOCIATON_DIR, glob.ASSOCIATION_RULES_3_FEATURES)
    df_assoc_rules.to_csv(fname, index=False)   
    glob.log.info('written all association rules with 3 features to %s' %(fname))
    
def run(df):
    glob.log.info('=============== Begin Association Rules Mining ===================')
    glob.log.info('mining association rules...')
    #choose two features which are a) Categorical and b) (obviously) of intrest
    mine_association_rules_2_features(df, 'Num.Starbucks.Stores.Categorical', 'ST.INT.ARVL.Categorical', 'SBS', 'TOURIST_ARR')
        
    #Starbucks.Store.Density.Categorical, Ease.Of.Doing.Business        
    #choose 2 features to predict 3rd
    mine_association_rules_3_features(df, 'SP.POP.TOTL.Categorical', 'ST.INT.ARVL.Categorical',
                                      'Num.Starbucks.Stores.Categorical', 'POPT', 'TOURIST_ARR', 'SBS')
    glob.log.info('=============== End Association Rules Mining ===================')                                  
        
            
                