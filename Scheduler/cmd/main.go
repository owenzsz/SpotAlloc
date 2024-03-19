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
	alpha := 0.1
	f := 1.0
	resourceScheduler := scheduler.NewResourceScheduler(alpha, f)

	// Run the scheduling loop every 2 minutes
	ticker := time.NewTicker(2 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		log.Println("Fetching services from Kubernetes cluster...")
		services, err := kubernetesClient.GetServices()
		if err != nil {
			log.Printf("Failed to fetch services: %v", err)
			continue
		}

		log.Println("Adding services to resource scheduler...")
		for _, service := range services {
			// fmt.Printf("Adding service %s with ID %s and initial credits %f\n", service.Name, service.ID, service.Credits)
			resourceScheduler.AddService(service.ID, service.Name, service.Credits)
		}

		log.Println("Updating resource utilization...")
		err = kubernetesClient.UpdateResourceUtilization(resourceScheduler)
		if err != nil {
			log.Printf("Failed to update resource utilization: %v", err)
			continue
		}

		log.Println("Running resource scheduler...")
		resourceScheduler.Schedule()

		log.Println("Updating resource limits...")
		err = kubernetesClient.UpdateResourceRequestsAndLimits(resourceScheduler)
		if err != nil {
			log.Printf("Failed to update resource limits: %v", err)
			continue
		}

		log.Println("Resource scheduling completed.")
	}
}
