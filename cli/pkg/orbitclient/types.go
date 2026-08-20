package orbitclient

// ExtractionField defines a single dynamic field in an extraction schema.
type ExtractionField struct {
	Name        string   `json:"name"`
	Type        string   `json:"type"`
	Description string   `json:"description,omitempty"`
	Required    bool     `json:"required"`
	EnumValues  []string `json:"enum_values,omitempty"`
}

// DynamicExtractionSchema describes the dynamic entity schema produced by the Goal Interpreter.
type DynamicExtractionSchema struct {
	EntityName  string            `json:"entity_name"`
	Fields      []ExtractionField `json:"fields"`
	Description string            `json:"description,omitempty"`
}

// ExecutionPlan is the structured representation of a goal.
type ExecutionPlan struct {
	Objective           string                  `json:"objective"`
	Domain              string                  `json:"domain"`
	SearchQuery         string                  `json:"search_query"`
	SourceHints         []string                `json:"source_hints,omitempty"`
	Geography           string                  `json:"geography,omitempty"`
	CountryCode         string                  `json:"country_code,omitempty"`
	ExtractionSchema    DynamicExtractionSchema `json:"extraction_schema"`
	Frequency           string                  `json:"frequency"`
	ScheduleTime        string                  `json:"schedule_time,omitempty"`
	Timezone            string                  `json:"timezone"`
	Condition           string                  `json:"condition,omitempty"`
	NotificationChannel string                  `json:"notification_channel,omitempty"`
}

// GoalRequest is sent when creating an automation.
type GoalRequest struct {
	Goal string `json:"goal"`
}

// AutomationOut represents a registered automation.
type AutomationOut struct {
	ID        string        `json:"id"`
	RawGoal   string        `json:"raw_goal"`
	Plan      ExecutionPlan `json:"plan"`
	Active    bool          `json:"active"`
	CreatedAt string        `json:"created_at"`
	NextRunAt *string       `json:"next_run_at,omitempty"`
}

// AutomationListOut is the paginated/list response.
type AutomationListOut struct {
	Items []AutomationOut `json:"items"`
	Total int             `json:"total"`
}

// ResultOut represents a single extracted data row.
type ResultOut struct {
	ID               string                 `json:"id"`
	URL              string                 `json:"url,omitempty"`
	Data             map[string]interface{} `json:"data"`
	Valid            bool                   `json:"valid"`
	ValidationErrors []string               `json:"validation_errors,omitempty"`
	CreatedAt        string                 `json:"created_at"`
}

// RunOut represents a single execution of an automation.
type RunOut struct {
	ID               string                   `json:"id"`
	AutomationID     string                   `json:"automation_id"`
	Status           string                   `json:"status"`
	StartedAt        string                   `json:"started_at"`
	FinishedAt       *string                  `json:"finished_at,omitempty"`
	SourcesFound     []string                 `json:"sources_found,omitempty"`
	PagesRetrieved   []string                 `json:"pages_retrieved,omitempty"`
	ExtractedCount   int                      `json:"extracted_count"`
	ValidatedCount   int                      `json:"validated_count"`
	ConditionMatched *bool                    `json:"condition_matched,omitempty"`
	ConditionMessage *string                  `json:"condition_message,omitempty"`
	ReasoningLog     []map[string]interface{} `json:"reasoning_log,omitempty"`
	Error            *string                  `json:"error,omitempty"`
	Results          []ResultOut              `json:"results,omitempty"`
}

// HealthResponse represents the health probe response.
type HealthResponse struct {
	Status           string `json:"status"`
	Version          string `json:"version"`
	Environment      string `json:"environment"`
	SchedulerEnabled bool   `json:"scheduler_enabled"`
}
