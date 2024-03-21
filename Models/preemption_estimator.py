import boto3
import datetime
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# import numpy as np
# import pandas as pd
# from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

import threading

SLEEP_TIME = 5

class PreemptionEstimator(object):
    def __init__(self, max_price=-1):
        self.prob = -1
        self.max_price = max_price

        self.mutex_lock = threading.Lock()
        self.predict_intention = False

        self.start_time = datetime.datetime.now()
        # self.time_deltas = np.empty()
        # self.prices = np.empty()
        self.time_deltas = np.array([])
        self.prices = np.array([])
        self.exceeds = np.array([])
    
    def add_data(self):
        self.time_deltas = np.append(self.time_deltas, [1,2,3,4])
        self.prices = np.append(self.prices, [1,2,3,4])
        self.exceeds = np.append(self.exceeds, [0,0,1,0])
    
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
                if float(price) > self.max_price:
                    self.exceeds = np.append(self.exceeds, 1)
                else:
                    self.exceeds = np.append(self.exceeds, 0)
            
            print(self.time_deltas)
            print(self.prices)
            print(self.exceeds)

            if self.predict_intention:
                self.mutex_lock.release()
                time.sleep(SLEEP_TIME)

                self.mutex_lock.acquire()
            else:
                time.sleep(SLEEP_TIME)
    
    def compute_preempt_prob_without_max(self):
        # TODO: how to estimate preemption probability if preemption does not rely on price
        return 0.005

    def compute_preempt_prob_with_max(self):
        current_time = datetime.datetime.now()

        # Standardize features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(self.time_deltas.reshape(-1,1))
        y_train = self.exceeds

        # print(self.time_deltas.reshape(-1,1))
        print(X_train_scaled)
        print(y_train)
        # Train logistic regression model
        model = LogisticRegression()
        model.fit(X_train_scaled, y_train)

        # Predict probability for a specific time
        specific_time = (current_time-self.start_time).total_seconds()
        specific_time_feature = scaler.transform([[specific_time]])
        probability = model.predict_proba(specific_time_feature)[0][1]
        print(f"Probability of price exceeding the function value at time {specific_time}: {probability}")
    
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


# P = PreemptionEstimator(10)
# # P.poll_price()

# P.add_data()
# P.compute_preemption_prob()

# print(P.prob)
