# Usage of Demand Estimator
## register
**request url:** /register \
**request type:** POST \
**request body:**
| name | type |
| :-----------: | :-------------:| 
| identifier       |   string      | 

## log
**request url:** /log \
**request type:** POST \
**request body:**
| name | type |
| :-----------: | :-------------:| 
| identifier       |   string      | 
| timestamp       |   int      | 
| data       |   JSON      | 

## allocate
**request url:** /allocate \
**request type:** GET \
**request return:**
| name | type |
| :-----------: | :-------------:| 
| demands       |   list      |
