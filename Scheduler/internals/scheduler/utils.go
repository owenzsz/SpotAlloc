package scheduler

import "math"

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
