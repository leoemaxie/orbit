package orbc

import (
	"fmt"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
)

type Client struct {
	http *resty.Client
}

func NewClient(baseURL string, timeout time.Duration) *Client {
	baseURL = strings.TrimRight(baseURL, "/")
	r := resty.New().
		SetBaseURL(baseURL).
		SetTimeout(timeout).
		SetHeader("Accept", "application/json").
		SetHeader("User-Agent", "Orbit-CLI/0.2.0")

	return &Client{http: r}
}

// Health checks the server connectivity and status.
func (c *Client) Health() (*HealthResponse, error) {
	var resp HealthResponse
	r, err := c.http.R().
		SetResult(&resp).
		Get("/api/v1/health")

	if err != nil {
		return nil, fmt.Errorf("health check failed: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("server error: %s (status %d)", r.String(), r.StatusCode())
	}
	return &resp, nil
}

// CreateAutomation creates a new automation from a natural-language goal.
func (c *Client) CreateAutomation(goal string) (*AutomationOut, error) {
	var out AutomationOut
	r, err := c.http.R().
		SetBody(GoalRequest{Goal: goal}).
		SetResult(&out).
		Post("/api/v1/automations")

	if err != nil {
		return nil, fmt.Errorf("failed to create automation: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to create automation: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

// ListAutomations retrieves all automations.
func (c *Client) ListAutomations() (*AutomationListOut, error) {
	var out AutomationListOut
	r, err := c.http.R().
		SetResult(&out).
		Get("/api/v1/automations")

	if err != nil {
		return nil, fmt.Errorf("failed to list automations: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to list automations: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

// GetAutomation fetches a single automation by ID.
func (c *Client) GetAutomation(id string) (*AutomationOut, error) {
	var out AutomationOut
	r, err := c.http.R().
		SetResult(&out).
		Get(fmt.Sprintf("/api/v1/automations/%s", id))

	if err != nil {
		return nil, fmt.Errorf("failed to get automation %s: %w", id, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("automation not found: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

// DeleteAutomation removes an automation.
func (c *Client) DeleteAutomation(id string) error {
	r, err := c.http.R().
		Delete(fmt.Sprintf("/api/v1/automations/%s", id))

	if err != nil {
		return fmt.Errorf("failed to delete automation %s: %w", id, err)
	}
	if r.IsError() {
		return fmt.Errorf("failed to delete automation: %s (status %d)", r.String(), r.StatusCode())
	}
	return nil
}

// RunAutomation triggers an execution of an automation.
func (c *Client) RunAutomation(id string) (*RunOut, error) {
	var out RunOut
	r, err := c.http.R().
		SetResult(&out).
		Post(fmt.Sprintf("/api/v1/automations/%s/run", id))

	if err != nil {
		return nil, fmt.Errorf("failed to run automation %s: %w", id, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to execute run: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

// GetRun fetches details of a specific run.
func (c *Client) GetRun(id string) (*RunOut, error) {
	var out RunOut
	r, err := c.http.R().
		SetResult(&out).
		Get(fmt.Sprintf("/api/v1/runs/%s", id))

	if err != nil {
		return nil, fmt.Errorf("failed to get run %s: %w", id, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("run not found: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

// ListRuns lists all past runs for a given automation.
func (c *Client) ListRuns(automationID string) ([]RunOut, error) {
	var out []RunOut
	r, err := c.http.R().
		SetResult(&out).
		Get(fmt.Sprintf("/api/v1/automations/%s/runs", automationID))

	if err != nil {
		return nil, fmt.Errorf("failed to list runs for %s: %w", automationID, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to list runs: %s (status %d)", r.String(), r.StatusCode())
	}
	return out, nil
}
