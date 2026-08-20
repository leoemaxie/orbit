package commands

import (
	"github.com/spf13/cobra"
	"github.com/leoemaxie/orbit/cli/internal/formatters"
	"github.com/leoemaxie/orbit/cli/internal/ui"
	"github.com/leoemaxie/orbit/cli/pkg/orbitclient"
)

var scheduleCmd = &cobra.Command{
	Use:   "schedule",
	Short: "Manage and inspect recurring automation schedules",
}

var scheduleListCmd = &cobra.Command{
	Use:   "list",
	Short: "List active recurring schedules",
	RunE: func(cmd *cobra.Command, args []string) error {
		list, err := client.ListAutomations()
		if err != nil {
			ui.Error("Failed to list schedules: %v", err)
			return err
		}

		scheduled := make([]orbitclient.AutomationOut, 0)
		for _, a := range list.Items {
			if a.Active && a.Plan.Frequency != "once" {
				scheduled = append(scheduled, a)
			}
		}

		if jsonFlag {
			return formatters.PrintJSON(scheduled)
		}

		ui.PrintBanner()
		ui.Info("Recurring Schedules Daemon:")
		formatters.RenderAutomationsTable(scheduled)
		return nil
	},
}

func init() {
	scheduleCmd.AddCommand(scheduleListCmd)
}
