package commands

import (
	"github.com/leoemaxie/orbit/cli/internal/formatters"
	"github.com/leoemaxie/orbit/cli/internal/ui"
	"github.com/spf13/cobra"
)

var deleteCmd = &cobra.Command{
	Use:     "delete <automation-id>",
	Aliases: []string{"del", "rm"},
	Short:   "Delete an automation and its associated runs",
	Args:    cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		automationID := args[0]
		return executeDelete(automationID)
	},
}

func executeDelete(automationID string) error {
	err := client.DeleteAutomation(automationID)
	if err != nil {
		if jsonFlag {
			return formatters.PrintJSON(map[string]any{
				"success": false,
				"error":   err.Error(),
			})
		}
		ui.Error("Failed to delete automation: %v", err)
		return err
	}

	if jsonFlag {
		return formatters.PrintJSON(map[string]any{
			"success":       true,
			"automation_id": automationID,
			"message":       "Automation deleted successfully",
		})
	}

	ui.Success("Automation %s and all associated runs deleted successfully.", ui.Cyan(automationID))
	return nil
}
