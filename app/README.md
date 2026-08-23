# Orbit Web Application

The Orbit Web Application is an operational telemetry interface and mission control dashboard for the Orbit autonomous web data operations platform. It provides a visual interface for natural-language goal submission, execution plan inspection, real-time provenance tracking, and data auditing.

---

## Technical Stack

- **Framework**: SvelteKit with Svelte 5 Runes (`$state`, `$derived`, `$effect`)
- **Styling**: Tailwind CSS v4
- **Icons**: `@lucide/svelte`
- **Deployment Adapter**: `@sveltejs/adapter-vercel`
- **Package Manager**: `pnpm`

---

## Features

- **Goal Studio**: Natural-language objective submission with live synthesis of execution plans, Cron schedules, and dynamic extraction schemas.
- **Execution Provenance DAG**: Interactive visual pipeline graph tracing every stage (Goal Synthesis, Source Discovery, Proxy Retrieval, Schema Extraction, Data Verification, and Condition Alerts) with slide-over log inspection.
- **Data Warehouse**: High-density tabular data viewer with validity filtering, anomaly inspection, and one-click CSV and JSON export capabilities.
- **Automation Fleet**: Centralized dashboard to monitor scheduled background jobs, view execution history, and trigger on-demand runs.

---

## Prerequisites

- **Node.js**: v20.x, v22.x, or v24.x (LTS recommended)
- **Package Manager**: `pnpm` (v9 or later)
- **Orbit Core API**: Backend daemon running on `http://localhost:8000` (optional for offline preview)

---

## Getting Started

### 1. Environment Configuration

Copy the example environment file and adjust the backend URL if necessary:

```bash
cp .env.example .env
```

Default configuration:
```env
PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 2. Install Dependencies

```bash
pnpm install
```

### 3. Start Development Server

```bash
pnpm dev
```

The application will be accessible at `http://localhost:5173`. Requests to `/api/v1` are automatically proxied to the Orbit Core backend configured in your `.env`.

---

## Production Build

### 1. Type Checking and Validation

```bash
pnpm check
```

### 2. Build for Production

```bash
pnpm build
```

The build output will be generated according to the `@sveltejs/adapter-vercel` specification.

### 3. Preview Production Build

```bash
pnpm preview
```

---

## Project Structure

```
app/
├── src/
│   ├── app.css              # Global styles and Tailwind v4 theme definitions
│   ├── app.html             # Root HTML template and web manifest links
│   ├── lib/
│   │   ├── api/             # Typed API client and TypeScript schema definitions
│   │   ├── components/      # UI primitives, Goal Studio, DAG visualizer, and Data Table
│   │   └── state/           # Svelte 5 reactive stores and telemetry state
│   └── routes/              # SvelteKit file-based routes
│       ├── +layout.svelte   # Main application shell and sidebar navigation
│       ├── +page.svelte     # Dashboard overview and Goal Omnibar
│       ├── automations/     # Automation fleet management and run history
│       ├── runs/            # Real-time execution DAG and telemetry inspection
│       └── data/            # Cross-automation data warehouse
├── static/                  # Static assets, vector icons, and web manifest
├── svelte.config.js         # SvelteKit adapter configuration
└── vite.config.ts           # Vite build configuration and API proxy
```
