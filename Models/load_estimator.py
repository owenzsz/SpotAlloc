import numpy as np
import math
from sklearn.kernel_ridge import KernelRidge
import statsmodels.api as sm
import scipy.stats as stats


# microservice-level load estimator
# assume constant step size for the time series model
class LoadEstimator(object):
    def __init__(self, data_logger, phi=0.7, theta=0.3):
        self.data_logger = data_logger
        self.phi = -1
        self.theta = -1

        self.data = None

        self.model = None

        self.setParam(phi, theta)

    def setParam(self, phi=0.7, theta=0.3):
        self.phi = 0.7
        self.theta = theta

    def load_data(self):
        if self.model != None:
            return np.random.normal(size=10)
            # return np.array([1,2,3,4]), np.array([1,2,3,4])

        np.random.seed(0)
        n_samples = 100
        # Generate AR(1) time series data
        self.data = [np.random.normal() for _ in range(n_samples)]
        # print("old data:", self.data)
        ar_data = self.data
        for i in range(1, n_samples):
            ar_data[i] = self.phi * ar_data[i-1] + np.random.normal()

        # Add MA(1) component
        ma_data = [ar_data[i] + self.theta * ar_data[i-1] + np.random.normal() for i in range(1, n_samples)]
        return ma_data
    
    def loadEstimate(self):
        if self.model == None:

            # print("old data:", ma_data)
            # Create ARMA(1,1) model
            # self.model = sm.tsa.ARIMA(ma_data, order=(1, 0,1))
            self.model = sm.tsa.ARIMA(self.load_data(), order=(1, 0,1))

            # Fit the model
            self.model = self.model.fit()
        else:
            # new_data = self.load_data()
        
            # Update the model with new observations
            self.model = self.model.append(self.load_data())

        # print(self.model.summary())

        # Forecast future values
        # forecast_values, stderr, conf_int = result.get_forecast(steps=10)  # Forecast 10 future values
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

        # # Print confidence bounds
        # print("forecast_values:", forecast_values)
        # print("Lower Bound:", lower_bound)
        # print("Upper Bound:", upper_bound)

        return forecast_values, lower_bound, upper_bound


le = LoadEstimator(None)
pred, l, u = le.loadEstimate()
print(pred, l, u)

pred, l, u = le.loadEstimate()
print(pred, l, u)
