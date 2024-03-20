import time
from flask import Flask, Response, send_file
from prometheus_client import Summary, generate_latest, CollectorRegistry

app = Flask(__name__)

# Create metrics
REQUEST_LATENCY = Summary('request_latency_milliseconds', 'Request latency in milliseconds')

def cpu_intensive_task():
    # Simulate a CPU-intensive task by performing a computationally expensive operation
    result = 0
    for i in range(10000000):
        result += i * i
    return result

@app.route('/')
def hello():
    start_time = time.time()
    latency = (time.time() - start_time) * 1000
    REQUEST_LATENCY.observe(latency)
    cpu_intensive_task()

    return send_file('index.html')

@app.route('/metrics')
def metrics():
    # Generate the metrics data
    registry = CollectorRegistry()
    registry.register(REQUEST_LATENCY)

    metrics_data = generate_latest(registry) #120 seconds

    # Return the metrics data as a response
    return Response(metrics_data, content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)