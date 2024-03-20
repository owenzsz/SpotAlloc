package scheduler

import (
	"context"
	"fmt"
	"time"

	"github.com/montanaflynn/stats"
	"github.com/prometheus/client_golang/api"
	prometheusv1 "github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/common/model"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/metrics/pkg/client/clientset/versioned"
)

var (
	defaultNameSpace = "default"
)

type KubernetesClient struct {
	clientset     *kubernetes.Clientset
	metricsClient *versioned.Clientset
}

func NewKubernetesClient() (*KubernetesClient, error) {
	config, err := clientcmd.BuildConfigFromFlags("", "kubeconfig")
	if err != nil {
		return nil, fmt.Errorf("failed to load kubeconfig: %v", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create Kubernetes clientset: %v", err)
	}

	metricsClient, err := versioned.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create Kubernetes metrics clientset: %v", err)
	}

	return &KubernetesClient{
		clientset:     clientset,
		metricsClient: metricsClient,
	}, nil
}

func (kc *KubernetesClient) AddServicesIfNeeded(resourceScheduler *ResourceScheduler) error {
	serviceList, err := kc.clientset.CoreV1().Services(defaultNameSpace).List(context.Background(), metav1.ListOptions{})
	if err != nil {
		return fmt.Errorf("failed to list services: %v", err)
	}
	fmt.Println("Adding services to resource scheduler...")
	for _, service := range serviceList.Items {
		if service.Name == "kubernetes" || service.Name == "prometheus" {
			continue // Skip the default "kubernetes" and the "prometheus" service
		}
		if _, ok := resourceScheduler.Services[string(service.UID)]; ok {
			continue // Skip the services that are already added
		}
		resourceScheduler.AddService(string(service.UID), service.Name, 100)
	}

	return nil
}

func (kc *KubernetesClient) UpdateServiceLatency(resourceScheduler *ResourceScheduler) error {
	services := resourceScheduler.GetAllServices()
	for _, service := range services {
		latency, err := kc.GetServiceLatency(service.Name, 90, 2)
		if err != nil {
			return fmt.Errorf("failed to get latency for service %s when updating the latency value: %v", service.Name, err)
		}
		resourceScheduler.UpdateServiceLatency(service.ID, latency)
	}
	return nil
}

func (kc *KubernetesClient) UpdateResourceUtilization(resourceScheduler *ResourceScheduler) error {
	services := resourceScheduler.GetAllServices()

	for _, service := range services {
		podMetrics, err := kc.metricsClient.MetricsV1beta1().PodMetricses(defaultNameSpace).List(context.Background(), metav1.ListOptions{
			LabelSelector: fmt.Sprintf("app=%s", service.Name),
		})
		if err != nil {
			return fmt.Errorf("failed to get pod metrics for service %s: %v", service.Name, err)
		}

		var totalCPUUtilization int64
		for _, podMetric := range podMetrics.Items {
			for _, container := range podMetric.Containers {
				totalCPUUtilization += container.Usage.Cpu().MilliValue()
			}
		}

		resourceScheduler.UpdateServiceUsage(service.ID, float64(totalCPUUtilization))
	}

	return nil
}

func (kc *KubernetesClient) UpdateResourceRequestsAndLimits(resourceScheduler *ResourceScheduler) error {
	services := resourceScheduler.GetAllServices()

	for _, service := range services {
		deploymentName := service.Name
		deployment, err := kc.clientset.AppsV1().Deployments(defaultNameSpace).Get(context.Background(), deploymentName, metav1.GetOptions{})
		if err != nil {
			return fmt.Errorf("failed to get deployment for service %s: %v", service.Name, err)
		}

		deployment.Spec.Template.Spec.Containers[0].Resources.Limits = corev1.ResourceList{
			corev1.ResourceCPU: resource.MustParse(fmt.Sprintf("%dm", int64(service.ResourceLimit))),
		}

		deployment.Spec.Template.Spec.Containers[0].Resources.Requests = corev1.ResourceList{
			corev1.ResourceCPU: resource.MustParse(fmt.Sprintf("%dm", int64(service.ResourceRequested))),
		}

		_, err = kc.clientset.AppsV1().Deployments(defaultNameSpace).Update(context.Background(), deployment, metav1.UpdateOptions{})
		if err != nil {
			return fmt.Errorf("failed to update deployment for service %s: %v", service.Name, err)
		}
	}

	return nil
}

