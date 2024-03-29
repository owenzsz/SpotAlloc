package scheduler

import (
	"context"
	"fmt"
	"math"
	"time"

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

func (kc *KubernetesClient) AddServicesIfNeeded(resourceScheduler *ResourceScheduler, SLOMap map[string]int64) error {
	serviceList, err := kc.clientset.CoreV1().Services(defaultNameSpace).List(context.Background(), metav1.ListOptions{})
	if err != nil {
		return fmt.Errorf("failed to list services: %v", err)
	}
	fmt.Println("Adding services to resource scheduler...")
	for _, service := range serviceList.Items {
		if service.Name == "kubernetes" || service.Name == "prometheus" {
			continue // Skip the default "kubernetes" and the "prometheus" service
		}
		if _, ok := resourceScheduler.Services[service.Name]; ok {
			continue // Skip the services that are already added
		}
		if _, ok := SLOMap[service.Name]; !ok {
			continue // Skip the services that are not in the SLO map
		}
		resourceScheduler.AddService(service.Name, service.Name, 100, SLOMap[service.Name])
	}

	return nil
}

func (kc *KubernetesClient) UpdateServicePerformanceMetrics(resourceScheduler *ResourceScheduler) error {
	services := resourceScheduler.GetAllServices()
	for _, service := range services {
		latency, QPS, err := kc.GetServicePerformanceMetrics(service.Name, 0.95, 2)
		if err != nil {
			return fmt.Errorf("failed to get performance metrics for service %s when updating the metrics: %v", service.Name, err)
		}
		if math.IsNaN(latency) {
			latency = 0
		}
		if math.IsNaN(QPS) {
			QPS = 0
		}
		// fmt.Printf("Service: %s, Latency: %f, QPS: %f\n", service.Name, latency, QPS)
		resourceScheduler.UpdateServiceLatency(service.ID, latency)
		resourceScheduler.UpdateServiceQPS(service.ID, QPS)
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
		resourceScheduler.UpdateServiceUsage(service.ID, totalCPUUtilization)
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
			corev1.ResourceCPU: resource.MustParse(fmt.Sprintf("%dm", service.ResourceLimit)),
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

func (kc *KubernetesClient) GetServicePerformanceMetrics(serviceName string, latencyQuantile float64, pastDuration int64) (float64, float64, error) {
	prometheusClientAddress, err := kc.getPrometheusClientAddress()
	if err != nil {
		return 0, 0, fmt.Errorf("failed to get Prometheus client IP address: %v", err)
	}
	client, err := api.NewClient(api.Config{
		Address: prometheusClientAddress,
	})
	if err != nil {
		return 0, 0, fmt.Errorf("failed to create Prometheus client: %v", err)
	}

	// Create a new Prometheus query API client
	queryAPI := prometheusv1.NewAPI(client)
	latency, err := kc.GetServiceLatency(queryAPI, serviceName, latencyQuantile, pastDuration)
	if err != nil {
		return 0, 0, fmt.Errorf("failed to get latency for service %s: %v", serviceName, err)
	}
	QPS, err := kc.GetServiceQPS(queryAPI, serviceName, pastDuration)
	fmt.Printf("Service: %s, Latency: %f, QPS: %f\n", serviceName, latency, QPS)
	if err != nil {
		return 0, 0, fmt.Errorf("failed to get QPS for service %s: %v", serviceName, err)
	}
	return latency, QPS, nil

}

func (kc *KubernetesClient) GetServiceLatency(queryAPI prometheusv1.API, serviceName string, quantile float64, pastDuration int64) (float64, error) {
	// Specify the Prometheus query to retrieve the latency metrics for the service
	query := fmt.Sprintf(`histogram_quantile(%f, rate(request_latency_seconds_bucket{service="%s"}[%dm]))`, quantile, serviceName, pastDuration)

	// Execute the Prometheus query
	result, warn, err := queryAPI.Query(context.Background(), query, time.Now())
	if err != nil {
		return 0, fmt.Errorf("failed to execute Prometheus query: %v", err)
	}
	if len(warn) > 0 {
		fmt.Printf("Warnings: %v\n", warn)
	}

	// Extract the latency value from the query result
	var latency float64
	vector, ok := result.(model.Vector)
	if !ok {
		return 0, fmt.Errorf("query did not return a matrix")
	}

	for _, sample := range vector {
		latency = float64(sample.Value)
		break
	}
	return latency, nil
}

func (kc *KubernetesClient) GetServiceQPS(queryAPI prometheusv1.API, serviceName string, pastDuration int64) (float64, error) {
	query := fmt.Sprintf(`rate(request_count_total{service="%s"}[%dm])`, serviceName, pastDuration)

	// Execute the Prometheus query
	result, warn, err := queryAPI.Query(context.Background(), query, time.Now())
	if err != nil {
		return 0, fmt.Errorf("failed to execute Prometheus query: %v", err)
	}
	if len(warn) > 0 {
		fmt.Printf("Warnings: %v\n", warn)
	}

	// Extract the QPS value from the query result
	var QPS float64
	vector, ok := result.(model.Vector)
	if !ok {
		return 0, fmt.Errorf("query did not return a matrix")
	}

	for _, sample := range vector {
		QPS = float64(sample.Value)
		break
	}
	return QPS, nil

}

func (kc *KubernetesClient) getPrometheusClientAddress() (string, error) {
	// Get the list of pods
	prometheusService, err := kc.clientset.CoreV1().Services(defaultNameSpace).Get(context.TODO(), "prometheus", metav1.GetOptions{})
	if err != nil {
		return "", fmt.Errorf("failed to get prometheus service: %v", err)
	}
	if len(prometheusService.Status.LoadBalancer.Ingress) > 0 {
		externalHostname := prometheusService.Status.LoadBalancer.Ingress[0].Hostname
		prometheusAddress := fmt.Sprintf("http://%s:9090", externalHostname)
		// fmt.Println("Prometheus address: ", prometheusAddress)
		return prometheusAddress, nil
	} else {
		return "", fmt.Errorf("failed to get prometheus service external IP")
	}
}
