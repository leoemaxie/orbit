package orbc

import (
	"fmt"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
)

type Client struct {
	http    *resty.Client
	baseURL string
}

func NewClient(baseURL string, timeout time.Duration) *Client {
	baseURL = strings.TrimRight(baseURL, "/")
	r := resty.New().
		SetBaseURL(baseURL).
		SetTimeout(timeout).
		SetHeader("Accept", "application/json").
		SetHeader("User-Agent", "Orbit-CLI/0.2.0")

	return &Client{http: r, baseURL: baseURL}
}

func (c *Client) BaseURL() string {
	return c.baseURL
}

func (c *Client) Health() (*HealthResponse, error) {
	var resp HealthResponse
	r, err := c.http.R().SetResult(&resp).Get("/api/v1/health")
	if err != nil {
		return nil, fmt.Errorf("health check failed: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("server error: %s (status %d)", r.String(), r.StatusCode())
	}
	return &resp, nil
}

func (c *Client) CreateAutomation(goal string) (*AutomationOut, error) {
	var out AutomationOut
	r, err := c.http.R().SetBody(GoalRequest{Goal: goal}).SetResult(&out).Post("/api/v1/automations")
	if err != nil {
		return nil, fmt.Errorf("failed to create automation: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to create automation: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

func (c *Client) ListAutomations() (*AutomationListOut, error) {
	var out AutomationListOut
	r, err := c.http.R().SetResult(&out).Get("/api/v1/automations")
	if err != nil {
		return nil, fmt.Errorf("failed to list automations: %w", err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("failed to list automations: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

func (c *Client) GetAutomation(id string) (*AutomationOut, error) {
	var out AutomationOut
	r, err := c.http.R().SetResult(&out).Get(fmt.Sprintf("/api/v1/automations/%s", id))
	if err != nil {
		return nil, fmt.Errorf("failed to get automation %s: %w", id, err)
	}
	if r.IsError() {
		return nil, fmt.Errorf("automation not found: %s (status %d)", r.String(), r.StatusCode())
	}
	return &out, nil
}

func (c *Client) DeleteAutomation(id string) error {
	r, err := c.http.R().Delete(fmt.Sprintf("/api/v1/automations/%s", id))
	if err != nil {
		return fmt.Errorf("failed to delete automation %s: %w", id, err)
	}
	if r.IsError() {
		return fmt.Errorf("failed to delete automation: %s (status %d)", r.String(), r.StatusCode())
	}
	return nil
}
