import numpy as np

import performance_estimator
from performance_estimator import PerformanceEstimator
from load_estimator import LoadEstimator
from MQ import MessageQueue

import threading

# FEATURE_NUM = 1 # FEATURE_NUM is the number of metric used for predictions

# microservice-level resource learner
class ResourceLearner(object):
    def __init__(self, max_local_data_table_size=-1, filepath=None):
        self.max_local_data_table_size = max_local_data_table_size
        self.filepath = filepath

        # self.lock = threading.Lock()

        self.mq = MessageQueue(self.max_local_data_table_size, self.filepath)
        self.performance_estimator = PerformanceEstimator()
        self.load_estimator = LoadEstimator()

        # self.x_train_perf = np.empty((0,FEATURE_NUM))
        # self.y_train_perf = np.empty((0,))

        # self.train_load = np.empty((0,))
        self.initialized = False
        self.initialize()

    def initialize(self):
        self.performance_estimator.initialize_model()
        # self.load_estimator.initialize_model()

    def put_data(self, timestamp, data):
        # self.lock.acquire()
        self.mq.offer(timestamp, data)
        # self.lock.release()

    def get_model(self):
        self.update()
        return self.performance_estimator.get_model()

    def load_data(self):
        # self.lock.acquire()
        if self.mq.empty():
            # self.lock.release()
            # print("Enter return false")
            return False

        x_perf = np.empty((0,performance_estimator.FEATURE_NUM))
        y_perf = np.empty((0,))
        load_data = np.empty((0,))
        while not self.mq.empty():
            data = self.mq.poll()
            # print(np.concatenate([value for key, value in data.items() if (key != 'timestamp') and (key != 'performance') and (key != 'load')]))
            # x_perf = np.append(x_perf, np.concatenate([value for key, value in data.items() if (key != 'timestamp') and (key != 'performance')]).reshape(1,-1), axis=0)
            x_extract = [value for key, value in data.items() if key not in ['timestamp', 'performance']]
            # x_extract = np.concatenate(x_extract).reshape(1,-1)
            x_extract = [np.atleast_2d(np.array(value)) for value in x_extract]
            x_extract = np.concatenate(x_extract, axis=1)


            # print(x_extract)
            # print(type(x_extract))
            # print(x_extract.shape)
            x_perf = np.append(x_perf, x_extract, axis=0)

            # print(x_perf)
            
            y_perf = np.append(y_perf, np.array([data['performance']]))

            load_data = np.append(load_data, np.array([data['load']]))

        # self.lock.release()

        self.performance_estimator.load_data(x_perf, y_perf)
        self.load_estimator.load_data(load_data)
        
        # print("Enter return true")
        # return x_perf, y_perf, load_data
        return True
    
    def update(self):
        ret = self.load_data()
        # print(ret)
        if ret:
            self.initialized = True
            self.performance_estimator.update()
            self.load_estimator.update()

    def predict_performance(self, resource_param):
        self.update()
        if self.initialized is False:
            return None
        # print(resource_param)
        # resource_param.extend(self.load_estimator.predict().tolist())
        resource_param = np.append(resource_param, self.load_estimator.predict())
        # print(resource_param)
        return self.performance_estimator.predict(resource_param)



# rl = ResourceLearner(4, r"/home/wangzhe/Desktop/CS525/SpotAlloc/Models/mq_test.csv")
# rl.initialize()
# rl.put_data(1, {"load": [10], "resource": [40], "performance":[100]})
# rl.put_data(1, {"load": [10], "resource": [50], "performance":[100]})
# rl.put_data(2, {"load": [20], "resource": [60], "performance":[200]})
# rl.put_data(3, {"load": [30], "resource": [70], "performance":[300]})
# rl.put_data(4, {"load": [40], "resource": [80], "performance":[400]})
# rl.put_data(5, {"load": [50], "resource": [90], "performance":[500]})


# # rl.update()
# res = rl.predict_performance([50])
# print(res)

# res = rl.predict_performance([60])
# print(res)

# rl.put_data(1, {"load": [10], "resource": [100], "performance":[600]})
# rl.put_data(1, {"load": [10], "resource": [110], "performance":[700]})
# rl.put_data(2, {"load": [20], "resource": [130], "performance":[900]})
# rl.put_data(3, {"load": [30], "resource": [120], "performance":[800]})
# rl.put_data(4, {"load": [40], "resource": [140], "performance":[1000]})
# rl.put_data(5, {"load": [50], "resource": [150], "performance":[1100]})

# # rl.update()
# res = rl.predict_performance([150])
# print(res)

# res = rl.predict_performance([160])
# print(res)
# res = rl.predict_performance([50])
# print(res)
