package scheduler

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
)

type ServiceSLOPair struct {
	ServiceName string
	SLO         int64
}

func sumDonatedSlices(donatedSlices map[string]float64) float64 {
	sum := 0.0
	for _, slices := range donatedSlices {
		sum += slices
	}
	return sum
}

func removeFromSlice(slice []string, item string) []string {
	for i, v := range slice {
		if v == item {
			return append(slice[:i], slice[i+1:]...)
		}
	}
	return slice
}

func ConvertMapToStringInterface[T any](inputMap map[string]T) map[string]interface{} {
	result := make(map[string]interface{})
	for key, value := range inputMap {
		result[key] = value
	}
	return result
}

func ReadSLOFromJSON() (map[string]int64, error) {
	SLOMap := make(map[string]int64)
	data, err := os.ReadFile("SLO.json")
	if err != nil {
		fmt.Println("Error reading SLO file:", err)
		return nil, err
	}
	var services []ServiceSLOPair
	err = json.Unmarshal(data, &services)
	if err != nil {
		fmt.Println("Error unmarshalling SLO file:", err)
		return nil, err
	}
	for _, pair := range services {
		SLOMap[pair.ServiceName] = pair.SLO
	}
	return SLOMap, nil
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

func findMaxFloat(m map[string]float64) (string, float64) {
	maxKey := ""
	maxValue := 0.0
	for key, value := range m {
		if value > maxValue {
			maxValue = value
			maxKey = key
		}
	}
	return maxKey, maxValue
}