func (kc *KubernetesClient) GetTotalAllocableCPUResources() (int64, error) {
	// Get the list of nodes in the cluster
	nodeList, err := kc.clientset.CoreV1().Nodes().List(context.Background(), metav1.ListOptions{})
	if err != nil {
		return 0, fmt.Errorf("failed to list nodes: %v", err)
	}

	var totalCPU, allocatableCPU int64
	for _, node := range nodeList.Items {
		// Get the allocatable CPU for each node
		allocatableCPU = node.Status.Allocatable.Cpu().MilliValue()
		totalCPU += allocatableCPU
	}

	// // Get the list of pods
	// podList, err := kc.clientset.CoreV1().Pods(defaultNameSpace).List(context.Background(), metav1.ListOptions{})
	// if err != nil {
	// 	return 0, fmt.Errorf("failed to list pods in namespace %s: %v", defaultNameSpace, err)
	// }

	// var usedCPU int64
	// for _, pod := range podList.Items {
	// 	for _, container := range pod.Spec.Containers {
	// 		// Get the CPU requests for each container
	// 		cpuRequest := container.Resources.Requests.Cpu().MilliValue()
	// 		usedCPU += cpuRequest
	// 	}
	// }

	// availableCPU := totalCPU - usedCPU
	return allocatableCPU, nil
}

func (kc *KubernetesClient) GetServiceLatency(serviceName string, quantile int64, pastDuration int64) (float64, error) {
	// Create a new Prometheus API client
	prometheusClientAddress, err := kc.getPrometheusClientAddress()
	if err != nil {
		return 0, fmt.Errorf("failed to get Prometheus client IP address: %v", err)
	}
	client, err := api.NewClient(api.Config{
		Address: prometheusClientAddress,
	})
	if err != nil {
		return 0, fmt.Errorf("failed to create Prometheus client: %v", err)
	}

	// Create a new Prometheus query API client
	queryAPI := prometheusv1.NewAPI(client)

	// Specify the Prometheus query to retrieve the latency metrics for the service
	query := fmt.Sprintf(`request_latency_milliseconds{service="%s"}[%dm])`, serviceName, pastDuration)
	end := time.Now()
	start := end.Add(time.Duration(-pastDuration) * time.Minute)

	// Execute the Prometheus query
	result, warn, err := queryAPI.QueryRange(context.Background(), query, prometheusv1.Range{
		Start: start,
		End:   end,
		Step:  time.Second,
	})
	if err != nil {
		return 0, fmt.Errorf("failed to execute Prometheus query: %v", err)
	}
	if len(warn) > 0 {
		fmt.Printf("Warnings: %v\n", warn)
	}

	// Extract the latency value from the query result
	matrix, ok := result.(model.Matrix)
	if !ok {
		return 0, fmt.Errorf("query did not return a matrix")
	}

	values := make([]float64, 0)
	for _, stream := range matrix {
		// fmt.Printf("Metric: %s\n", stream.Metric)
		for _, value := range stream.Values {
			// fmt.Printf("  At %s, value: %f\n", value.Timestamp.Time(), float64(value.Value))
			values = append(values, float64(value.Value))
		}
	}

	latencyQuantile, err := stats.Percentile(values, 90.0)
	if err != nil {
		return 0, fmt.Errorf("failed to calculate 90th percentile: %v", err)
	}
	return latencyQuantile, nil
}

func (kc *KubernetesClient) getPrometheusClientAddress() (string, error) {
	// Get the list of pods
	prometheusService, err := kc.clientset.CoreV1().Services(defaultNameSpace).Get(context.TODO(), "prometheus", metav1.GetOptions{})
	if err != nil {
		return "", fmt.Errorf("failed to get prometheus service: %v", err)
	}
	if len(prometheusService.Status.LoadBalancer.Ingress) > 0 {
		externalIP := prometheusService.Status.LoadBalancer.Ingress[0].IP
		prometheusAddress := fmt.Sprintf("http://%s:9090", externalIP)
		return prometheusAddress, nil
	} else {
		return "", fmt.Errorf("failed to get prometheus service external IP")
	}
}
