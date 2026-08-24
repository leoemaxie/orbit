package orbc

import (
	"fmt"
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
