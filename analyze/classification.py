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
RANDOM_FORESTS_CLASSIFIER = 'RandomForests'

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
    models.append((RANDOM_FORESTS_CLASSIFIER, RandomForestClassifier(n_estimators=1000)))
    
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
    return models

def classify_dependant(df, dependant_categorical, num_important):
    #first find important features which we are then going to use in the classifier  
    #from previous runs we determined these features ot be most important 15
    if dependant_categorical == 'Num.Starbucks.Stores.Categorical':
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
    return important_features

def get_prediction_country_list(df, df_WB, features, dependant_categorical):
    #list all the countries for which we have data for these features
    predictions = { 'country_codes': [], 'names': [], dependant_categorical: [] }
    for i in range(len(df_WB)):
        country = df_WB.ix[i]
        country_code = country['country_code']
        countries_w_starbucks = list(df['country_code'])
        if country_code not in countries_w_starbucks:
            #this country does not have Starbucks, check if we have data for it
            #for features we need for classification
            data_for_all_features = True
            for f in features:
                if pd.isnull(country[f]) == True:
                    data_for_all_features = False
                    break
            if data_for_all_features == True:
                predictions['country_codes'].append(country['country_code'])
                predictions['names'].append(country['name'])
    return predictions
    
def predict(df, df_WB, features, dependant_categorical):
    glob.log.info('ready to predict categorical variables....................')
    glob.log.info('doing predictions for countries with enough data ..for which there are no Starbucks yet')
    
    predictions = get_prediction_country_list(df, df_WB, features, dependant_categorical)
    
    #now that we have the country list lets run the model...we know 
    #from cross validation results that random forests gives best results
    
    rf = RandomForestClassifier(n_estimators=1000)
    #prepare X,y    
    X = df[features].values
    X = normalize(X, axis=0) #normalize per feature
    y = df[dependant_categorical].values
    #fit the data into the model
    rf.fit(X, y)

    #ok, predict now    
    df_temp = df_WB[df_WB['country_code'].isin(predictions['country_codes'])]
    X = df_temp[features].values 
    X = normalize(X, axis=0) #normalize per feature      
    y = rf.predict(X)
    predictions[dependant_categorical] = y
    
    #convert to a df and store the output in a csv file
    df_temp = pd.DataFrame(predictions)
    df_temp.sort_values(by=dependant_categorical, inplace=True)
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.CLASSIFICATION_DIR, dependant_categorical + '_predictions.csv')
    df_temp.to_csv(fname, index=False)    
    
def run(df, df_WB):
    glob.log.info('=============== Begin Classifier ===================')

    important_features = classify_dependant(df, 'Num.Starbucks.Stores.Categorical', 15)
    #predict the number of stores as categorical for all countries where Starbucks does not exist
    predict(df, df_WB, important_features, 'Num.Starbucks.Stores.Categorical')
    
    classify_dependant(df, 'Starbucks.Store.Density.Categorical', 5)
    
    classify_dependant(df, 'Ownership.Type.Mixed', 15)
    
    
    glob.log.info('=============== End Classifier ===================')