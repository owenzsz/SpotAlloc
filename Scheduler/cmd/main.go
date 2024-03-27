package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"

	scheduler "github.com/owenzsz/SpotAllocScheduler/internals"
)

func main() {

	//check if the kubeconfig file exists
	if _, err := os.Stat("kubeconfigr"); err == nil {
		os.Remove("kubeconfig")
	}
	//create a new kubeconfig file
	kubeconfig, err := os.Create("kubeconfig")
	if err != nil {
		fmt.Printf("Failed to create kubeconfig file: %v\n", err)
		return
	}
	defer kubeconfig.Close()

	// Run the kubectl command and redirect the output to the kubeconfig file
	cmd := exec.Command("kubectl", "config", "view", "--raw")
	cmd.Stdout = kubeconfig
	err = cmd.Run()
	if err != nil {
		fmt.Printf("Failed to run kubectl command: %v\n", err)
		return
	}

	fmt.Println("Kubeconfig file generated successfully.")

	// Create a new Kubernetes client
	kubernetesClient, err := scheduler.NewKubernetesClient()
	if err != nil {
		log.Fatalf("Failed to create Kubernetes client: %v", err)
	}

	// Create a new resource scheduler with the configurable parameters
	allocableResources, err := kubernetesClient.GetTotalAllocableCPUResources()
	if err != nil {
		fmt.Printf("Failed to get total allocable CPU resources: %v", err)
	}
	alpha := 0.1
	resourceScheduler := scheduler.NewResourceScheduler(alpha, allocableResources)

	// Run the scheduling loop every 2 minutes
	ticker := time.NewTicker(2 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		fmt.Println("Fetching services from Kubernetes cluster...")
		err := kubernetesClient.AddServicesIfNeeded(resourceScheduler)
		if err != nil {
			fmt.Printf("Failed to update services: %v \n", err)
			continue
		}

		err = kubernetesClient.UpdateServicePerformanceMetrics(resourceScheduler)
		if err != nil {
			fmt.Printf("Failed to update performance metrics: %v \n", err)
			continue
		}

		fmt.Println("Updating resource utilization...")
		err = kubernetesClient.UpdateResourceUtilization(resourceScheduler)
		if err != nil {
			fmt.Printf("Failed to update resource utilization: %v \n", err)
			continue
		}

		err = resourceScheduler.LogServiceMetricsToModelProxy()
		if err != nil {
			fmt.Printf("Failed to log service metrics to model proxy: %v \n", err)
		}

		fmt.Println("Running resource scheduler...")
		err = resourceScheduler.Schedule(scheduler.CreditAlgorithm)
		if err != nil {
			fmt.Printf("Failed to run resource scheduler: %v \n", err)
			continue
		}

		fmt.Println("Updating resource limits...")
		err = kubernetesClient.UpdateResourceRequestsAndLimits(resourceScheduler)
		if err != nil {
			fmt.Printf("Failed to update resource limits: %v \n", err)
			continue
		}

		fmt.Println("Resource scheduling completed.")
	}
}
