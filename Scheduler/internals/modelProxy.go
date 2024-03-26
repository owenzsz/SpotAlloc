package scheduler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

var (
	defaultPort = "3000"
)

type ModelProxy struct {
	endPointURL string
}

type DemandResponse struct {
	Demands []float64 `json:"demands"`
}

func NewModelProxy(baseURL string) *ModelProxy {
	return &ModelProxy{
		endPointURL: fmt.Sprintf("http://%s:%s", baseURL, defaultPort),
	}
}

func (mp *ModelProxy) RegisterService(serviceID string) error {
	url := fmt.Sprintf("%s/register", mp.endPointURL)
	// fmt.Println(url)
	requestBody, err := json.Marshal(map[string]interface{}{
		"identifier": serviceID,
	})
	// fmt.Println("RequestBody:", string(requestBody))

	if err != nil {
		return fmt.Errorf("error marshaling request body: %v", err)
	}

	resp, err := http.Post(url, "application/json", bytes.NewReader(requestBody))
	if err != nil {
		return fmt.Errorf("error creating request: %v", err)
	}
	defer resp.Body.Close()

	// body, _ := io.ReadAll(resp.Body)
	// fmt.Println("Response Status:", resp.StatusCode)
	// fmt.Println("Response Body:", string(body))
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	return nil
}

func (mp *ModelProxy) UpdateService(serviceID string, timestamp int64, inputData map[string]interface{}) error {
	url := fmt.Sprintf("%s/log", mp.endPointURL)
	requestMap := map[string]interface{}{
		"identifier": serviceID,
		"timestamp":  1,
		"data":       inputData,
	}
	// fmt.Printf("RequestMap: %v\n", requestMap)
	requestBody, err := json.Marshal(requestMap)
	if err != nil {
		return fmt.Errorf("error marshaling request body: %v", err)
	}

	resp, err := http.Post(url, "application/json", bytes.NewReader(requestBody))
	if err != nil {
		return fmt.Errorf("error creating request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	return nil
}

func (mp *ModelProxy) PredictDemand() ([]float64, error) {
	url := fmt.Sprintf("%s/allocate", mp.endPointURL)
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %v", err)
	}

	var demands DemandResponse
	err = json.Unmarshal(body, &demands)
	// fmt.Println("Demands:", demands)
	if err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %v", err)
	}

	return demands.Demands, nil
}
