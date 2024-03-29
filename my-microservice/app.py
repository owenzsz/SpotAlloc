import time
import asyncio
from flask import Flask, Response, send_file, request, abort
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Create metrics
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request Latency In Seconds', ['method', 'endpoint', 'status'], buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1, 2.5, 5, 7.5, 10, float("inf")))
REQUEST_COUNT = Counter('request_count', 'Total request count of the host', ['method', 'endpoint', 'status'])

async def cpu_intensive_task():
    # Simulate a CPU-intensive task by performing a computationally expensive operation
    result = 0
    for i in range(1000000):
        result += i * i
    return result

@app.before_request
def set_timeout():
    # Set a timeout for the request
    request.environ['REQUEST_TIMEOUT'] = 10  # Timeout in seconds

@app.route('/')
async def hello():
    start_time = time.time()
    status_code = 200
    try:
        await asyncio.wait_for(cpu_intensive_task(), timeout=10)  # Timeout in seconds
    except asyncio.TimeoutError:
        status_code = 504  # Gateway Timeout
        abort(504)
    finally:
        latency = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.path, status=status_code).observe(latency)

    return send_file('index.html')

@app.route('/metrics')
def metrics():
    # Return the metrics data as a response
    return Response(generate_latest(), content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)