import json

# Sample data provided as a list of log entries
log_entries = [
'2024/04/13 14:16:22 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":463,"my-microservice-3":462,"my-microservice-4":462,"my-microservice-5":463},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:16:22-05:00"}',
'2024/04/13 14:16:31 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":397,"my-microservice-3":398,"my-microservice-4":398,"my-microservice-5":397},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:16:31-05:00"}',
'2024/04/13 14:16:41 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":386,"my-microservice-3":385,"my-microservice-4":385,"my-microservice-5":386},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:16:41-05:00"}',
'2024/04/13 14:16:51 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":385,"my-microservice-3":386,"my-microservice-4":386,"my-microservice-5":385},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:16:51-05:00"}',
'2024/04/13 14:17:01 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":385,"my-microservice-3":385,"my-microservice-4":385,"my-microservice-5":385},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:17:01-05:00"}',
'2024/04/13 14:17:11 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":386,"my-microservice-3":386,"my-microservice-4":386,"my-microservice-5":386},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:17:11-05:00"}',
'2024/04/13 14:17:21 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":385,"my-microservice-3":385,"my-microservice-4":385,"my-microservice-5":385},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:17:21-05:00"}',
'2024/04/13 14:17:31 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":386,"my-microservice-3":386,"my-microservice-4":386,"my-microservice-5":386},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:17:31-05:00"}',
'2024/04/13 14:17:41 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":385,"my-microservice-3":385,"my-microservice-4":385,"my-microservice-5":385},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:17:41-05:00"}',
'2024/04/13 14:17:51 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":77,"my-microservice-2":386,"my-microservice-3":386,"my-microservice-4":386,"my-microservice-5":386},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:17:51-05:00"}',
'2024/04/13 14:18:01 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":1853,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:18:01-05:00"}',
'2024/04/13 14:18:11 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":720,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:18:11-05:00"}',
'2024/04/13 14:18:21 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":386,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:18:21-05:00"}',
'2024/04/13 14:18:31 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:18:31-05:00"}',
'2024/04/13 14:18:41 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":386,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:18:41-05:00"}',
'2024/04/13 14:18:51 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:18:51-05:00"}',
'2024/04/13 14:19:01 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":386,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:19:01-05:00"}',
'2024/04/13 14:19:11 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:19:11-05:00"}',
'2024/04/13 14:19:21 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":386,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:19:21-05:00"}',
'2024/04/13 14:19:31 {"algorithm":"credit","data":{"TotalAllocableResources":1930,"my-microservice-1":385,"my-microservice-2":19,"my-microservice-3":19,"my-microservice-4":19,"my-microservice-5":19},"level":"INFO","message":"Credit-based scheduling resource allocation summary","timestamp":"2024-04-13T14:19:31-05:00"}',
'2024/04/13 14:20:10 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:20:10-05:00"}',
'2024/04/13 14:20:19 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:20:19-05:00"}',
'2024/04/13 14:20:29 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:20:29-05:00"}',
'2024/04/13 14:20:39 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:20:39-05:00"}',
'2024/04/13 14:20:49 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:20:49-05:00"}',
'2024/04/13 14:20:59 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:20:59-05:00"}',
'2024/04/13 14:21:09 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:21:09-05:00"}',
'2024/04/13 14:21:19 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:21:19-05:00"}',
'2024/04/13 14:21:29 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:21:29-05:00"}',
'2024/04/13 14:21:39 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":100,"my-microservice-2":463,"my-microservice-3":463,"my-microservice-4":463,"my-microservice-5":463},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:21:39-05:00"}',
'2024/04/13 14:21:49 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:21:49-05:00"}',
'2024/04/13 14:21:59 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:21:59-05:00"}',
'2024/04/13 14:22:09 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:22:09-05:00"}',
'2024/04/13 14:22:19 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:22:19-05:00"}',
'2024/04/13 14:22:29 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:22:29-05:00"}',
'2024/04/13 14:22:39 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:22:39-05:00"}',
'2024/04/13 14:22:49 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:22:49-05:00"}',
'2024/04/13 14:22:59 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:22:59-05:00"}',
'2024/04/13 14:23:09 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:23:09-05:00"}',
'2024/04/13 14:23:19 {"algorithm":"maxmin","data":{"TotalAllocableResources":1930,"my-microservice-1":1852,"my-microservice-2":100,"my-microservice-3":100,"my-microservice-4":100,"my-microservice-5":100},"level":"INFO","message":"Max-min scheduling resource allocation summary","timestamp":"2024-04-13T14:23:19-05:00"}',
]

# Initialize dictionaries to hold the aggregate resources for each service by algorithm
aggregate_resources = {
    "credit": 0,
    "maxmin": 0,
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
        threshold = 1930 * 0.8
        # Skip the total allocable resources entry and update the aggregate resources
        for service, resources in resources_data.items():
            if service == "TotalAllocableResources":
                continue
            if resources > threshold:
                 aggregate_resources[algorithm] += 1

for algo, val in aggregate_resources.items():
    print(algo, val)
    aggregate_resources[algo] = val / 20

print(aggregate_resources)


# Calculate and print the fairness scores for each algorithm
# for algorithm, resources_dict in aggregate_resources.items():
#     score = calculate_domination_time(resources_dict)
#     print(f"Long-term Fairness Score for {algorithm}: {score}")