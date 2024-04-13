import time
import asyncio
from flask import Flask, Response, send_file, request, abort, g
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry

app = Flask(__name__)

# Create metrics
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request Latency In Seconds', ['method', 'endpoint', 'status'], buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1, 2.5, 5, 7.5, 10, float("inf")))
REQUEST_COUNT = Counter('request_count', 'Total Request Count', ['method', 'endpoint'])

@app.before_request
def set_timeout_and_start_time():
    if request.path != '/metrics':
        # Set a timeout for the request
        request.environ['REQUEST_TIMEOUT'] = 10 # Timeout in seconds
        # Increment the request count
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
        # Record the start time of the request
        g.start_time = time.time()

@app.after_request
def record_request_metrics(response):
    if request.path != '/metrics':
        # Get the status code from the response
        status_code = response.status_code
        
        if hasattr(g, 'start_time'):
            # Calculate the request latency
            latency = time.time() - g.start_time
            
            # Record the request latency
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.path, status=status_code).observe(latency)
    
    return response

async def cpu_intensive_task():
    # Simulate a CPU-intensive task by performing a computationally expensive operation
    result = 0
    for i in range(1000000):
        result += i * i
    return result

@app.route('/')
async def hello():
    try:
        await asyncio.wait_for(cpu_intensive_task(), timeout=10)  # Timeout in seconds
    except asyncio.TimeoutError:
        abort(504)  # Gateway Timeout
    
    return send_file('index.html')

@app.route('/metrics')
def metrics():
    # Return the metrics data as a response
    return Response(generate_latest(), content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)