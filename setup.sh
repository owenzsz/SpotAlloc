#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the base directory as the directory where the script is located
BASEDIR=$(dirname "$0")

# Start EKS cluster
echo "Creating EKS cluster..."
eksctl create cluster -f "$BASEDIR/Configs/eks/cluster.yaml"
echo "EKS cluster created successfully."

# Wait for the cluster to become fully active
echo "Waiting for the cluster nodes to become ready..."
kubectl wait --for=condition=ready nodes --all --timeout=600s
echo "Cluster nodes are ready."

# Configure and deploy services on k8s
for i in {1..5}; do
  echo "Deploying service $i..."
  cat "$BASEDIR/Configs/kube/service/deployment-template.yaml" | sed "s/{{SERVICE_NUMBER}}/$i/g" | kubectl apply -f -
  cat "$BASEDIR/Configs/kube/service/service-template.yaml" | sed "s/{{SERVICE_NUMBER}}/$i/g" | kubectl apply -f -
  echo "Service $i deployed successfully."
done

# Deploy metrics server
echo "Deploying metrics server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
echo "Metrics server deployed successfully."

# Setup Prometheus
echo "Setting up Prometheus..."
kubectl create configmap prometheus-config --from-file="$BASEDIR/Configs/kube/prometheus/prometheus.yaml" || true # ignore if configmap already exists
kubectl apply -f "$BASEDIR/Configs/kube/prometheus/prometheus-deployment.yaml"
kubectl apply -f "$BASEDIR/Configs/kube/prometheus/prometheus-service.yaml"
kubectl apply -f "$BASEDIR/Configs/kube/prometheus/prometheus-serviceaccount.yaml"
kubectl apply -f "$BASEDIR/Configs/kube/prometheus/prometheus-clusterrole.yaml"
kubectl apply -f "$BASEDIR/Configs/kube/prometheus/prometheus-clusterrolebinding.yaml"
echo "Prometheus set up successfully."

echo "All services have been deployed!"
