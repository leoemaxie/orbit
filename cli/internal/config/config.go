package config

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/spf13/viper"
)

// Config holds all CLI user preferences and connection info.
type Config struct {
	APIURL  string        `mapstructure:"api_url"`
	Timeout time.Duration `mapstructure:"timeout"`
	Format  string        `mapstructure:"format"`
}

// LoadConfig loads the CLI configuration from ~/.orbc/config.yaml or environment variables.
func LoadConfig() (*Config, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return nil, fmt.Errorf("failed to get user home directory: %w", err)
	}

	configDir := filepath.Join(home, ".orbc")
	configFile := filepath.Join(configDir, "config.yaml")

	viper.AddConfigPath(configDir)
	// Also check fallback ~/.orbit for backward compatibility
	viper.AddConfigPath(filepath.Join(home, ".orbit"))
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")

	viper.SetDefault("api_url", DefaultAPIURL)
	viper.SetDefault("timeout", DefaultTimeout)
	viper.SetDefault("format", DefaultFormat)

	viper.SetEnvPrefix("ORBC")
	viper.AutomaticEnv()

	// If config file doesn't exist, create ~/.orbc/config.yaml with defaults
	if _, err := os.Stat(configFile); os.IsNotExist(err) {
		_ = os.MkdirAll(configDir, 0755)
		_ = viper.WriteConfigAs(configFile)
	} else {
		_ = viper.ReadInConfig()
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("unable to decode config: %w", err)
	}

	return &cfg, nil
}

// SetKey updates a configuration key and saves to ~/.orbc/config.yaml.
func SetKey(key, value string) error {
	home, err := os.UserHomeDir()
	if err != nil {
		return err
	}

	configDir := filepath.Join(home, ".orbc")
	_ = os.MkdirAll(configDir, 0755)
	configFile := filepath.Join(configDir, "config.yaml")

	viper.Set(key, value)
	return viper.WriteConfigAs(configFile)
}
