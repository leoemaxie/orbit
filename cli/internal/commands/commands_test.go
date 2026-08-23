package commands

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/leoemaxie/orbit/cli/pkg/orbc"
	"github.com/spf13/viper"
)

// resetFlags resets package-level flags before running a command test
func resetFlags() {
	apiURLFlag = ""
	jsonFlag = false
	verboseFlag = false
	runImmediatelyFlag = false
	quietFlag = false
	formatFlag = "table"
	validOnlyFlag = false
	viper.Reset()
}

func executeCommand(args ...string) (string, error) {
	resetFlags()

	r, w, _ := os.Pipe()
	origStdout := os.Stdout
	os.Stdout = w

	outC := make(chan string)
	go func() {
		var buf bytes.Buffer
		_, _ = io.Copy(&buf, r)
		outC <- buf.String()
	}()

	RootCmd.SetArgs(args)
	err := RootCmd.Execute()

	_ = w.Close()
	os.Stdout = origStdout
	out := <-outC
	_ = r.Close()

	return out, err
}

func setupMockServer() *httptest.Server {
	mockAuto := orbc.AutomationOut{
		ID:      "auto-5555",
		RawGoal: "Track laptop prices",
		Plan: orbc.ExecutionPlan{
			Objective:   "Find laptops under $1000",
			Domain:      "ecommerce",
			SearchQuery: "laptops sale",
			Frequency:   "daily",
			ExtractionSchema: orbc.DynamicExtractionSchema{
				EntityName: "laptop",
				Fields: []orbc.ExtractionField{
					{Name: "brand", Type: "string", Required: true, Description: "Brand name"},
					{Name: "price", Type: "number", Required: true, Description: "Price in USD"},
				},
			},
		},
		Active:    true,
		CreatedAt: "2026-08-23T00:00:00Z",
	}

	condMatched := true
	condMsg := "Price < 1000"
	mockRun := orbc.RunOut{
		ID:               "run-7777",
		AutomationID:     "auto-5555",
		Status:           "completed",
		StartedAt:        "2026-08-23T12:00:00Z",
		ExtractedCount:   2,
		ValidatedCount:   2,
		ConditionMatched: &condMatched,
		ConditionMessage: &condMsg,
		SourcesFound:     []string{"https://store.com/item1"},
		PagesRetrieved:   []string{"https://store.com/item1"},
		Results: []orbc.ResultOut{
			{
				ID:    "res-1",
				URL:   "https://store.com/item1",
				Valid: true,
				Data: map[string]interface{}{
					"brand": "Dell",
					"price": 850,
				},
			},
		},
	}

	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		switch {
		case r.URL.Path == "/api/v1/health":
			_ = json.NewEncoder(w).Encode(orbc.HealthResponse{
				Status:           "ok",
				Version:          "0.2.0",
				Environment:      "test",
				SchedulerEnabled: true,
			})
		case r.URL.Path == "/api/v1/automations" && r.Method == http.MethodPost:
			_ = json.NewEncoder(w).Encode(mockAuto)
		case r.URL.Path == "/api/v1/automations" && r.Method == http.MethodGet:
			_ = json.NewEncoder(w).Encode(orbc.AutomationListOut{
				Items: []orbc.AutomationOut{mockAuto},
				Total: 1,
			})
		case r.URL.Path == "/api/v1/automations/auto-5555" && r.Method == http.MethodGet:
			_ = json.NewEncoder(w).Encode(mockAuto)
		case r.URL.Path == "/api/v1/automations/auto-5555/run" && r.Method == http.MethodPost:
			_ = json.NewEncoder(w).Encode(mockRun)
		case r.URL.Path == "/api/v1/automations/auto-5555/runs" && r.Method == http.MethodGet:
			_ = json.NewEncoder(w).Encode([]orbc.RunOut{mockRun})
		case r.URL.Path == "/api/v1/runs/run-7777" && r.Method == http.MethodGet:
			_ = json.NewEncoder(w).Encode(mockRun)
		default:
			http.NotFound(w, r)
		}
	}))
}

