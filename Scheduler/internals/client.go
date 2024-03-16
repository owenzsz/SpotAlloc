package scheduler

import (
	"context"
	"fmt"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/metrics/pkg/client/clientset/versioned"
)

type KubernetesClient struct {
	clientset     *kubernetes.Clientset
	metricsClient *versioned.Clientset
}

func NewKubernetesClient() (*KubernetesClient, error) {
	config, err := rest.InClusterConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to get in-cluster config: %v", err)
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

func (kc *KubernetesClient) GetServices() ([]Service, error) {
	serviceList, err := kc.clientset.CoreV1().Services(metav1.NamespaceAll).List(context.Background(), metav1.ListOptions{})
	if err != nil {
		return nil, fmt.Errorf("failed to list services: %v", err)
	}

	var services []Service
	for _, svc := range serviceList.Items {
		service := Service{
			ID:      string(svc.UID),
			Name:    svc.Name,
			Credits: 100, // Set the initial credits as needed
		}
		services = append(services, service)
	}

	return services, nil
}

func (kc *KubernetesClient) UpdateResourceUtilization(resourceScheduler *ResourceScheduler) error {
	services := resourceScheduler.GetAllServices()

	for _, service := range services {
		podMetrics, err := kc.metricsClient.MetricsV1beta1().PodMetricses(metav1.NamespaceAll).List(context.Background(), metav1.ListOptions{
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
		deployment, err := kc.clientset.AppsV1().Deployments(metav1.NamespaceAll).Get(context.Background(), service.Name, metav1.GetOptions{})
		if err != nil {
			return fmt.Errorf("failed to get deployment for service %s: %v", service.Name, err)
		}

		deployment.Spec.Template.Spec.Containers[0].Resources.Limits = corev1.ResourceList{
			corev1.ResourceCPU: resource.MustParse(fmt.Sprintf("%dm", int64(service.ResourceLimit))),
		}

		deployment.Spec.Template.Spec.Containers[0].Resources.Requests = corev1.ResourceList{
			corev1.ResourceCPU: resource.MustParse(fmt.Sprintf("%dm", int64(service.ResourceRequested))),
		}

		_, err = kc.clientset.AppsV1().Deployments(deployment.Namespace).Update(context.Background(), deployment, metav1.UpdateOptions{})
		if err != nil {
			return fmt.Errorf("failed to update deployment for service %s: %v", service.Name, err)
		}
	}

	return nil
}
