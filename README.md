# SpotAlloc
This is the Project Repository for SpotAlloc, a resource Allocation system for a cluster of spot instances. 

## Project Structure
The project directory contains {x} main directories: `Configs`, `my-microservice`, and `Scheduler`. In this section, we will discuss the contents and the function of each directory.

### Configs
This directory contains the configuration files for the cluster and the microservices. The `eks` directory contains the configuration files for the AWS EKS cluster. The `kube` directory contains the configuration files for the microservices.

### my-microservice
This is a very simple sample microservice for the purpose of experimentation. It hosts a single-page website that returns a simple html file. You can replace this microservice with your own microservice.

### Scheduler
This is the directory that contains the code for the actual scheduler. You can check the it and its subdirectories for more implementation details.

## Project Setup
This section will guide you through the process of setting up the cluster and run the project. 

1. Create a cluster of spot instances on AWS.
    ```
    cd to /Configs/eks
    eksctl create cluster -f cluster.yaml
    ```
    The default cluster size of the is 3 m5.large nodes. You can change the size and other configurations by modifying the `cluster.yaml` file.

2. Deploy the sample microservice to the cluster.
    ```
    cd to /Configs/kube
    for i in {1..5}; do
        cat deployment-template.yaml | sed "s/{{SERVICE_NUMBER}}/$i/g" | kubectl apply -f -
        cat service-template.yaml | sed "s/{{SERVICE_NUMBER}}/$i/g" | kubectl apply -f -
    done
    ```
    You can replace the entire microservice with your own service. The `deployment-template.yaml` and `service-template.yaml` files are the templates for the deployment and service of the microservice. You should change the image name to your own image name in both files to change the microservice.

    In the for loop, you can change the number of microservices you want to deploy by changing the range of the loop.

3. Check the status of the microservices.
    ```
    kubectl get pods
    kubectl get services
    ```
    You should see the status of the microservices and the pods if you set up the cluster and your microservice correctly.

4. Deploy the metrics server
    ```
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    kubectl get deployment metrics-server -n kube-system
    ```
    You should see the metrics server deployment running.

5. Run the Scheduler
    ```
    cd to /Scheduler
    go run cmd/main.go
    ```
    The scheduler will start running and you should see the logs of the scheduler.