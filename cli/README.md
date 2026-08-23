# orbc 🛰️

A high-performance, single-binary Go CLI for **Orbit — Autonomous Goal-Driven Web Data Operations**.

> *"Set the goal. Walk away."*

---

## Installation & Build

### Build from Source

```bash
cd cli
make build
# Binary is generated at bin/orbc
```

### Add to PATH

```bash
# macOS / Linux
cp bin/orbc /usr/local/bin/

# Windows (PowerShell)
Move-Item .\bin\orbc.exe C:\Windows\System32\
```

---

## Commands Reference

### 1. Interpret & Create Goal

```bash
# Create automation and view synthesized plan
orbc goal "Every day at 8 AM, find cheapest PS5 in Nigeria and alert if price < 400000 NGN"

# Create and trigger immediate execution
orbc goal "Weekly, monitor Python remote jobs paying > $150k" --run

# Silent output (prints only automation ID)
ID=$(orbc goal "Find cheapest flights to London" -q)
```

### 2. Run On-Demand

```bash
orbc run <automation_id>
```

### 3. List Automations

```bash
orbc list
# or JSON format
orbc list --json | jq .
```

### 4. View Run History

```bash
orbc runs <automation_id>
```

### 5. Inspect Run & Provenance Trail

```bash
orbc show <run_id>
```

### 6. View & Export Extracted Data

```bash
# Table format
orbc data <run_id>

# Export to CSV
orbc data <run_id> --format csv > results.csv

# Export valid records to JSON
orbc data <run_id> --format json --valid-only | jq .
```

### 7. Manage Recurring Schedules

```bash
orbc schedule list
```

### 8. Configuration

```bash
# Point CLI to a remote Orbit instance
orbc config set api_url https://orbit.internal.corp

# View current configuration
orbc config show
```

### 9. Version & Health Probe

```bash
orbc version
```
