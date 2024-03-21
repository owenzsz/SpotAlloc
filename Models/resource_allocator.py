from resource_learner import ResourceLearner
from preemption_estimator import PreemptionEstimator

from scipy.optimize import minimize
import numpy as np

# application-level resource allocator
class ResourceAllocator(object):
    def __init__(self):
        self.id_mapping = {}

        self.n_microservices = 0
        self.resource_learner_pool = []
        self.preemption_estimator_pool = []

        # self.preemptions = None
        # self.performance_models = None

        self.optimal = None

    def log_data(self, identifier, timestamp, data):
        id = self.id_mapping[identifier]
        self.resource_learner_pool[id].put_data(timestamp, data)
    
    def register_microservice(self, identifier, max_price=-1):
        if identifier not in self.id_mapping:
            self.id_mapping[identifier] = self.n_microservices
            self.n_microservices += 1
            self.resource_learner_pool.append(ResourceLearner())
            self.preemption_estimator_pool.append(PreemptionEstimator(max_price=-1))
        
    def start_poll_one(self, identifier):
        id = self.id_mapping[identifier]

        self.preemption_estimator_pool[id].poll_price()
    
    def start_poll_all(self):
        for i in range(self.n_microservices):
            self.preemption_estimator_pool[i].poll_price()

    # def get_estimation(self):
    #     self.preemptions = [self.preemption_estimator_pool[i].compute_preemption_prob() for i in range(self.n_microservices)]
    #     # self.performance_models = [self.resource_learner_pool[i].get_model() for i in range(self.n_microservices)]
    #     # self.performance_models = [self.resource_learner_pool[i].get_model() for i in range(self.n_microservices)]


    def objective_function(self, a):
        # return -np.dot(a, l)  # Negating as we want to maximize
        # print(self.preemptions)

        # print(self.resource_learner_pool[0].predict_performance(a))
        # print([self.resource_learner_pool[i].predict_performance(a) for i in range(self.n_microservices) if self.resource_learner_pool[i] is not None])

        return -np.sum([self.resource_learner_pool[i].predict_performance(a) for i in range(self.n_microservices) if self.resource_learner_pool[i] is not None])

    def constraint(self, a):
        return 1.0 - np.sum(a)

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

        return optimized_demands / preemptions


ra = ResourceAllocator()
ra.register_microservice("ms1")
ra.log_data("ms1", 1, {"load": [10], "resource": [40], "performance":[100]})
ra.log_data("ms1", 1, {"load": [10], "resource": [40], "performance":[100]})
ra.log_data("ms1", 2, {"load": [20], "resource": [60], "performance":[200]})
ra.log_data("ms1", 3, {"load": [30], "resource": [70], "performance":[300]})

# print("Enter 1")

ret = ra.allocate()


print(ret)

# ra.start_poll_all()
