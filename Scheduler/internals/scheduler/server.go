package scheduler

import (
	"fmt"
	"math"
	"sort"
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
	modelProxy              *ModelProxy
}

type DemandPair struct {
	ServiceID string
	Demand    float64
}

func NewResourceScheduler(alpha float64, allocableResources int64) *ResourceScheduler {
	return &ResourceScheduler{
		Services:                make(map[string]*Service),
		Alpha:                   alpha,
		TotalAllocableResources: int64(allocableResources),
		modelProxy:              NewModelProxy("localhost"),
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
	err := rs.modelProxy.RegisterService(id)
	if err != nil {
		fmt.Printf("Failed to register service to model proxy: %v\n", err)
	}
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

func (rs *ResourceScheduler) LogServiceMetricsToModelProxy() error {
	rs.Lock()
	defer rs.Unlock()

	for id, service := range rs.Services {
		err := rs.modelProxy.UpdateService(id, 1, map[string]interface{}{
			"performance": service.Latency,
			"load":        service.QPS,
			"resource":    service.ResourceUtilized,
		})
		if err != nil {
			return fmt.Errorf("failed to log service metrics to model proxy: %v", err)
		}
	}

	return nil
}

func (rs *ResourceScheduler) Schedule(algorithmName string) error {
	var err error
	if algorithmName == "credit" {
		err = rs.CreditBasedSchedule()
	} else if algorithmName == "fair" {
		err = rs.FairSchedule()
	} else if algorithmName == "maxmin" {
		err = rs.MaxMinSchedule()
	} else {
		err = fmt.Errorf("unknown scheduling algorithm: %s", algorithmName)
	}
	return err
}

func (rs *ResourceScheduler) CreditBasedSchedule() error {
	rs.Lock()
	defer rs.Unlock()

	demand := make(map[string]float64)
	demandList, err := rs.modelProxy.PredictDemand()
	if err != nil || demandList == nil {
		return fmt.Errorf("error predicting demand: %v", err)
	}

	index := 0
	for id := range rs.Services {
		demand[id] = demandList[index]
		index++
	}
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
	return nil
}

func (rs *ResourceScheduler) FairSchedule() error {
	rs.Lock()
	defer rs.Unlock()

	fairShare := float64(rs.TotalAllocableResources / int64(len(rs.Services)))
	for _, service := range rs.Services {
		service.ResourceLimit = fairShare
	}
	return nil
}

func (rs *ResourceScheduler) MaxMinSchedule() error {
	demands := make([]*DemandPair, 0)
	demandList, err := rs.modelProxy.PredictDemand()
	if err != nil || demandList == nil {
		return fmt.Errorf("error predicting demand: %v", err)
	}
	index := 0
	for id := range rs.Services {
		newPair := DemandPair{
			ServiceID: id,
			Demand:    demandList[index],
		}
		demands = append(demands, &newPair)
		index++
	}

	n := len(demands)
	sort.Slice(demands, func(i, j int) bool {
		return demands[i].Demand < demands[j].Demand
	})
	allocation := make(map[string]float64)
	capacity := float64(rs.TotalAllocableResources)

	var allocatedSum float64
	var remainingServicesToAllocation int

	for i := 0; i < n; i++ {
		remainingServicesToAllocation = n - i
		// Calculate the tentative equal share for the remaining sources
		equalShare := (capacity - allocatedSum) / float64(remainingServicesToAllocation)

		if demands[i].Demand <= equalShare {
			// If the source's demand is less than or equal to the equal share,
			// allocate the demanded amount to the source
			allocation[demands[i].ServiceID] = demands[i].Demand
			allocatedSum += demands[i].Demand
		} else {
			// If the source's demand is greater than the equal share,
			// allocate the equal share to the source and distribute the remaining
			// resources among the remaining sources
			for j := i; j < n; j++ {
				otherDemand := demands[j]
				allocation[otherDemand.ServiceID] = equalShare
			}
			break
		}
		for serviceID, resourceAllocation := range allocation {
			rs.Services[serviceID].ResourceLimit = resourceAllocation
		}
	}

	return nil

}
