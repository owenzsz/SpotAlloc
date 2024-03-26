import numpy as np
import math
from sklearn.kernel_ridge import KernelRidge
import statsmodels.api as sm
import scipy.stats as stats

from MQ import MessageQueue


# microservice-level load estimator
# assume constant step size for the time series model
class LoadEstimator(object):
    def __init__(self, phi=0.7, theta=0.3):
        self.phi = phi
        self.theta = theta

        # self.data = np.empty((0,))
        self.data = np.array([])

        self.model = None

    def resetParam(self, phi=0.7, theta=0.3):
        self.phi = 0.7
        self.theta = theta

    # def initialize_model(self):
    #     self.model = sm.tsa.ARIMA(self.data, order=(1, 0,1))
    #     self.model = self.model.fit()

    def load_data(self, load_data):
        # print(self.model)
        # print(load_data)
        if self.model is None and len(load_data) == 1:
            # print("Enter 3")
            self.data = np.append(load_data, load_data)
        else:
            self.data = load_data
    
    def get_model(self):
        return self.model

    def update(self):
        # print("Enter update")
        if self.model is None:
            
            # print(self.data)
            self.model = sm.tsa.ARIMA(self.data, order=(1, 0,1))
            # print("get 1")
            # print(self.data.shape)
            self.model = self.model.fit()
            # print("get 2")
        else:
            # self.model = self.model.append(self.data)
            self.data = load_data

    def predict(self):
        forecast_results = self.model.get_forecast(steps=1)  # Forecast 10 future values
       
        # Extract forecasted values and standard errors
        forecast_values = forecast_results.predicted_mean
        stderr = forecast_results.se_mean

        # Calculate z-score for desired confidence level (e.g., 95%)
        confidence_level = 0.95
        z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)

        # Calculate confidence bounds
        lower_bound = forecast_values - z_score * stderr
        upper_bound = forecast_values + z_score * stderr
        # return forecast_values, lower_bound, upper_bound
        return forecast_values


if __name__ == '__main__':
    le = LoadEstimator()

    load = np.array([10])
    le.load_data(load)
    le.update()

    # v,l,u = le.predict()
    # print(v, l, u)


    # load = np.array([70,80,90,100])
    # le.load_data(load)
    # le.update()

    # v,l,u = le.predict()
    # print(v, l, u)
