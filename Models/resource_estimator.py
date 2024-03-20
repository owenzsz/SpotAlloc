import numpy as np
import math
from sklearn.kernel_ridge import KernelRidge
import statsmodels.api as sm
import scipy.stats as stats

# microservice-level performance-resource estimator
class ResourceEstimator(object):
    # n_features is the number of micro-services in the application
    def __init__(self, data_logger, nu=2.5, length_scale=1, alpha=1):
        self.data_logger = data_logger
        self.nu = -1
        self.length_scale = -1
        self.alpha = -1

        self.x_train = None
        self.y_train = None

        self.model = None

        self.setParam(nu, length_scale, alpha)
    
    def setParam(self, nu=2.5, length_scale=1, alpha=1):
        self.nu = nu
        self.length_scale = length_scale 
        self.alpha = alpha

    # TODO: modify data logger. ideal case: data logger should log data more frequently, and each time data is read, it 
    # erase all data and waits for new one
    def load_data(self):
        if self.model != None:
            return np.random.rand(2,2), np.random.randn(2)
            # return np.array([1,2,3,4]), np.array([1,2,3,4])
        np.random.seed(0)
        n_samples = 100

        # return np.random.rand(n_samples, 2), np.sum(self.x_train, axis=1) + np.random.randn(n_samples)
        x = np.random.rand(n_samples, 2)  # Random feature values
        y = np.sum(x, axis=1) + np.random.randn(n_samples)  # Sum of features plus noise
        return x,y

    # x_pred: [performance, load]
    def resourceEstimate(self,x_pred):
        if self.model == None:
            self.x_train, self.y_train = self.load_data()

            matern_kernel = lambda X, Y: (1 / (2 ** (self.nu - 1) * math.gamma(self.nu))) * \
                                (np.sqrt(2 * self.nu) * np.linalg.norm(X - Y) / self.length_scale) ** self.nu \
                                * math.gamma(self.nu + 1)

            # Train the Kernel Ridge Regression model with Matern kernel
            self.model = KernelRidge(alpha=self.alpha, kernel=matern_kernel)
        else:
            x, y = self.load_data()
            self.x_train = np.append(self.x_train, x, axis=0)
            self.y_train = np.append(self.y_train, y, axis=0)

        # print(self.x_train)
        # Fit the model to the training data
        self.model.fit(self.x_train, self.y_train)

        # X_test = np.random.rand(2, 2)
        # y_pred = self.model.predict(X_test)

        # print("Predictions:", y_pred)

        return self.model.predict(x_pred)


re = ResourceEstimator(None)

x_pred = np.random.rand(2, 2)
y_pred = re.resourceEstimate(x_pred)
print(x_pred)
print(y_pred)

x_pred = np.random.rand(2, 2)
y_pred = re.resourceEstimate(x_pred)
print(x_pred)
print(y_pred)
