from flask import Flask, jsonify, request
from resource_allocator import ResourceAllocator
import resource_allocator
import sys

app = Flask(__name__)

if len(sys.argv) > 1:
    max_resource = int(sys.argv[1])
else:
    max_resource = 10

ra = ResourceAllocator(max_resource)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    identifier = data.get('identifier')
    if 'max_price' not in data:
        max_price = -1
    else:
        max_price = data.get('max_price')

    if 'slo' not in data:
        slo = 10
    else:
        slo = data.get('max_price')

    ret = ra.register_microservice(identifier, max_price, slo)

    if ret == resource_allocator.MICROSERICE_ALREADY_REGISTERED:
        return jsonify({'code': 200, 'message': "microservice already registered"})

    ret = ra.start_poll(identifier)

    return jsonify({'code': 100})
    
@app.route('/log', methods=['POST'])
def log():
    data = request.json
    identifier = data['identifier']
    timestamp = data['timestamp']
    log_data = data['data']

    ret = ra.log_data(identifier, timestamp, log_data)

    # print(identifier)
    # print(timestamp)
    # print(type(log_data))
    # print(log_data)

    if ret != resource_allocator.SUCCESS:
        return jsonify({'code': 200, 'message': "log data error"})

    return jsonify({'code': 100})

@app.route('/allocate', methods=['GET'])
def allocate ():
    result = ra.allocate()

    return jsonify({'demands': result})



if __name__ == '__main__':
    app.run(debug=True, port=3000)  # Run Flask app in debug mode


# SLO goal
# egalitarian number of service satisfy SLO goal / total numbe rof service