func TestCommand_Goal(t *testing.T) {
	ts := setupMockServer()
	defer ts.Close()

	t.Run("interactive display", func(t *testing.T) {
		out, err := executeCommand("goal", "Find laptops under $1000", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("goal command failed: %v", err)
		}

		if !strings.Contains(out, "auto-5555") || !strings.Contains(out, "Find laptops under $1000") {
			t.Errorf("expected goal output to contain automation ID and objective: %s", out)
		}
	})

	t.Run("quiet flag returns only ID", func(t *testing.T) {
		out, err := executeCommand("goal", "Find laptops", "--quiet", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("goal --quiet failed: %v", err)
		}

		if strings.TrimSpace(out) != "auto-5555" {
			t.Errorf("expected quiet output 'auto-5555', got %q", out)
		}
	})

	t.Run("json flag returns valid json", func(t *testing.T) {
		out, err := executeCommand("goal", "Find laptops", "--json", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("goal --json failed: %v", err)
		}

		var parsed map[string]interface{}
		if err := json.Unmarshal([]byte(out), &parsed); err != nil {
			t.Fatalf("expected valid JSON output: %v, raw: %s", err, out)
		}
		if parsed["id"] != "auto-5555" {
			t.Errorf("unexpected JSON content: %+v", parsed)
		}
	})

	t.Run("missing arguments fails validation", func(t *testing.T) {
		_, err := executeCommand("goal", "--api-url", ts.URL)
		if err == nil {
			t.Fatalf("expected error when goal argument is missing")
		}
	})
}

func TestCommand_List(t *testing.T) {
	ts := setupMockServer()
	defer ts.Close()

	t.Run("table output", func(t *testing.T) {
		out, err := executeCommand("list", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("list failed: %v", err)
		}

		if !strings.Contains(out, "auto-555") {
			t.Errorf("list output missing auto-555: %s", out)
		}
	})

	t.Run("json output", func(t *testing.T) {
		out, err := executeCommand("list", "--json", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("list --json failed: %v", err)
		}

		var list orbc.AutomationListOut
		if err := json.Unmarshal([]byte(out), &list); err != nil {
			t.Fatalf("invalid json from list: %v, raw: %s", err, out)
		}
		if list.Total != 1 || list.Items[0].ID != "auto-5555" {
			t.Errorf("unexpected list output: %+v", list)
		}
	})
}

func TestCommand_Run_And_Runs(t *testing.T) {
	ts := setupMockServer()
	defer ts.Close()

	t.Run("run command execution", func(t *testing.T) {
		out, err := executeCommand("run", "auto-5555", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("run failed: %v", err)
		}

		if !strings.Contains(out, "run-7777") || !strings.Contains(out, "Execution Audit Trail") {
			t.Errorf("unexpected run output: %s", out)
		}
	})

	t.Run("runs list history", func(t *testing.T) {
		out, err := executeCommand("runs", "auto-5555", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("runs failed: %v", err)
		}

		if !strings.Contains(out, "run-7777") {
			t.Errorf("runs table missing run-7777: %s", out)
		}
	})
}

func TestCommand_Show(t *testing.T) {
	ts := setupMockServer()
	defer ts.Close()

	out, err := executeCommand("show", "run-7777", "--api-url", ts.URL)
	if err != nil {
		t.Fatalf("show command failed: %v", err)
	}

	if !strings.Contains(out, "run-7777") || !strings.Contains(out, "Discovered Sources") {
		t.Errorf("unexpected show output: %s", out)
	}
}

func TestCommand_Data(t *testing.T) {
	ts := setupMockServer()
	defer ts.Close()

	t.Run("json format", func(t *testing.T) {
		out, err := executeCommand("data", "run-7777", "--format", "json", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("data --format json failed: %v", err)
		}

		var results []orbc.ResultOut
		if err := json.Unmarshal([]byte(out), &results); err != nil {
			t.Fatalf("invalid json data: %v, raw: %s", err, out)
		}
		if len(results) != 1 || results[0].Data["brand"] != "Dell" {
			t.Errorf("unexpected results data: %+v", results)
		}
	})

	t.Run("csv format", func(t *testing.T) {
		out, err := executeCommand("data", "run-7777", "--format", "csv", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("data --format csv failed: %v", err)
		}

		if !strings.Contains(out, "id,valid,url,brand,price") || !strings.Contains(out, "Dell,850") {
			t.Errorf("unexpected csv output: %s", out)
		}
	})

	t.Run("invalid format returns error", func(t *testing.T) {
		_, err := executeCommand("data", "run-7777", "--format", "yaml", "--api-url", ts.URL)
		if err == nil {
			t.Fatalf("expected error for unsupported format 'yaml'")
		}
	})
}

func TestCommand_Version(t *testing.T) {
	ts := setupMockServer()
	defer ts.Close()

	t.Run("version with connected server", func(t *testing.T) {
		out, err := executeCommand("version", "--json", "--api-url", ts.URL)
		if err != nil {
			t.Fatalf("version failed: %v", err)
		}

		var ver map[string]interface{}
		if err := json.Unmarshal([]byte(out), &ver); err != nil {
			t.Fatalf("invalid json: %v, raw: %s", err, out)
		}

		if ver["cli_version"] != CLIVersion || ver["server_version"] != "0.2.0" {
			t.Errorf("unexpected version json: %+v", ver)
		}
	})
}
