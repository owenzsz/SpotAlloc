package scheduler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

var (
	defaultPort = "8080"
)

type ModelProxy struct {
	endPointURL string
}

func NewModelProxy(baseURL string) *ModelProxy {
	return &ModelProxy{
		endPointURL: fmt.Sprintf("http://%s:%s", baseURL, defaultPort),
	}
}

func (mp *ModelProxy) AddService(serviceID string) error {
	url := fmt.Sprintf("%s/services/%s", mp.endPointURL, serviceID)
	req, err := http.NewRequest("POST", url, nil)
	if err != nil {
		return fmt.Errorf("error creating request: %v", err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("error sending request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	return nil
}

func (mp *ModelProxy) UpdateService(serviceID string, inputData map[string]interface{}) error {
	url := fmt.Sprintf("%s/services/%s", mp.endPointURL, serviceID)
	jsonData, err := json.Marshal(inputData)
	if err != nil {
		return fmt.Errorf("error marshaling input data: %v", err)
	}

	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("error creating request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("error sending request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	return nil
}

func (mp *ModelProxy) Predict(serviceID string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/services/%s/predict", mp.endPointURL, serviceID)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %v", err)
	}

	resp, err := http.DefaultClient.Do(req)
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

	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %v", err)
	}

	return result, nil
}
