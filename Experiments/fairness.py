import json

# Sample data provided as a list of log entries
log_entries = [
'2024/03/30 13:11:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":486,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:11:39-05:00"}',
'2024/03/30 13:13:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":729,"my-microservice-2":385,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:13:39-05:00"}',
'2024/03/30 13:15:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":386,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:15:39-05:00"}',
'2024/03/30 13:17:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":385,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:17:39-05:00"}',
'2024/03/30 13:19:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":1527},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:19:39-05:00"}',
'2024/03/30 13:21:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":486},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:21:39-05:00"}',
'2024/03/30 13:23:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":385},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:23:39-05:00"}',
'2024/03/30 13:25:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":530,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":97},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:25:39-05:00"}',
'2024/03/30 13:27:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":710,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:27:39-05:00"}',
'2024/03/30 13:29:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":386,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:29:39-05:00"}',
'2024/03/30 13:31:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:31:39-05:00"}',
'2024/03/30 13:33:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:33:39-05:00"}',
'2024/03/30 13:35:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":386,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:35:39-05:00"}',
'2024/03/30 13:37:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:37:39-05:00"}',
'2024/03/30 13:39:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":97,"my-microservice-2":100,"my-microservice-3":1530,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:39:39-05:00"}',
'2024/03/30 13:41:39 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":97,"my-microservice-2":100,"my-microservice-3":1530,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-03-30T13:41:39-05:00"}',
'2024/03/30 13:46:27 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":1530,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:46:27-05:00"}',
'2024/03/30 13:48:27 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":601,"my-microservice-4":558,"my-microservice-5":569},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:48:27-05:00"}',
'2024/03/30 13:50:27 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":711,"my-microservice-2":778,"my-microservice-3":100,"my-microservice-4":240,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:50:27-05:00"}',
'2024/03/30 13:52:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":1530,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:52:26-05:00"}',
'2024/03/30 13:54:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1530,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:54:26-05:00"}',
'2024/03/30 13:56:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":1530},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:56:26-05:00"}',
'2024/03/30 13:58:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":1530,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T13:58:26-05:00"}',
'2024/03/30 14:00:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":1529,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:00:26-05:00"}',
'2024/03/30 14:02:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1530,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:02:26-05:00"}',
'2024/03/30 14:04:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":671,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:04:26-05:00"}',
'2024/03/30 14:06:27 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1530,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:06:27-05:00"}',
'2024/03/30 14:08:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":1530,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:08:26-05:00"}',
'2024/03/30 14:10:26 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":1529},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:10:26-05:00"}',
'2024/03/30 14:12:27 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":1530},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-03-30T14:12:27-05:00"}'
]

# Initialize dictionaries to hold the aggregate resources for each service by algorithm
aggregate_resources = {
    "credit": {},
    "maxmin": {},
}

# Process each log entry
for entry in log_entries:
    # Find the start of the JSON substring
    json_start = entry.find('{"algorithm":')
    
    # Directly parse the JSON part of the entry
    if json_start != -1:
        json_str = entry[json_start:]
        data = json.loads(json_str)
        
        algorithm = data["algorithm"]  # Identify the algorithm used
        resources_data = data["data"]

        # Skip the total allocable resources entry and update the aggregate resources
        for service, resources in resources_data.items():
            if service == "TotalAllocableResources":
                continue
            if service not in aggregate_resources[algorithm]:
                aggregate_resources[algorithm][service] = 0
            aggregate_resources[algorithm][service] += resources

print(aggregate_resources)
# Function to calculate the fairness score
def calculate_fairness_score(aggregate_dict):
    mean_aggregate_resource = sum(aggregate_dict.values()) / len(aggregate_dict)
    fairness_score = sum(abs(resources - mean_aggregate_resource) for resources in aggregate_dict.values())
    return fairness_score

# Calculate and print the fairness scores for each algorithm
for algorithm, resources_dict in aggregate_resources.items():
    score = calculate_fairness_score(resources_dict)
    print(f"Long-term Fairness Score for {algorithm}: {score}")