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
	Short: "Inspect active adapter workflow pipeline and multi-sink topology",
	Long:  "Displays the end-to-end adapter pipeline (Parser, Converter, Generator, Redactor, S3, Slack).",
	RunE: func(cmd *cobra.Command, args []string) error {
		return renderWorkflow()
	},
}

func renderWorkflow() error {
	adapters := []AdapterInfo{
		{Stage: "1. Inbound Ingestion", Adapter: "LayoutParser", Type: "Document", Status: "ACTIVE", Description: "Semantic layout & table deconstruction"},
		{Stage: "2. Ingestion Normalize", Adapter: "FormatConverter", Type: "Document", Status: "ACTIVE", Description: "DOCX/XLSX to PDF/A conversion & OCR"},
		{Stage: "3. Schema Extraction", Adapter: "LLMExtractor", Type: "Agentic", Status: "ACTIVE", Description: "Structured record parsing & anomaly check"},
		{Stage: "4. Dossier Generation", Adapter: "HtmlDossierGenerator", Type: "Dossier", Status: "ACTIVE", Description: "Responsive executive HTML/PDF briefs"},
		{Stage: "5. Privacy Redactor", Adapter: "PiiRedactor", Type: "Compliance", Status: "ACTIVE", Description: "Automated PII masking (SSN, Email, Card)"},
		{Stage: "6. Object Storage", Adapter: "S3ExportSink", Type: "Storage", Status: "ACTIVE", Description: "Presigned URL & cloud bucket archival"},
		{Stage: "7. Notification Sink", Adapter: "SlackWebhookAdapter", Type: "Communication", Status: "ACTIVE", Description: "Telemetry alerts with signed dossier links"},
	}

	if jsonFlag {
		return formatters.PrintJSON(adapters)
	}

	fmt.Printf("\n%s\n", ui.Cyan("🛰️ Orbit Adapter Workflow Pipeline"))
	fmt.Println(ui.Gray("Visual pipeline topology from inbound ingestion to multi-sink dispatch:"))
	fmt.Println()

	fmt.Printf("  %s\n", ui.White("[Trigger] ──► [Discovery] ──► [LayoutParser] ──► [Extractor] ──► [DossierGen] ──► [S3/Slack]"))
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
