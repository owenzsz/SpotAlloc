#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Get all services across all namespaces
echo "Retrieving all services..."
services=$(kubectl get svc --all-namespaces -o json)

# Loop through services and delete those with an external IP
echo "Deleting services with an associated EXTERNAL-IP..."
echo "$services" | jq -r '.items[] | select(.status.loadBalancer.ingress != null) | .metadata.name + " " + .metadata.namespace' | while read svc ns; do
  kubectl delete svc "$svc" -n "$ns"
  echo "Deleted service $svc in namespace $ns."
done

# Delete the EKS cluster
echo "Deleting EKS cluster..."
eksctl delete cluster --name my-spot-cluster
echo "EKS cluster deleted successfully."

echo "All specified services have been deleted and the cluster has been shut down."
