package commands

import (
	"fmt"

	"github.com/spf13/cobra"
	"github.com/leoemaxie/orbit/cli/internal/formatters"
	"github.com/leoemaxie/orbit/cli/internal/ui"
	"github.com/leoemaxie/orbit/cli/pkg/orbc"
)

var watchCmd = &cobra.Command{
	Use:   "watch <run-id>",
	Short: "Stream live telemetry and logs for an autonomous run in real time",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		runID := args[0]
		return executeWatch(runID)
	},
}

func init() {
	rootCmd.AddCommand(watchCmd)
}

func executeWatch(runID string) error {
	ui.Header(fmt.Sprintf("??? Orbit Stream — Tailing Run %s", runID[:8]))
	lastStatus := ""

	err := client.StreamRunTelemetry(runID, func(event string, run *orbc.RunOut) error {
		if run.Status != lastStatus {
			lastStatus = run.Status
			switch run.Status {
			case "discovering":
				ui.Info("[Stage: Discover] Finding web sources and search queries...")
			case "retrieving":
				ui.Info("[Stage: Retrieve] Resilient proxy fetch across %d source(s)...", len(run.SourcesFound))
			case "extracting":
				ui.Info("[Stage: Extract] LLM entity and schema extraction active...")
			case "validating":
				ui.Info("[Stage: Validate] Anomaly detection and statistical validation...")
			case "storing":
				ui.Info("[Stage: Store] Writing results and generating export sinks...")
			case "verified":
				ui.Success("[Stage: Verified] Run verified successfully with %d valid record(s).", run.ValidatedCount)
			case "failed":
				ui.Error("[Stage: Failed] Execution failed: %s", formatError(run.Error))
			}
		}

		if event == "complete" {
			if len(run.Results) > 0 {
				fmt.Println()
				fmt.Printf("%s\n", ui.Cyan("Extracted Data Records:"))
				formatters.RenderResultsTable(run.Results)
			}
		}
		return nil
	})

	return err
}

func formatError(err *string) string {
	if err == nil || *err == "" {
		return "Unknown error"
	}
	return *err
}
