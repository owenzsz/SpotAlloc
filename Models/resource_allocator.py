from resource_learner import ResourceLearner
from preemption_estimator import PreemptionEstimator

from scipy.optimize import minimize
import numpy as np

import threading

SUCCESS = 100
MICROSERICE_ALREADY_REGISTERED = 101

# application-level resource allocator
class ResourceAllocator(object):
    def __init__(self, resource):
        self.id_mapping = {}
        self.index_mapping = {}

        self.n_microservices = 0
        self.resource_learner_pool = []
        self.preemption_estimator_pool = []

        # self.preemptions = None
        # self.performance_models = None

        self.optimal = None

        self.resource = resource

        self.preemptions = None

    def log_data(self, identifier, timestamp, data):
        id = self.id_mapping[identifier]
        if self.resource_learner_pool[id].put_data(timestamp, data) == 0:
            return SUCCESS
    
    def register_microservice(self, identifier, max_price=-1):
        if identifier not in self.id_mapping:
            self.id_mapping[identifier] = self.n_microservices
            self.index_mapping[self.n_microservices] = identifier
            self.n_microservices += 1
            self.resource_learner_pool.append(ResourceLearner())
            self.preemption_estimator_pool.append(PreemptionEstimator(max_price=-1))
            return SUCCESS
        else:
            return MICROSERICE_ALREADY_REGISTERED
        
    def start_poll_one(self, identifier):
        id = self.id_mapping[identifier]

        self.preemption_estimator_pool[id].poll_price()
    
    def start_poll_all(self):
        for i in range(self.n_microservices):
            self.preemption_estimator_pool[i].poll_price()
        
    def start_poll(self, identifier):
        thread = threading.Thread(target=self.start_poll_one, args=(identifier))
        # print("Started pricing polling service for microservice", identifier)
        thread.start()

    # def get_estimation(self):
    #     self.preemptions = [self.preemption_estimator_pool[i].compute_preemption_prob() for i in range(self.n_microservices)]
    #     # self.performance_models = [self.resource_learner_pool[i].get_model() for i in range(self.n_microservices)]
    #     # self.performance_models = [self.resource_learner_pool[i].get_model() for i in range(self.n_microservices)]


    def objective_function(self, a):
        # return -np.dot(a, l)  # Negating as we want to maximize
        # print(self.preemptions)

        # print(self.resource_learner_pool[0].predict_performance(a))
        # print([self.resource_learner_pool[i].predict_performance(a) for i in range(self.n_microservices) if self.resource_learner_pool[i] is not None])
        # print([self.resource_learner_pool[i].predict_performance(a[i]) for i in range(self.n_microservices) if self.resource_learner_pool[i] is not None])
        return np.sum([self.resource_learner_pool[i].predict_performance(a[i]) for i in range(self.n_microservices) if self.resource_learner_pool[i] is not None])

    def constraint(self, a):
        # return 1.0 - np.sum(a)
        resource_utlization = 0
        for i in range(a.size):
            resource_utlization += (a[i] / (1-self.preemptions[i]))
        return self.resource - resource_utlization
        # return self.resource - np.sum(a)
        # return np.sum(a) - 1

    def optimize(self):
        # Initial guess for a
        # initial_a = np.random.rand(self.n_microservices)
        # initial_a /= np.sum(initial_a)  # Normalize initial guess to satisfy the constraint

        initial_a_tmp = np.random.rand(self.n_microservices)
        initial_a = np.full_like(initial_a_tmp, (self.resource/self.n_microservices))
        for i in range(initial_a.size):
            initial_a[i] = initial_a[i] * (1-self.preemptions[i])

        # Bounds for each component of a (0 <= a_i <= 1)
        bounds = [(0, self.resource) for _ in range(len(initial_a))]

        # Constraint dictionary
        constraints = {'type': 'eq', 'fun': self.constraint}

        # print("initial a after preemption:", initial_a)
        # Minimize the negative of the objective function to maximize
        result = minimize(self.objective_function, initial_a, bounds=bounds, constraints=constraints, options={'maxiter': 1000})
        # print(result)
        optimal_a = result.x
        # optimal_a /= np.sum(optimal_a)  # Normalize to ensure the sum is 1

        return optimal_a

    def allocate(self):
        # print("Enter allocate")
        self.preemptions = [self.preemption_estimator_pool[i].compute_preemption_prob() for i in range(self.n_microservices)]
        # print("preemption: ", self.preemptions)
        optimized_demands = self.optimize()
        print("Optimized allocation: ", optimized_demands)

        alloc = {}
        # aggregate = sum([optimized_demands[i] / (1-self.preemptions[i]) for i in range(self.n_microservices)])

        # for i in range(self.n_microservices):
        #     alloc[self.index_mapping[i]] = (optimized_demands[i] / (1-self.preemptions[i])) / aggregate

        for i in range(self.n_microservices):
            alloc[self.index_mapping[i]] = optimized_demands[i] / (1-self.preemptions[i])
        # return optimized_demands / preemptions
        return alloc


if __name__ == '__main__':
    # ra = ResourceAllocator()
    # ra.register_microservice("ms1")
    # ra.log_data("ms1", 1, {"load": [10], "resource": [40], "latency":[100]})
    # ra.log_data("ms1", 1, {"load": [10], "resource": [40], "latency":[100]})
    # ra.log_data("ms1", 2, {"load": [20], "resource": [60], "latency":[200]})
    # ra.log_data("ms1", 3, {"load": [30], "resource": [70], "latency":[300]})

    # # print("Enter 1")

    # ret = ra.allocate()


    # print(ret)

    # # ra.start_poll_all()

    ra = ResourceAllocator(100)
    ra.register_microservice("a")
    ra.start_poll("a")

    # print("enter 1")


    # ra.log_data("a", 1, {"load": [10], "resource": [40], "latency":[100]})
    # ra.log_data("a", 2, {"load": [20], "resource": [60], "latency":[200]})
    ra.log_data("a", 2, {"load": [42.8571], "resource": [42.18], "latency":[10]})


    # print("enter 2")

    ret = ra.allocate()

    # print("enter 3")
    print(ret)


    ra.register_microservice("b")
    ra.start_poll("b")


    # ra.log_data("b", 1, {"load": [10], "resource": [40], "latency":[100]})
    # ra.log_data("b", 2, {"load": [20], "resource": [60], "latency":[200]})
    ra.log_data("b", 2, {"load": [35.71429], "resource": [51.289], "latency":[7.495427]})


    ret = ra.allocate()
    print(ret)


    ra.register_microservice("c")
    ra.start_poll("c")

    # ra.log_data("c", 1, {"load": [10], "resource": [40], "latency":[100]})
    # ra.log_data("c", 2, {"load": [20], "resource": [60], "latency":[200]})
    # ra.log_data("c", 2, {"load": [20], "resource": [60], "latency":[200]})
    # ra.log_data("c", 3, {"load": [30], "resource": [70], "latency":[300]})
    ra.log_data("c", 1, {"load": [37.0830], "resource": [27.2186], "latency":[10]})


    ret = ra.allocate()
    print(ret)

    ra.register_microservice("d")
    ra.start_poll("d")


    ra.log_data("d", 1, {"load": [45.7143], "resource": [13.1289], "latency":[10]})



    ra.register_microservice("e")
    ra.start_poll("e")

    ra.log_data("e", 1, {"load": [42.8571], "resource": [10.681], "latency":[10]})


    ret = ra.allocate()
    print(ret)
