# Usage of Demand Estimator
Follow the steps to use the demand estimator. \
Step 1: install python and pip on the machine \
Step 2: use `pip install -r requirements.txt` to install dependencies required \
Step 3: `cd` to the Models directory and start the service by running `python3 main.py` or `python main.py` based on the naming of python on the machine \
Step 4: start using the api

# Backend API
## register
**description:** This url registers a microservice into the demand estimator. This is a must have step for each microservice and it only need to be called once for each microservice \
**request url:** /register \
**request type:** POST \
**request body:**
| name | type |
| :-----------: | :-------------:| 
| identifier       |   string      | 

## log
**description:** This url logs corresponding timestamp and data into the storage for that microservice. This step is only legal after the corresponding microservice is registered \
**request url:** /log \
**request type:** POST \
**request body:**
| name | type |
| :-----------: | :-------------:| 
| identifier       |   string      | 
| timestamp       |   int      | 
| data       |   JSON      | 

## allocate
**description:** This url estimate the demands for each microservice based on the logged data \
**request url:** /allocate \
**request type:** GET \
**request return:**
| name | type |
| :-----------: | :-------------:| 
| demands       |   list      |
