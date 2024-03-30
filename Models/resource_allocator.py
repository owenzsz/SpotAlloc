from resource_learner import ResourceLearner
from preemption_estimator import PreemptionEstimator

from scipy.optimize import minimize
import numpy as np

import threading

SUCCESS = 100
MICROSERICE_ALREADY_REGISTERED = 101

# application-level resource allocator
class ResourceAllocator(object):
    def __init__(self):
        self.id_mapping = {}
        self.index_mapping = {}

        self.n_microservices = 0
        self.resource_learner_pool = []
        self.preemption_estimator_pool = []

        # self.preemptions = None
        # self.performance_models = None

        self.optimal = None

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
        print("Started pricing polling service for microservice", identifier)
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

        return np.sum([self.resource_learner_pool[i].predict_performance(a[i]) for i in range(self.n_microservices) if self.resource_learner_pool[i] is not None])

    def constraint(self, a):
        # return 1.0 - np.sum(a)
        return np.sum(a) - 1

    def optimize(self):
        # Example usage
        # n = 5  # Dimension of vectors a and l
        l = np.random.rand(self.n_microservices)  # Randomly initialize vector l

        # Initial guess for a
        initial_a = np.random.rand(self.n_microservices)
        initial_a /= np.sum(initial_a)  # Normalize initial guess to satisfy the constraint

        # Bounds for each component of a (0 <= a_i <= 1)
        bounds = [(0, 1) for _ in range(len(initial_a))]

        # Constraint dictionary
        constraints = {'type': 'eq', 'fun': self.constraint}

        print("initial a:", initial_a)
        # Minimize the negative of the objective function to maximize
        result = minimize(self.objective_function, initial_a, bounds=bounds, constraints=constraints)

        optimal_a = result.x
        optimal_a /= np.sum(optimal_a)  # Normalize to ensure the sum is 1

        print("Optimal a:", optimal_a)
        print("Objective value:", -result.fun)  # Objective value is negated due to maximizing

        return optimal_a

    def allocate(self):
        # print("Enter allocate")
        preemptions = [self.preemption_estimator_pool[i].compute_preemption_prob() for i in range(self.n_microservices)]
        print(preemptions)
        optimized_demands = self.optimize()
        print(optimized_demands)

        alloc = {}
        aggregate = sum([optimized_demands[i] / (1-preemptions[i]) for i in range(self.n_microservices)])
        for i in range(self.n_microservices):
            alloc[self.index_mapping[i]] = (optimized_demands[i] / (1-preemptions[i])) / aggregate

        # return optimized_demands / preemptions
        return alloc


if __name__ == '__main__':
    # ra = ResourceAllocator()
    # ra.register_microservice("ms1")
    # ra.log_data("ms1", 1, {"load": [10], "resource": [40], "performance":[100]})
    # ra.log_data("ms1", 1, {"load": [10], "resource": [40], "performance":[100]})
    # ra.log_data("ms1", 2, {"load": [20], "resource": [60], "performance":[200]})
    # ra.log_data("ms1", 3, {"load": [30], "resource": [70], "performance":[300]})

    # # print("Enter 1")

    # ret = ra.allocate()


    # print(ret)

    # # ra.start_poll_all()

    ra = ResourceAllocator()
    ra.register_microservice("a")
    ra.start_poll("a")

    # print("enter 1")

    # ra.log_data("a", 1, {"load": [10], "resource": [40], "performance":[100]})
    # ra.log_data("a", 2, {"load": [20], "resource": [60], "performance":[200]})
    ra.log_data("a", 2, {"load": [0.428571], "resource": [100], "performance":[10]})

    # print("enter 2")

    ret = ra.allocate()

    # print("enter 3")
    print(ret)


    ra.register_microservice("b")
    ra.start_poll("b")

    # ra.log_data("b", 1, {"load": [10], "resource": [40], "performance":[100]})
    # ra.log_data("b", 2, {"load": [20], "resource": [60], "performance":[200]})
    ra.log_data("b", 2, {"load": [1.171429], "resource": [101], "performance":[7.495427]})

    ret = ra.allocate()
    print(ret)


    ra.register_microservice("c")
    ra.start_poll("c")

    # ra.log_data("c", 1, {"load": [10], "resource": [40], "performance":[100]})
    # ra.log_data("c", 2, {"load": [20], "resource": [60], "performance":[200]})
    # ra.log_data("c", 2, {"load": [20], "resource": [60], "performance":[200]})
    # ra.log_data("c", 3, {"load": [30], "resource": [70], "performance":[300]})
    ra.log_data("c", 1, {"load": [0.370830], "resource": [200], "performance":[10]})

    ret = ra.allocate()
    print(ret)

    ra.register_microservice("d")
    ra.start_poll("d")

    ra.log_data("d", 1, {"load": [0.457143], "resource": [100], "performance":[10]})


    ra.register_microservice("e")
    ra.start_poll("e")

    ra.log_data("e", 1, {"load": [0.428571], "resource": [100], "performance":[10]})

    ret = ra.allocate()
    print(ret)
