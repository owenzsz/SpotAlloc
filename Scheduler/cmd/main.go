package main

import (
	"log"
	"time"

	scheduler "github.com/owenzsz/SpotAllocScheduler/internals"
)

func main() {
	// Create a new Kubernetes client

	kubernetesClient, err := scheduler.NewKubernetesClient() // Use the fully qualified package name to call the NewKubernetesClient function
	if err != nil {
		log.Fatalf("Failed to create Kubernetes client: %v", err)
	}

	// Create a new resource scheduler with the desired parameters
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
