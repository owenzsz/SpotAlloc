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
}

type ResourceScheduler struct {
	sync.Mutex
	Services     map[string]*Service
	Alpha        float64
	F            float64
	SharedSlices float64
}

func NewResourceScheduler(alpha, f float64) *ResourceScheduler {
	return &ResourceScheduler{
		Services:     make(map[string]*Service),
		Alpha:        alpha,
		F:            f,
		SharedSlices: 0,
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
	rs.SharedSlices += (1 - rs.Alpha) * rs.F
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
	for id, service := range rs.Services {
		demand[id] = service.ResourceRequested
	}

	donatedSlices := make(map[string]float64)
	alloc := make(map[string]float64)

	for id := range rs.Services {
		donatedSlices[id] = math.Max(0, rs.Alpha*rs.F-demand[id])
		alloc[id] = math.Min(demand[id], rs.Alpha*rs.F)
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

	for len(borrowers) > 0 && (sumDonatedSlices(donatedSlices) > 0 || rs.SharedSlices > 0) {
		// Find the borrower with maximum credits
		selectedBorrower := selectBorrowerWithMaxCredits(rs.Services, borrowers)

		var requiredAmount = 1.0
		if len(donors) > 0 {
			// Find the donor with minimum credits
			selectedDonor := selectDonorWithMinCredits(rs.Services, donors)
			requiredAmount = math.Min(requiredAmount, donatedSlices[selectedDonor])
			// in case the current donor has less than 1 required amount
			rs.Services[selectedDonor].Credits += requiredAmount
			donatedSlices[selectedDonor] -= requiredAmount
			// Update the set of donors
			if donatedSlices[selectedDonor] == 0 {
				donors = removeFromSlice(donors, selectedDonor)
			}
		} else {
			rs.SharedSlices -= requiredAmount
		}

		alloc[selectedBorrower] += requiredAmount
		rs.Services[selectedBorrower].Credits -= requiredAmount

		// Update the set of borrowers
		if alloc[selectedBorrower] == demand[selectedBorrower] || rs.Services[selectedBorrower].Credits == 0 {
			borrowers = removeFromSlice(borrowers, selectedBorrower)
		}
	}

	for serviceID, allocation := range alloc {
		rs.Services[serviceID].ResourceLimit = allocation
	}
}

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
