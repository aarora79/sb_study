# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 01:32:22 2016

@author: aarora
"""

# -*- coding: utf-8 -*-
import pandas as pd
import os
from common import globals as glob
from common import utils
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.ensemble import ExtraTreesClassifier
from matplotlib import style
style.use("ggplot")
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering

from sklearn import metrics
from collections import Counter

NUM_COMPONENTS_FOR_PCA   = 3
DO_SCALAR_TRANSFORM      = True
CLUSTER_COUNT_FOR_KMEANS = 5

def set_colors(labels, colors='rgkybcm'):
    colored_labels = []
    for label in labels:
        colored_labels.append(colors[label])
    return colored_labels

  
def do_PCA(df, components=NUM_COMPONENTS_FOR_PCA, do_scalar_transform=DO_SCALAR_TRANSFORM):  
    glob.log.info('doing PCA on the combined dataset...')
    #first remove columns which are not continous i.e. country_code and name
    #the goal here is to just find clusters within the WB dataset which has been filtered by the existence
    #of starbucks stores..then we want to find out are there any clusters there
    numeric_features = []
    for col in df.columns:
        try:
            x=df[col].iloc[0] 
            float(x)#typecast the data to float to test if it is numeric
        except:
            glob.log.info('%s is not a numeric feature, ignoring for PCA' %(col))
        else:
            numeric_features.append(col)
    #get the values as a numpy array  ..
    #NOTE: this is important, we are getting the column names from the WB dataset
    #      but the final, cleaned, to be used, dataset is the combined dataset so use df and not df_WB 
    X = df.ix[:,numeric_features].values   
    #print(X)
    
    #now standardize it 
    if do_scalar_transform == True:         
        X = StandardScaler().fit_transform(X)
    
    # To getter a better understanding of interaction of the dimensions
    # plot the first three PCA dimensions
    #fig = plt.figure(1, figsize=(8, 6))
    #ax = Axes3D(fig, elev=-150, azim=110)
    fig = plt.figure(1, figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    X_reduced = PCA(n_components=components).fit_transform(X)
    ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2]) #, c=1,cmap=plt.cm.Paired)
    title = 'PCA(components=%d)' %(components)    
    ax.set_title(title)
    ax.set_xlabel('1st eigenvector')
    ax.set_ylabel('2nd eigenvector')
    ax.set_zlabel('3rd eigenvector')
    fname = 'PCA.png'
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.CLUSTERING_DIR, fname)
    plt.savefig(fname)
    
    return X_reduced

def run_KMeans(X):
    kmeans = KMeans(n_clusters=CLUSTER_COUNT_FOR_KMEANS)
    kmeans.fit(X)

    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_
     
    glob.log.info('====== printing results for kmeans ======') 
    glob.log.info('====== centroids ======') 
    
    glob.log.info(centroids)
    glob.log.info('====== labels ======') 
    glob.log.info(labels)
    glob.log.info('=========================================') 
    
    color_list_by_label = set_colors(labels)
    #plot it now
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    #combine the points and the centroids to plot in a single call to the scatter function
    X_combined = np.vstack((X,centroids))
    
    centroid_colors = ['b']*len(centroids)
    color_list_by_label = color_list_by_label + centroid_colors
    
    marker_list = ['.']*len(X)
    marker_list_centroids = ['x']*len(centroids)
    marker_list = marker_list + marker_list_centroids
    
    size_list = [25]*len(X)
    size_list_centroids = [75]*len(centroids)
    size_list = size_list + size_list_centroids
    glob.log.info('%d %d %d %d' %(len(X_combined), len(color_list_by_label), len(marker_list), len(size_list)))
    ax.scatter(X_combined[:, 0], X_combined[:, 1], X_combined[:, 2], c=color_list_by_label, marker='o', s=size_list)
    
    title = 'KMeans(n=%d)' %(CLUSTER_COUNT_FOR_KMEANS)    
    ax.set_title(title)
    ax.set_xlabel('1st eigenvector')
    ax.set_ylabel('2nd eigenvector')
    ax.set_zlabel('3rd eigenvector')
    fname = 'KMeans.png'
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.CLUSTERING_DIR, fname)
    plt.savefig(fname)  
    return labels
    
def run_DBSCAN(X):
    # Fit a DBSCAN estimator
    estimator = DBSCAN(eps=1, min_samples=5)
    estimator.fit(X)
    # Clusters are given in the labels_ attribute
    labels = estimator.labels_
    
    colors = set_colors(labels)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(X[:,0], X[:,1], X[:,2],c=colors, marker='o')
    
    ax.set_xlabel('1st eigenvector')
    ax.set_ylabel('2nd eigenvector')
    ax.set_zlabel('3rd eigenvector')
    
    fname = 'DBSCAN.png'
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.CLUSTERING_DIR, fname)
    plt.savefig(fname) 
    
    core_samples = np.zeros_like(labels, dtype = bool)
    core_samples[estimator.core_sample_indices_] = True
     
    glob.log.info('====== printing results for DBSCAN ======') 
    glob.log.info('====== core_samples ======')     
    glob.log.info(core_samples)
    glob.log.info('====== labels ======') 
    glob.log.info(estimator.labels_)
    glob.log.info(Counter(labels))
    
    glob.log.info('=========================================') 
    return labels
 
def run_heirarchical(X):
    # Fit an estimator
    estimator = AgglomerativeClustering(n_clusters=CLUSTER_COUNT_FOR_KMEANS)
    estimator.fit(X)
    # Clusters are given in the labels_ attribute
    labels = estimator.labels_
    colors = set_colors(labels)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(X[:,0], X[:,1], X[:,2],c=colors, marker='o')
    
    ax.set_xlabel('1st eigenvector')
    ax.set_ylabel('2nd eigenvector')
    ax.set_zlabel('3rd eigenvector')
    
    fname = 'Hierarchical.png'
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.CLUSTERING_DIR, fname)
    plt.savefig(fname) 
     
    glob.log.info('====== printing results for Hierarchical Agglomerative Clustering ======') 
    glob.log.info('====== labels ======') 
    glob.log.info(estimator.labels_)
    glob.log.info(Counter(labels))
    
    glob.log.info('=========================================') 
    return labels

def run(df):
    
    #the combined dataset has 40 odd attributes so do PCA before clustering
    X = do_PCA(df)
    
    #keep a copy of the original df
    df2 = df.copy(deep = True)
    #run KMeans
    labels = run_KMeans(X)
    df2['KMeans_labels'] = labels
    
    #run DBSCAN
    labels = run_DBSCAN(X)
    df2['DBSCAN_labels'] = labels
    
    #run heirarchical
    labels = run_heirarchical(X)
    df2['Heirarchical_labels'] = labels
    
    #store in a new CSV file
    fname = os.path.join(glob.OUTPUT_DIR_NAME, glob.CLUSTERING_DIR, glob.COMBINED_DS_W_LABELS)
    df2.to_csv(fname, index=False)