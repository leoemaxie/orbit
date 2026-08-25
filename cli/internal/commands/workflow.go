package commands

import (
	"fmt"

	"github.com/leoemaxie/orbit/cli/internal/formatters"
	"github.com/leoemaxie/orbit/cli/internal/ui"
	"github.com/spf13/cobra"
)

type AdapterInfo struct {
	Stage       string `json:"stage"`
	Adapter     string `json:"adapter"`
	Type        string `json:"type"`
	Status      string `json:"status"`
	Description string `json:"description"`
}

var workflowCmd = &cobra.Command{
	Use:   "workflow",
	Short: "Inspect active adapter pipeline and storage/notification topology",
	Long:  "Displays the end-to-end pipeline (Parsers, LLM Extractor, PDF Report Generator, S3, Slack).",
	RunE: func(cmd *cobra.Command, args []string) error {
		return renderWorkflow()
	},
}

func renderWorkflow() error {
	var adapters []AdapterInfo

	serverNodes, err := client.GetWorkflowTopology()
	if err == nil && len(serverNodes) > 0 {
		for _, n := range serverNodes {
			adapters = append(adapters, AdapterInfo{
				Stage:       fmt.Sprintf("[%s] %s", n.Category, n.Label),
				Adapter:     n.Label,
				Type:        n.Category,
				Status:      n.Status,
				Description: n.Description,
			})
		}
	} else {
		// Offline fallback display
		adapters = []AdapterInfo{
			{Stage: "1. Trigger", Adapter: "Schedule Trigger", Type: "Trigger", Status: "ACTIVE", Description: "Cron schedule & webhook trigger"},
			{Stage: "2. Discovery", Adapter: "Source Discovery", Type: "Retrieval", Status: "ACTIVE", Description: "Search engine & web proxy retrieval"},
			{Stage: "3. Parser", Adapter: "Document & Table Parser", Type: "Document", Status: "ACTIVE", Description: "Document layout analysis & table extraction"},
			{Stage: "4. Extraction", Adapter: "LLM Schema Extraction", Type: "Extraction", Status: "ACTIVE", Description: "Structured JSON record extraction & validation"},
			{Stage: "5. Reports", Adapter: "PDF Report Generator", Type: "Reports", Status: "ACTIVE", Description: "Automated PDF reports with PII data masking"},
			{Stage: "6. Storage", Adapter: "Amazon S3 Storage", Type: "Storage", Status: "ACTIVE", Description: "S3 bucket archival & presigned download links"},
			{Stage: "7. Notifications", Adapter: "Slack Notifications", Type: "Alerts", Status: "ACTIVE", Description: "Slack alert webhook with report links"},
		}
	}

	if jsonFlag {
		return formatters.PrintJSON(adapters)
	}

	fmt.Printf("\n%s\n", ui.Cyan("🛰️ Orbit Pipeline Studio Topology"))
	fmt.Println(ui.Gray("Data pipeline topology from source ingestion to S3 and Slack sinks:"))
	fmt.Println()

	fmt.Printf("  %s\n", ui.White("[Trigger] ──► [Discovery] ──► [DocParser] ──► [LLMExtractor] ──► [ReportGen] ──► [S3 / Slack]"))
	fmt.Println()

	headers := []string{"Stage", "Active Adapter", "Category", "Status", "Description"}
	var rows [][]string
	for _, a := range adapters {
		rows = append(rows, []string{
			a.Stage,
			ui.Cyan(a.Adapter),
			a.Type,
			ui.Green(a.Status),
			a.Description,
		})
	}

	formatters.RenderTable(headers, rows)
	return nil
}
