package commands

import (
	"fmt"
	"os"

	"github.com/leoemaxie/orbit/cli/internal/config"
	"github.com/leoemaxie/orbit/cli/pkg/orbc"
	"github.com/spf13/cobra"
)

var (
	apiURLFlag  string
	jsonFlag    bool
	verboseFlag bool

	cfg    *config.Config
	client *orbc.Client
)

// RootCmd is the base command for orbc CLI.
var RootCmd = &cobra.Command{
	Use:   "orbc",
	Short: "orbc - Autonomous Goal-Driven Web Data Operations CLI",
	Long: `orbc is an agentic web-data automation CLI for Orbit.
Transform natural-language goals into recurring, verifiable web-data workflows.

"Set the goal. Walk away."`,
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		var err error
		cfg, err = config.LoadConfig()
		if err != nil {
			return fmt.Errorf("error loading configuration: %w", err)
		}

		targetURL := cfg.APIURL
		if apiURLFlag != "" {
			targetURL = apiURLFlag
		}

		client = orbc.NewClient(targetURL, cfg.Timeout)
		return nil
	},
}

func init() {
	RootCmd.PersistentFlags().StringVar(&apiURLFlag, "api-url", "", "Orbit API Base URL (default: http://localhost:8000)")
	RootCmd.PersistentFlags().BoolVar(&jsonFlag, "json", false, "Output raw JSON")
	RootCmd.PersistentFlags().BoolVarP(&verboseFlag, "verbose", "v", false, "Enable verbose logging")

	// Add subcommands
	RootCmd.AddCommand(goalCmd)
	RootCmd.AddCommand(runCmd)
	RootCmd.AddCommand(listCmd)
	RootCmd.AddCommand(runsCmd)
	RootCmd.AddCommand(showCmd)
	RootCmd.AddCommand(dataCmd)
	RootCmd.AddCommand(rmCmd)
	RootCmd.AddCommand(scheduleCmd)
	RootCmd.AddCommand(workflowCmd)
	RootCmd.AddCommand(configCmd)
	RootCmd.AddCommand(versionCmd)
}

// Execute runs the root command.
func Execute() {
	if err := RootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
