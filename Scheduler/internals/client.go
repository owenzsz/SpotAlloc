package scheduler

import (
	"context"
	"fmt"

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

func (kc *KubernetesClient) UpdateServices(resourceScheduler *ResourceScheduler) error {
	serviceList, err := kc.clientset.CoreV1().Services(defaultNameSpace).List(context.Background(), metav1.ListOptions{})
	if err != nil {
		return fmt.Errorf("failed to list services: %v", err)
	}
	fmt.Println("Adding services to resource scheduler...")
	for _, service := range serviceList.Items {
		if service.Name == "kubernetes" {
			continue // Skip the default "kubernetes" service
		}
		if _, ok := resourceScheduler.Services[string(service.UID)]; ok {
			continue // Skip the services that are already added
		}
		resourceScheduler.AddService(string(service.UID), service.Name, 100)
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
