package formatters

import (
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/olekukonko/tablewriter"
	"github.com/leoemaxie/orbit/cli/pkg/orbitclient"
)

// RenderAutomationsTable renders a list of automations into an ASCII table.
func RenderAutomationsTable(automations []orbitclient.AutomationOut) {
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader([]string{"ID", "OBJECTIVE", "DOMAIN", "FREQUENCY", "ACTIVE", "NEXT RUN"})
	table.SetBorder(true)
	table.SetAutoWrapText(true)
	table.SetHeaderColor(
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
	)

	for _, a := range automations {
		nextRun := "-"
		if a.NextRunAt != nil {
			nextRun = *a.NextRunAt
		}
		activeStr := "Yes"
		if !a.Active {
			activeStr = "No"
		}
		table.Append([]string{
			a.ID[:8] + "...",
			a.Plan.Objective,
			a.Plan.Domain,
			a.Plan.Frequency,
			activeStr,
			nextRun,
		})
	}
	table.Render()
}

// RenderRunsTable renders a list of runs into an ASCII table.
func RenderRunsTable(runs []orbitclient.RunOut) {
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader([]string{"RUN ID", "STATUS", "EXTRACTED", "VALIDATED", "CONDITION", "STARTED AT"})
	table.SetBorder(true)
	table.SetHeaderColor(
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
		tablewriter.Colors{tablewriter.Bold, tablewriter.FgCyanColor},
	)

	for _, r := range runs {
		cond := "-"
		if r.ConditionMatched != nil {
			if *r.ConditionMatched {
				cond = "MATCHED"
			} else {
				cond = "NO"
			}
		}
		table.Append([]string{
			r.ID[:8] + "...",
			r.Status,
			fmt.Sprintf("%d", r.ExtractedCount),
			fmt.Sprintf("%d", r.ValidatedCount),
			cond,
			r.StartedAt,
		})
	}
	table.Render()
}

// RenderResultsTable dynamically renders arbitrary extracted records into an aligned table.
func RenderResultsTable(results []orbitclient.ResultOut) {
	if len(results) == 0 {
		fmt.Println("No records extracted.")
		return
	}

	// Discover all distinct keys across records
	keySet := make(map[string]bool)
	for _, res := range results {
		for k := range res.Data {
			keySet[k] = true
		}
	}

	keys := make([]string, 0, len(keySet))
	for k := range keySet {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	headers := append([]string{"VALID"}, keys...)
	headers = append(headers, "URL")

	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader(headers)
	table.SetBorder(true)
	table.SetAutoWrapText(true)

	for _, res := range results {
		validStr := "✓"
		if !res.Valid {
			validStr = "✖"
		}
		row := []string{validStr}
		for _, k := range keys {
			val := res.Data[k]
			if val == nil {
				row = append(row, "-")
			} else {
				row = append(row, fmt.Sprintf("%v", val))
			}
		}
		urlStr := res.URL
		if len(urlStr) > 40 {
			urlStr = urlStr[:37] + "..."
		}
		row = append(row, urlStr)
		table.Append(row)
	}
	table.Render()
}
