import boto3
import datetime
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

import threading

class PreemptionEstimator(object):
    def __init__(self, max_price=-1):
        self.prob = -1
        self.max_price = max_price

        self.mutex_lock = threading.Lock()
        self.predict_intention = False

        self.start_time = datetime.datetime.now()
        # self.time_deltas = np.empty()
        # self.prices = np.empty()
        self.time_deltas = np.array([1,2,3,4]).reshape(-1, 1)
        self.prices = np.array([1,2,3,4]).reshape(-1, 1)
    
    def get_spot_instance_price(self, region, instance_type, curr_time):
        client = boto3.client('ec2', region_name=region)
        response = client.describe_spot_price_history(
            InstanceTypes=[instance_type],
            ProductDescriptions=['Linux/UNIX'],
            StartTime=datetime.datetime.now().isoformat()
        )
        if 'SpotPriceHistory' in response:
            spot_price_history = response['SpotPriceHistory']
            if spot_price_history:
                return spot_price_history[0]['SpotPrice']
        return None

    def poll_price(self):
        self.mutex_lock.acquire()
        while True:
            curr_time = datetime.datetime.now()

            price = self.get_spot_instance_price('us-west-2', 'm5.large', curr_time)
            if price != None:
                self.time_deltas = np.append(self.time_deltas, curr_time.timestamp())
                self.prices = np.append(self.prices, price)
            
            print(self.time_deltas)
            print(self.prices)

            if self.predict_intention:
                self.mutex_lock.release()
                time.sleep(30)

                self.mutex_lock.acquire()
            else:
                time.sleep(30)
    
    def compute_preempt_prob_without_max(self):
        # TODO: how to estimate preemption probability if preemption does not rely on price
        return 0.005

    def compute_preempt_prob_with_max(self):
        degree = 2 

        # get current time_delta
        current_time = datetime.datetime.now()
        x_val = (current_time - self.start_time).total_seconds()

        # define regression model
        poly = PolynomialFeatures(degree)
        x_train_poly = poly.fit_transform(self.time_deltas)
        x_predict_poly = poly.transform(np.array([current_time.timestamp()]).reshape(-1, 1))

        model = LinearRegression()
        model.fit(x_train_poly, self.prices)

        price_predict = model.predict(x_predict_poly)

        # print(current_time.timestamp())
        # print(price_predict)

        # TODO: estimate probability from the price
        # Challenge 1: hard to customize for each instance type and location
        # challenge 2: how to continually fit in new data without retrain
    
    def compute_preemption_prob(self):
        self.predict_intention = True
        self.mutex_lock.acquire()

        prob = 0
        if self.max_price == -1:
            prob = self.compute_preempt_prob_without_max()
        else:
            prob = self.compute_preempt_prob_with_max()
        
        self.predict_intention = False
        self.mutex_lock.release()
        return prob


P = PreemptionEstimator(10)
P.poll_price()
# P.compute_preemption_prob()

# print(P.prob)
