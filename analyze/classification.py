# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 01:12:18 2016

@author: aarora
"""
# -*- coding: utf-8 -*-
import pandas as pd
import os
from common import globals as glob
from common import utils
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sklearn.preprocessing import normalize
from sklearn import cross_validation
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier

from sklearn import metrics


TEST_DATA_FRACTION = 0.20
NUM_FOLDS          = 10
SEED               = 7

def map_values_to_numeric(y):
    y_unique = y.unique()
    #now replace every value with its numeric counterpart  
    i = 0    
    for y_val in y_unique:    
        y = y.replace(y_val, i)
        i += 1 #number representing next unique value
    return y    
        
def find_important_features(df, dependant, num_important):

    #first find all numeric features
    excluded_feature_list = ['Num.Starbucks.Stores.On.Airports', 'Starbucks.Store.Density', 'Num.Starbucks.Stores']
    numeric_features = utils.get_numeric_feature_list(df, excluded_feature_list)            
    #do feature ranking
    y = df[dependant]
    y = map_values_to_numeric(y)
    X = df.ix[:,numeric_features]   
    X = normalize(X, axis=0) #normalize per feature
    # fit an Extra Trees model to the data
    model = ExtraTreesClassifier()
    model.fit(X, y)
    important_feature_list = np.array(model.feature_importances_.argsort()[-num_important:][::-1])
    glob.log.info('feature names to be used  -> ' )
    glob.log.info(important_feature_list)
    glob.log.info('feature name, importance for predicted feature %s' %(dependant))
    for i in important_feature_list:
        glob.log.info('%s %f' %(numeric_features[i], model.feature_importances_[i]))  
        
    return [numeric_features[i] for i in important_feature_list]   
    
def run_models(X_train, Y_train, scoring, seed, num_instances, num_folds, dependant):
 
    # Add each algorithm and its name to the model array
    models = []
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('CART', DecisionTreeClassifier()))
    models.append(('NB', GaussianNB()))
    #models.append(('SVM-sigmoid', SVC(kernel='sigmoid')))
    models.append(('SVM-rbf', SVC(kernel='rbf'))) #all kernels are providing results identical to rbf so keeping that only
    #models.append(('SVM-linear', SVC(kernel='linear')))
    #models.append(('SVM-poly', SVC(kernel='poly')))
    #models.append(('SVM-precomputed', SVC(kernel='precomputed')))
    models.append(('RandomForest', RandomForestClassifier(n_estimators=1000)))
    
    # Evaluate each model, add results to a results array,
    # Print the accuracy results (remember these are averages and std
    results = []
    names = []
    msg =''
    for name, model in models:
        kfold = cross_validation.KFold(n=num_instances, n_folds=num_folds, random_state=seed)
        cv_results = cross_validation.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
        results.append(cv_results)
        #glob.log.info(cv_results)
        names.append(name)
        msg += "%s: %f (%f)\n" % (name, cv_results.mean(), cv_results.std())
    glob.log.info('------------- Results for %s-------------' %(dependant))
    glob.log.info(msg)
    glob.log.info('-----------------------------------------')

def classify_dependant(df, dependant_categorical, num_important):
    #first find important features which we are then going to use in the classifier  
    #from previous runs we determined these features ot be most important 15
    if dependant_categorical == 'Num.Starbucks.Stores.Categorical1':
        important_features = ['ST.INT.ARVL', 'BX.KLT.DINV.WD.GD.ZS', 'IC.REG.PROC', 'TX.VAL.TECH.CD',
                              'BG.GSR.NFSV.GD.ZS', 'SL.GDP.PCAP.EM.KD', 'IC.WRH.DURS', 'IC.IMP.COST.CD',
                              'IC.LGL.CRED.XQ', 'IC.EXP.COST.CD', 'NE.CON.PETC.ZS', 'IC.IMP.DURS',
                              'IQ.WEF.PORT.XQ', 'IC.REG.DURS']
    else:
        important_features = find_important_features(df, dependant_categorical, num_important)
                                  
    
    
    #now get things ready by arranging the data in test/train splits     
    test_size = TEST_DATA_FRACTION
    seed      = SEED
    #Hypothesis 2: a set of WDI indicators can be used to predict the categorical value of number of Starbucks store
    #              i.e. VerLow, Low, Medium, High, VeryHigh
    
    
    X = df[important_features].values
    X = normalize(X, axis=0) #normalize per feature
    Y = df[dependant_categorical].values
    X_train, X_validate, Y_train, Y_validate = cross_validation.train_test_split(X, Y, test_size=test_size, random_state=seed)
    
    # Setup 10-fold cross validation to estimate the accuracy of different models
    # Split data into 10 parts
    # Test options and evaluation metric
    num_folds = NUM_FOLDS
    num_instances = len(X_train)
    
    scoring = 'accuracy'
    run_models(X_train, Y_train, scoring, seed, num_instances, num_folds, dependant_categorical)
        
def run(df):
    glob.log.info('=============== Begin Classifier ===================')

    classify_dependant(df, 'Num.Starbucks.Stores.Categorical', 15)
    
    classify_dependant(df, 'Starbucks.Store.Density.Categorical', 5)
    
    classify_dependant(df, 'Ownership.Type.Mixed', 15)
    
    
    glob.log.info('=============== End Classifier ===================')