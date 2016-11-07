# -*- coding: utf-8 -*-
import os
from common import globals as glob
import matplotlib.pyplot as plt
import numpy as np

from sklearn import linear_model
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from . import classification

def linear_reg(df, explanatory, dependant):
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    #df2 = df[df['country_code'] != 'US']
    X = df[explanatory].values
    X = X.reshape(-1,1) #new version of scikit learn needs this 
    
    y = df[dependant].values
    y = y.reshape(-1,1) #new version of scikit learn needs this 
    
    regr.fit(X,y)
    
    # The coefficients
    glob.log.info('[Linear regression] Coefficients:')
    glob.log.info(regr.coef_)
    
    # The mean squared error
    glob.log.info("[Linear regression] Mean squared error: %.2f"
          % np.mean((regr.predict(X) - y) ** 2))
    # Explained variance score: 1 is perfect prediction
    glob.log.info('[Linear regression] Variance score: %.2f' % regr.score(X, y))
    
    # Plot outputs
    lw = 2
    x = np.linspace(min(X), max(X), 10)
    x = x.reshape(-1,1)
    plt.figure()
    plt.scatter(X, y,  color='navy', s=30, marker='o', label="training points")
    plt.plot(x, regr.predict(x), color='teal', linewidth=lw, label="linear regression") 
    plt.legend(loc='lower right')
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.REGRESSION_DIR, 'linear.png')
    plt.savefig(fname)
    plt.close('all')

def poly_reg(df, explanatory, dependant):
    # Train the model using the training sets
    #df2 = df[df['country_code'] != 'US']
    X = df[explanatory].values
    X = X.reshape(-1,1) #new version of scikit learn needs this 
    
    y = df[dependant].values
    y = y.reshape(-1,1) #new version of scikit learn needs this 
    plt.figure()
    plt.scatter(X, y, color='navy', s=30, marker='o', label="training points")
    colors = ['teal', 'yellowgreen', 'gold']
    lw = 2
    x = np.linspace(min(X), max(X), 10)
    x = x.reshape(-1,1)
    
    #verified that degree 3 polynomial fits best so using that only
    for count, degree in enumerate([3]):
    #for count, degree in enumerate([3, 4, 5]):
        model = make_pipeline(PolynomialFeatures(degree), Ridge())
        model.fit(X, y)
        
        # The mean squared error
        glob.log.info("[Polynomial regression(degree=%d)] Mean squared error: %.2f"
              % (degree, np.mean((model.predict(X) - y) ** 2)))
        # Explained variance score: 1 is perfect prediction
        glob.log.info('[Polynomial regression(degree=%d)] Variance score: %.2f' % (degree, model.score(X, y)))
        
        y_plot = model.predict(x)
        plt.plot(x, y_plot, color=colors[count], linewidth=lw,
                 label="degree %d" % degree)
    
        plt.legend(loc='lower right')
        fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.REGRESSION_DIR, 'polynomial.png')
        plt.savefig(fname)
    plt.close('all')

def linear_multivariate_reg(df, dependant, dependant_categorical):
    important_features = classification.find_important_features(df, dependant_categorical, 15)
    
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    #df2 = df[df['country_code'] != 'US']
    X = df[important_features].values
    #X = X.reshape(-1,1) #new version of scikit learn needs this 
    
    y = df[dependant].values
    y = y.reshape(-1,1) #new version of scikit learn needs this 
    
    regr.fit(X,y)
    
    # The coefficients
    glob.log.info('[Multivariate Linear regression] Coefficients:')
    glob.log.info(regr.coef_)
    
    # The mean squared error
    glob.log.info("[Multivariate Linear regression] Mean squared error: %.2f"
          % np.mean((regr.predict(X) - y) ** 2))
    # Explained variance score: 1 is perfect prediction
    glob.log.info('[Multivariate Linear regression] Variance score: %.2f' % regr.score(X, y))

def poly_multivariate_reg(df, dependant, dependant_categorical):
    
    important_features = classification.find_important_features(df, dependant_categorical, 15)
    
    # Train the model using the training sets
    #df2 = df[df['country_code'] != 'US']
    X = df[important_features].values
    #X = X.reshape(-1,1) #new version of scikit learn needs this 
    
    y = df[dependant].values
    y = y.reshape(-1,1) #new version of scikit learn needs this 
    
    #verified that degree 3 polynomial fits best so using that only
    for count, degree in enumerate([3]):
    #for count, degree in enumerate([3, 4, 5]):
        model = make_pipeline(PolynomialFeatures(degree), Ridge())
        model.fit(X, y)
        
        # The mean squared error
        glob.log.info("[Polynomial Multivariate regression(degree=%d)] Mean squared error: %.2f"
              % (degree, np.mean((model.predict(X) - y) ** 2)))
        # Explained variance score: 1 is perfect prediction
        glob.log.info('[Polynomial Multivariate regression(degree=%d)] Variance score: %.2f' % (degree, model.score(X, y)))
         
def run(df):
    glob.log.info('=============== Begin Regression ===================')
    explanatory           = 'ST.INT.ARVL'
    dependant             = 'Num.Starbucks.Stores'
    dependant_categorical = 'Num.Starbucks.Stores.Categorical'
    
    #first run linear regression
    linear_reg(df, explanatory, dependant)
    
    #then polynomial
    poly_reg(df, explanatory, dependant)
    
    #now do a multivariate to predict value of number of stores
    linear_multivariate_reg(df, dependant, dependant_categorical)
    poly_multivariate_reg(df, dependant, dependant_categorical)
    
    glob.log.info('=============== End Regression ===================')
     
    

    