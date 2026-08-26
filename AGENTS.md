# Orbit — Agent & Developer Engineering Guidelines

This document outlines core architectural standards, design principles, and engineering guidelines for AI agents and human contributors working on the Orbit codebase.

---

## 1. Provider-Agnostic Design Principle (Critical Standard)

### Rule
**Never use vendor- or provider-specific names for file names, class names, function names, or environment variables.**

All adapters, pipeline steps, settings, and functions must remain **strictly provider-agnostic** unless the provider is an established industry-wide dominant protocol or standard (e.g., `S3`, `Slack`, `PostgreSQL`).

### Guidelines & Examples

| Component Category | ❌ Incorrect (Vendor-Specific) | ✅ Correct (Provider-Agnostic) | Standard Exception |
| :--- | :--- | :--- | :--- |
| **Email Delivery** | `resend.py`, `RESEND_API_KEY`, `send_resend_email` | `email.py`, `EMAIL_API_KEY`, `EmailNotificationAdapter` | None |
| **Web Retrieval** | `brightdata.py`, `BRIGHTDATA_API_KEY` | `retrieval.py`, `RETRIEVAL_API_KEY`, `DataRetrievalService` | None |
| **Search Engine** | `serpapi.py`, `SERPAPI_API_KEY` | `search_engine.py`, `SEARCH_ENGINE_API_KEY`, `SearchEngineDiscovery` | None |
| **Document Processing** | `foxit.py`, `nutrient.py`, `FOXIT_API_KEY` | `format_converter.py`, `DOCUMENT_CONVERTER_API_KEY`, `layout_parser.py` | None |
| **Cloud Storage** | — | `s3_export.py`, `S3_ACCESS_KEY`, `S3_BUCKET_NAME` | **S3** is an industry standard |
| **Team Chat** | — | `slack.py`, `SLACK_WEBHOOK_URL` | **Slack** is an industry standard |
| **Relational Database** | — | `database_sink.py`, `DATABASE_URL` | **SQL/Postgres** is an industry standard |

---

## 2. Managed vs. Custom & Destination Sink Scoping

Orbit adapters operate under clean separation between platform execution credentials and user destination sinks:

1. **Platform Execution Credentials (Daemon `.env`):**
   * Shared outbound engine keys (`LLM_API_KEY`, `RETRIEVAL_API_KEY`, `SEARCH_ENGINE_API_KEY`, `DOCUMENT_CONVERTER_API_KEY`, `EMAIL_API_KEY`).
   * Managed by the platform administrator for headless execution.

2. **Destination Sink Scoping (Per-Node / Per-Mission):**
   * Destination endpoints (`recipient_email`, `webhook_url`, `slack_webhook_url`, `s3_access_key`) must **never** be hardcoded as daemon-level environment variables (e.g. do NOT use `DEFAULT_RECIPIENT_EMAIL` or `DEFAULT_WEBHOOK_URL`).
   * User destination sinks belong strictly in the mission's DAG node configuration or must be elicited via `MissingParameter`.

3. **Hybrid Mode (`both`):**
   * Adapters like Email Notifications and Document Processing default to managed execution while allowing optional custom credential overrides per node.

---

## 3. Configuration, Pydantic & Type Safety Standards

* **Explicit Defaults:** Always use explicit `default="..."` or `default_factory=...` in Pydantic `Field(...)` declarations inside `core/config/settings.py` for Pyright and Uvicorn compatibility.
* **Multi-Alias Support:** Use `validation_alias=AliasChoices(...)` with provider-agnostic aliases (e.g. `AliasChoices("EMAIL_API_KEY", "MAIL_API_KEY", "SMTP_API_KEY")`).
* **Secret Masking:** Ensure all sensitive keys (passwords, secrets, tokens) are masked in UI and diagnostic logs using `SecretVault.mask_secret(...)`.
* **Exception Safety:** When catching third-party client exceptions (e.g. `httpx.HTTPError`), safely inspect attributes with `getattr(err, "response", None)` before accessing nested fields like `status_code`.
* **Enum Integrity:** Verify that run statuses match valid enum members (e.g., `RunStatus.verified`).

---

## 4. Frontend & UI Engineering Guidelines (`app/`)

### Component Size & Modularity (< 120 Lines)
* **Rule:** Svelte components in `app/src/lib/components/` must be single-responsibility and strictly under **~120 lines of code**.
* **Decomposition:** Large views or panels must be split into dedicated sub-components (e.g. separating complex views into `*Header.svelte`, `*Controls.svelte`, `*Card.svelte`, `*Table.svelte`, `*Row.svelte`).

### Svelte 5 Runes Standard
* **Strict Runes Usage:** Always use Svelte 5 runes:
  * `$state(...)` for reactive local variables.
  * `$derived(...)` for computed reactive expressions.
  * `$props()` for typed component arguments (`interface Props { ... }`).
  * `$effect(...)` for reactive side-effects and lifecycle sync.
* **No Legacy Syntax:** Never use legacy Svelte 3/4 syntax (`export let`, `$:`, writable stores).

### Design Tokens & Typography
* **Color Palette:** Deep Space Dark theme (`bg-void` `#07090E`, `bg-surface-900` `#0E131F`, `bg-surface-800` `#141B2D`, `accent-cyan` / `text-orbit-cyan` `#00F2FE` / `#38BDF8`).
* **Typography Hierarchy:**
  * `font-display` (`Space Grotesk`): Aerospace headers & hero titles.
  * `font-sans` (`Sora`): UI controls, buttons, tooltips, body text.
  * `font-mono` (`JetBrains Mono`): Telemetry data, metrics, timestamps, status badges, schedules.
* **Iconography:** Use `@lucide/svelte` exclusively with standardized sizing (`size={12-16}` for inline buttons/badges, `size={18-24}` for cards/banners).

### State Management & API Client
* Centralize domain state in `$lib/state/*.svelte.ts` (e.g. `orbitStore` in `orbit.svelte.ts`) with reactive runes.
* All backend API interactions must flow through the typed `ApiClient` in `$lib/api/client.ts`.

---

## 5. Code & Commit Hygiene

* **Conventional Commits:** Use standard Conventional Commit prefixes (`feat(...)`, `fix(...)`, `refactor(...)`, `test(...)`, `chore(...)`).
* **Intent-Driven Messages:** Summarize architectural intent and system impact; avoid verbose enumerations of individual variable names.
* **Documentation & CI Sync:** Keep `.env.example`, `core/.env.example`, and `.github/workflows/` synchronized with codebase changes.
