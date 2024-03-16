package scheduler

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
