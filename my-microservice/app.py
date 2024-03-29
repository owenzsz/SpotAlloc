import time
from flask import Flask, Response, send_file, request
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry

app = Flask(__name__)

# Create metrics
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request Latency In Seconds', ['method', 'endpoint'], buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1, 2.5, 5, 7.5, 10, float("inf")))
REQUEST_COUNT = Counter('request_count', 'Total request count of the host', ['method', 'endpoint'])

def cpu_intensive_task():
    # Simulate a CPU-intensive task by performing a computationally expensive operation
    result = 0
    for i in range(1000000):
        result += i * i
    return result

@app.route('/')
def hello():
    start_time = time.time()
    cpu_intensive_task()
    latency = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
    return send_file('index.html')

@app.route('/metrics')
def metrics():
    # Return the metrics data as a response
    return Response(generate_latest(), content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)