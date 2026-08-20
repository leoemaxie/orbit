package commands

import (
	"fmt"

	"github.com/spf13/cobra"
	"github.com/leoemaxie/orbit/cli/internal/config"
	"github.com/leoemaxie/orbit/cli/internal/formatters"
	"github.com/leoemaxie/orbit/cli/internal/ui"
)

var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Manage CLI configuration and preferences",
}

var configSetCmd = &cobra.Command{
	Use:   "set <key> <value>",
	Short: "Set a configuration parameter (e.g. api_url, format)",
	Args:  cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		key, val := args[0], args[1]
		if err := config.SetKey(key, val); err != nil {
			ui.Error("Failed to save config: %v", err)
			return err
		}
		ui.Success("Configuration updated: %s = %s", key, val)
		return nil
	},
}

var configShowCmd = &cobra.Command{
	Use:   "show",
	Short: "Show current configuration",
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := config.LoadConfig()
		if err != nil {
			return err
		}
		if jsonFlag {
			return formatters.PrintJSON(c)
		}
		ui.PrintBanner()
		fmt.Printf("API URL : %s\n", ui.Cyan(c.APIURL))
		fmt.Printf("Timeout : %s\n", ui.Cyan(fmt.Sprintf("%v", c.Timeout)))
		fmt.Printf("Format  : %s\n", ui.Cyan(c.Format))
		return nil
	},
}

func init() {
	configCmd.AddCommand(configSetCmd)
	configCmd.AddCommand(configShowCmd)
}
