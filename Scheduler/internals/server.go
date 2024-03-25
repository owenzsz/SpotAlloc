package scheduler

import (
	"fmt"
	"math"
	"sync"
)

type Service struct {
	ID                string
	Name              string
	Credits           float64
	ResourceUtilized  float64
	ResourceRequested float64
	ResourceLimit     float64
	Latency           float64
	QPS               float64
}

type ResourceScheduler struct {
	sync.Mutex
	Services                map[string]*Service
	Alpha                   float64
	TotalAllocableResources int64
}

func NewResourceScheduler(alpha float64, allocableResources int64) *ResourceScheduler {
	return &ResourceScheduler{
		Services:                make(map[string]*Service),
		Alpha:                   alpha,
		TotalAllocableResources: int64(allocableResources),
	}
}

func (rs *ResourceScheduler) AddService(id, name string, initialCredits float64) {
	rs.Lock()
	defer rs.Unlock()

	service := &Service{
		ID:      id,
		Name:    name,
		Credits: initialCredits,
	}
	rs.Services[id] = service
}

func (rs *ResourceScheduler) UpdateServiceUsage(id string, resourceUtilized float64) {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return
	}

	service.ResourceUtilized = resourceUtilized
}

func (rs *ResourceScheduler) UpdateServiceCredits(id string, credits float64) {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return
	}

	service.Credits = credits
}

func (rs *ResourceScheduler) UpdateServiceLimit(id string, limit float64) {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return
	}

	service.ResourceLimit = limit
}

func (rs *ResourceScheduler) UpdateServiceRequest(id string, request float64) {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return
	}

	service.ResourceRequested = request
}

func (rs *ResourceScheduler) UpdateServiceLatency(id string, latency float64) {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return
	}

	service.Latency = latency
}

func (rs *ResourceScheduler) UpdateServiceQPS(id string, QPS float64) {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return
	}

	service.QPS = QPS
}

func (rs *ResourceScheduler) GetServiceCredits(id string) float64 {
	rs.Lock()
	defer rs.Unlock()

	service, ok := rs.Services[id]
	if !ok {
		fmt.Printf("Service with id %s does not exist\n", id)
		return 0
	}

	return service.Credits
}

func (rs *ResourceScheduler) GetAllServices() []*Service {
	rs.Lock()
	defer rs.Unlock()

	services := make([]*Service, 0, len(rs.Services))
	for _, service := range rs.Services {
		services = append(services, service)
	}

	return services
}

func (rs *ResourceScheduler) Schedule() {
	rs.Lock()
	defer rs.Unlock()

	demand := make(map[string]float64)
	mp := NewModelProxy("http://localhost")
	// Predict the demand for each service
	var wg sync.WaitGroup
	for id := range rs.Services {
		wg.Add(1)
		go func(serviceID string) {
			defer wg.Done()
			response, err := mp.Predict(serviceID)
			if err != nil {
				fmt.Printf("error predicting demand for service %s: %v\n", serviceID, err)
				return
			}
			currDemand, ok := response["demand"].(float64)
			if !ok {
				fmt.Printf("invalid demand value for service %s\n", serviceID)
				return
			}
			rs.Lock()
			demand[serviceID] = currDemand
			rs.Unlock()
		}(id)
	}
	wg.Wait()
	fairShare := float64(rs.TotalAllocableResources / int64(len(rs.Services)))
	sharedSlices := float64(len(rs.Services)) * (1 - rs.Alpha) * fairShare
	donatedSlices := make(map[string]float64)
	alloc := make(map[string]float64)

	for id := range rs.Services {
		donatedSlices[id] = math.Max(0, rs.Alpha*fairShare-demand[id])
		alloc[id] = math.Min(demand[id], rs.Alpha*fairShare)
		rs.Services[id].Credits += (1 - rs.Alpha) * fairShare
	}

	donors := make([]string, 0)
	for serviceID, slices := range donatedSlices {
		if slices > 0 {
			donors = append(donors, serviceID)
		}
	}

	borrowers := make([]string, 0)
	for serviceID, allocated := range alloc {
		if allocated < demand[serviceID] && rs.Services[serviceID].Credits > 0 {
			borrowers = append(borrowers, serviceID)
		}
	}

	for len(borrowers) > 0 && (sumDonatedSlices(donatedSlices) > 0 || sharedSlices > 0) {
		// Find the borrower with maximum credits
		selectedBorrower := selectBorrowerWithMaxCredits(rs.Services, borrowers)

		borrowerRequiredAmount := math.Max(0, demand[selectedBorrower]-alloc[selectedBorrower]) //unit: milliCPU, 1000 milliCPU = 1 CPU
		borrowerGainedAmount := borrowerRequiredAmount
		if len(donors) > 0 {
			// Find the donor with minimum credits
			selectedDonor := selectDonorWithMinCredits(rs.Services, donors)
			borrowerGainedAmount = math.Min(borrowerRequiredAmount, donatedSlices[selectedDonor])
			rs.Services[selectedDonor].Credits += borrowerGainedAmount
			donatedSlices[selectedDonor] -= borrowerGainedAmount
			// Update the set of donors
			if donatedSlices[selectedDonor] == 0 {
				donors = removeFromSlice(donors, selectedDonor)
			}
		} else {
			sharedSlices -= borrowerGainedAmount
		}

		alloc[selectedBorrower] += borrowerGainedAmount
		rs.Services[selectedBorrower].Credits -= borrowerGainedAmount

		// Update the set of borrowers
		if alloc[selectedBorrower] >= demand[selectedBorrower] || rs.Services[selectedBorrower].Credits == 0 {
			borrowers = removeFromSlice(borrowers, selectedBorrower)
		}
	}

	for serviceID, resourceAllocation := range alloc {
		rs.Services[serviceID].ResourceLimit = resourceAllocation
	}
}

// TODO: implement this with heap for better performance
func selectBorrowerWithMaxCredits(services map[string]*Service, borrowers []string) string {
	maxCredits := float64(-1)
	var selectedBorrower string
	for _, borrower := range borrowers {
		c := services[borrower].Credits
		if c > maxCredits {
			maxCredits = c
			selectedBorrower = borrower
		}
	}
	return selectedBorrower
}

func selectDonorWithMinCredits(services map[string]*Service, donors []string) string {
	minCredits := math.MaxFloat64
	var selectedDonor string
	for _, donor := range donors {
		c := services[donor].Credits
		if c < minCredits {
			minCredits = c
			selectedDonor = donor
		}
	}
	return selectedDonor
}
