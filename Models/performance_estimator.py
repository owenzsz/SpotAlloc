import numpy as np
import math
from sklearn.kernel_ridge import KernelRidge
import statsmodels.api as sm
import scipy.stats as stats

from MQ import MessageQueue 

FEATURE_NUM = 2 # FEATURE_NUM is the number of metric used for predictions

# microservice-level performance-resource estimator
class PerformanceEstimator(object):
    def __init__(self, nu=2.5, length_scale=1, alpha=1):
        self.nu = nu
        self.length_scale = length_scale
        self.alpha = alpha

        self.x_train = np.empty((0,FEATURE_NUM))
        self.y_train = np.empty((0,))

        self.model = None
    
    def resetParam(self, nu=2.5, length_scale=1, alpha=1):
        self.nu = nu
        self.length_scale = length_scale 
        self.alpha = alpha

    def initialize_model(self):
        # matern_kernel = lambda X, Y: (1 / (2 ** (self.nu - 1) * math.gamma(self.nu))) * \
        #                         (np.sqrt(2 * self.nu) * np.linalg.norm(X - Y) / self.length_scale) ** self.nu \
        #                         * math.gamma(self.nu + 1)

        # self.model = KernelRidge(alpha=self.alpha, kernel=matern_kernel)
        self.model = KernelRidge(kernel='poly', degree=2)

    def load_data(self, x_append, y_append):
        self.x_train = np.append(self.x_train, x_append, axis=0)
        self.y_train = np.append(self.y_train, y_append, axis=0)
    
    def get_model(self):
        return self.model
    
    def update(self):
        self.model.fit(self.x_train, self.y_train)
    
    # performance_param can be simple list [a,b,c,...]
    def predict(self, performance_param):
        # print(performance_param)
        performance_param = np.array(performance_param).reshape(1,-1)
        # print("performance param:", performance_param)
        return self.model.predict(performance_param)


if __name__ == '__main__':
    pe = PerformanceEstimator()
    pe.initialize_model()

    x_append = np.array([[10,40],[20,50],[30,60]]).reshape(-1,2)
    y_append = np.array([100, 200, 300])
    pe.load_data(x_append, y_append)
    pe.update()

    ret = pe.predict([10,40])
    print(ret)
    ret = pe.predict([40,70])
    print(ret)

    # print(pe.x_train)

    x_append = np.array([[40,70]]).reshape(-1,2)
    y_append = np.array([400])
    pe.load_data(x_append, y_append)
    pe.update()

    ret = pe.predict([10,40])
    print(ret)
    ret = pe.predict([30,70])
    print(ret)


    ret = pe.predict([40,70])
    print(ret)
    ret = pe.predict([50,80])
    print(ret)
    ret = pe.predict([60,90])
    print(ret)

    ret = pe.predict([70,100])
    print(ret)

    # print(pe.x_train)
