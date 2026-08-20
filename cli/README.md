# Orbit CLI 🛰️

A high-performance, single-binary Go CLI for **Orbit — Autonomous Goal-Driven Web Data Operations**.

> *"Set the goal. Walk away."*

---

## 📦 Installation & Build

### Build from Source

```bash
cd cli
make build
# Binary is generated at bin/orbit
```

### Add to PATH

```bash
# macOS / Linux
cp bin/orbit /usr/local/bin/

# Windows (PowerShell)
Move-Item .\bin\orbit.exe C:\Windows\System32\
```

---

## ⚡ Commands Reference

### 1. Interpret & Create Goal

```bash
# Create automation and view synthesized plan
orbit goal "Every day at 8 AM, find cheapest PS5 in Nigeria and alert if price < 400000 NGN"

# Create and trigger immediate execution
orbit goal "Weekly, monitor Python remote jobs paying > $150k" --run

# Silent output (prints only automation ID)
ID=$(orbit goal "Find cheapest flights to London" -q)
```

### 2. Run On-Demand

```bash
orbit run <automation_id>
```

### 3. List Automations

```bash
orbit list
# or JSON format
orbit list --json | jq .
```

### 4. View Run History

```bash
orbit runs <automation_id>
```

### 5. Inspect Run & Provenance Trail

```bash
orbit show <run_id>
```

### 6. View & Export Extracted Data

```bash
# Table format
orbit data <run_id>

# Export to CSV
orbit data <run_id> --format csv > results.csv

# Export valid records to JSON
orbit data <run_id> --format json --valid-only | jq .
```

### 7. Manage Recurring Schedules

```bash
orbit schedule list
```

### 8. Configuration

```bash
# Point CLI to a remote Orbit instance
orbit config set api_url https://orbit.internal.corp

# View current configuration
orbit config show
```

### 9. Version & Health Probe

```bash
orbit version
```
