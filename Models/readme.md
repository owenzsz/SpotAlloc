### Initialization
```
ra = ResourceAllocator()
```

### register microservices
After initialization, the resource allocator must first register microservices with the following code
```
ra.register_microservice("custom_identifier")
```
After registering, corresponding price poller needs to be manually started using a separate thread by (please wrap the following code in a new thread)
```
ra.start_poll_one("custom_identifier")
```
This will start the price polling process which gets up-to-date price data every 30 seconds

### log status
Each microservice is responsible to log corresponding service status for future optimization using the following code
```
ra.log_data("target_microservice_identifier", 1, {"load": [10], "resource": [40], "performance":[100]})
```
this function is in the form of `log_data(identifier, timestamp, dict_data)`

### demand optimization
```
ret = ra.allocate()
```
This returns a vector, with each element the optimized allocation for each microservice of the application
