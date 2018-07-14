# IMPORT DEPENDENCIES
import warnings
warnings.simplefilter('ignore')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from datetime import *
import time

from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense

def predict_20s(filename):
    df = pd.read_csv(filename)
    
    # remove data from customers - their data doesn't include their age, so they will not help our regression
    df = df[df['usertype'] == "Subscriber"]
    df = df[df['gender']!=0]
    df = df[(df['start station latitude'] < 41.5) & (df['end station latitude'] < 41.5)]
    df = df.dropna()

    # parse datetime of ride start to create variables for hour of the day, and whether or not the ride happened on a weekend
    hour = []
    weekend = []
    for start_time in df['starttime']:
        t1 = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
        hour.append(t1.hour)
        if t1.weekday() in [5,6]:
            weekend.append(1)
        else:
            weekend.append(0)
    
    # aggregate results into a new dataframe
    clean_df = pd.DataFrame({
        "duration":df['tripduration'],\
        "weekend":weekend,\
        "hour":hour,\
        "start_lat":df['start station latitude'],\
        "start_long":df['start station longitude'],\
        "end_lat":df['end station latitude'],\
        "end_long":df['end station longitude'],\
        "gender":(df['gender']-1),\
        "age":(2018 - df['birth year'])
    })
    
    # create a new column based on the age of riders
    # since a neural network predicts a binary outcome, we will predict whether or not a rider is in their 20s (aged 20-29)
    twenties = []
    for val in clean_df['age']:
        if val < 30 and val > 19:
            twenties.append(1)
        else:
            twenties.append(0)

    clean_df['twenties'] = twenties
    
    print(f'{filename} successfully cleaned.') 
    
    # pull beginning and ending coordinates to build clusters around
    km_test = clean_df[['start_lat','start_long','end_lat','end_long']]
    # be sure not to include coordinates in the modelling data, since they will have collinearity with the trip clusters we make
    k_data = clean_df.drop(['start_lat','start_long','end_lat','end_long','age','twenties'], axis=1)

    # cluster rides
    kmeans = KMeans(n_clusters=10)
    kmeans.fit(km_test)
    predicted_clusters = kmeans.predict(km_test)
    k_data['trip_cluster'] = predicted_clusters
    
    print("Trip clustering complete")
    print("Beginning neural network modelling")
    
    # create dummy columns for trip cluster and hour of the day
    k_data_encoded = pd.get_dummies(k_data, columns=['trip_cluster','hour'])
    y = clean_df['twenties'].values.reshape(-1, 1) 
    
    # split data into training and testing samples
    # create a scaler according to training input, apply to testing input
    X_train, X_test, y_train, y_test = train_test_split(
        k_data_encoded, y, random_state=1, stratify=y)
    X_scaler = StandardScaler().fit(X_train)
    X_train_scaled = X_scaler.transform(X_train)
    X_test_scaled = X_scaler.transform(X_test)

    y_train_categorical = to_categorical(y_train)
    y_test_categorical = to_categorical(y_test)
    
    # build sequential model
    model = Sequential()
    model.add(Dense(units=64, activation='relu', input_dim=37))
    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=2, activation='softmax'))
    
    # compile and fit to training data
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    model.fit(
        X_train_scaled,
        y_train_categorical,
        epochs=5,
        shuffle=True,
        verbose=2
    )
    
    # test model on testing data
    model_loss, model_accuracy = model.evaluate(
        X_test_scaled, y_test_categorical, verbose=2)
    print(
        f"Normal Neural Network - Loss: {model_loss}, Accuracy: {model_accuracy}")
    
    # save cleaned data and nn model
    clean_df['predicted_cluster'] = predicted_clusters
    clean_df.to_csv(f'cleaned_{filename}')
    model.save(f'{filename}_nn.h5')
    
    return;

# predict_20s('201802_citibikenyc_tripdata.csv')
   