package orbc

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestClient_Health(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/health" {
			t.Errorf("unexpected path: %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(HealthResponse{
			Status:           "ok",
			Version:          "0.2.0",
			Environment:      "test",
			SchedulerEnabled: true,
		})
	}))
	defer ts.Close()

	client := NewClient(ts.URL, 5*time.Second)
	resp, err := client.Health()
	if err != nil {
		t.Fatalf("Health() error = %v", err)
	}

	if resp.Status != "ok" || resp.Version != "0.2.0" {
		t.Errorf("unexpected health response: %+v", resp)
	}
}

func TestClient_CreateAutomation(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/automations" || r.Method != http.MethodPost {
			t.Errorf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(AutomationOut{
			ID:      "auto-123",
			RawGoal: "Find PS5",
			Plan: ExecutionPlan{
				Objective:   "Find PS5",
				Domain:      "ecommerce",
				SearchQuery: "PS5 Nigeria",
				Frequency:   "daily",
			},
			Active:    true,
			CreatedAt: "2026-08-20T23:00:00Z",
		})
	}))
	defer ts.Close()

	client := NewClient(ts.URL, 5*time.Second)
	resp, err := client.CreateAutomation("Find PS5")
	if err != nil {
		t.Fatalf("CreateAutomation() error = %v", err)
	}

	if resp.ID != "auto-123" || resp.Plan.Domain != "ecommerce" {
		t.Errorf("unexpected automation response: %+v", resp)
	}
}
