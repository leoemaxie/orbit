package commands

import (
	"fmt"

	"github.com/spf13/cobra"
	"github.com/leoemaxie/orbit/cli/internal/formatters"
	"github.com/leoemaxie/orbit/cli/internal/ui"
	"github.com/leoemaxie/orbit/cli/pkg/orbitclient"
)

var (
	formatFlag    string
	validOnlyFlag bool
)

var dataCmd = &cobra.Command{
	Use:   "data <run-id>",
	Short: "View and export extracted records for a run",
	Example: `  orbc data 8f2c34a1
  orbc data 8f2c34a1 --format csv > results.csv
  orbc data 8f2c34a1 --format json | jq .`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		runID := args[0]
		run, err := client.GetRun(runID)
		if err != nil {
			ui.Error("Failed to fetch data for run: %v", err)
			return err
		}

		results := run.Results
		if validOnlyFlag {
			filtered := make([]orbitclient.ResultOut, 0)
			for _, r := range results {
				if r.Valid {
					filtered = append(filtered, r)
				}
			}
			results = filtered
		}

		switch formatFlag {
		case "json":
			return formatters.PrintJSON(results)
		case "csv":
			return formatters.ExportResultsCSV(results)
		case "table":
			formatters.RenderResultsTable(results)
			return nil
		default:
			return fmt.Errorf("unsupported format '%s', choose from table, json, csv", formatFlag)
		}
	},
}

func init() {
	dataCmd.Flags().StringVarP(&formatFlag, "format", "f", "table", "Output format: table, json, csv")
	dataCmd.Flags().BoolVar(&validOnlyFlag, "valid-only", false, "Show only records that passed validation")
}
