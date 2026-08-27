package orbc

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

func (c *Client) RunAutomation(id string) (*RunOut, error) {
	var out RunOut
	r, err := c.http.R().SetResult(&out).Post(fmt.Sprintf("/api/v1/automations/%s/run", id))
	if err != nil {
		return nil, fmt.Errorf("failed to run automation %s: %w", id, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to execute run: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

func (c *Client) RetryRun(runID string) (*RunOut, error) {
	var out RunOut
	r, err := c.http.R().SetResult(&out).Post(fmt.Sprintf("/api/v1/runs/%s/retry", runID))
	if err != nil {
		return nil, fmt.Errorf("failed to retry run %s: %w", runID, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to retry run: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

func (c *Client) GetRun(id string) (*RunOut, error) {
	var out RunOut
	r, err := c.http.R().SetResult(&out).Get(fmt.Sprintf("/api/v1/runs/%s", id))
	if err != nil {
		return nil, fmt.Errorf("failed to get run %s: %w", id, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("run not found: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

func (c *Client) ListRuns(automationID string) ([]RunOut, error) {
	var out []RunOut
	r, err := c.http.R().SetResult(&out).Get(fmt.Sprintf("/api/v1/automations/%s/runs", automationID))
	if err != nil {
		return nil, fmt.Errorf("failed to list runs for %s: %w", automationID, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to list runs: %s (status %d)", r.String(), r.StatusCode())
	}
	return out, nil
}

func (c *Client) GetWorkflowTopology() ([]WorkflowNodeOut, error) {
	var out []WorkflowNodeOut
	r, err := c.http.R().SetResult(&out).Get("/api/v1/workflows/topology")
	if err != nil {
		return nil, fmt.Errorf("failed to get workflow topology: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to get workflow topology: %s (status %d)", r.String(), r.StatusCode())
	}
	return out, nil
}

func (c *Client) StreamRunTelemetry(runID string, handler func(event string, run *RunOut) error) error {
	url := fmt.Sprintf("%s/api/v1/runs/%s/stream", c.baseURL, runID)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "text/event-stream")
	req.Header.Set("User-Agent", "Orbit-CLI/0.2.0")

	httpClient := &http.Client{Timeout: 0}
	resp, err := httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to stream: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("stream connection failed with HTTP status %d", resp.StatusCode)
	}

	scanner := bufio.NewScanner(resp.Body)
	var currentEvent string
	var dataLines []string

	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "event:") {
			currentEvent = strings.TrimSpace(strings.TrimPrefix(line, "event:"))
		} else if strings.HasPrefix(line, "data:") {
			dataLines = append(dataLines, strings.TrimPrefix(line, "data:"))
		} else if line == "" {
			if len(dataLines) > 0 {
				joinedData := strings.Join(dataLines, "\n")
				var runOut RunOut
				if err := json.Unmarshal([]byte(joinedData), &runOut); err == nil {
					if err := handler(currentEvent, &runOut); err != nil {
						return err
					}
				}
				if currentEvent == "complete" {
					return nil
				}
				currentEvent = ""
				dataLines = nil
			}
		}
	}

	return scanner.Err()
}

func (c *Client) StreamRunResults(runID string, handler func(record *ResultOut) error) error {
	url := fmt.Sprintf("%s/api/v1/runs/%s/results/stream", c.baseURL, runID)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "text/event-stream")
	req.Header.Set("User-Agent", "Orbit-CLI/0.2.0")

	httpClient := &http.Client{Timeout: 0}
	resp, err := httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to results stream: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("results stream connection failed with HTTP status %d", resp.StatusCode)
	}

	scanner := bufio.NewScanner(resp.Body)
	var currentEvent string
	var dataLines []string

	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "event:") {
			currentEvent = strings.TrimSpace(strings.TrimPrefix(line, "event:"))
		} else if strings.HasPrefix(line, "data:") {
			dataLines = append(dataLines, strings.TrimPrefix(line, "data:"))
		} else if line == "" {
			if len(dataLines) > 0 {
				joinedData := strings.Join(dataLines, "\n")
				if currentEvent == "record" {
					var resOut ResultOut
					if err := json.Unmarshal([]byte(joinedData), &resOut); err == nil {
						if err := handler(&resOut); err != nil {
							return err
						}
					}
				} else if currentEvent == "complete" {
					return nil
				}
				currentEvent = ""
				dataLines = nil
			}
		}
	}

	return scanner.Err()
}
