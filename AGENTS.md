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

## 2. Managed vs. Custom Adapter Architecture

Orbit adapters generally operate in one of two modes (or support both):

1. **Managed Mode (`managed`):**
   * The platform handles provider authentication and credentials automatically using default daemon settings (e.g., `EMAIL_API_KEY`, `RETRIEVAL_API_KEY`).
   * End-users only supply operational configuration (e.g., `recipient_email`, `search_query`) without managing third-party accounts or API keys.

2. **Custom Mode (`custom`):**
   * The user or mission supplies their own custom API keys, endpoints, or target infrastructure (e.g., custom S3 bucket, private PostgreSQL URI, custom webhook URL).

3. **Hybrid Mode (`both`):**
   * Adapters like Email Notifications, Outbound Webhooks, and Document Processing default to managed execution while allowing optional custom credential overrides per node.

---

## 3. Configuration & Settings Standard

* Always use explicit `default="..."` or `default_factory=...` in Pydantic `Field(...)` declarations inside `core/config/settings.py`.
* Provide multi-alias support with `validation_alias=AliasChoices(...)` using provider-agnostic aliases (e.g. `AliasChoices("EMAIL_API_KEY", "MAIL_API_KEY", "SMTP_API_KEY")`).
* Ensure all sensitive keys (passwords, secrets, tokens) are masked in UI and diagnostic logs using `SecretVault.mask_secret(...)`.

---

## 4. Code & Commit Hygiene

* Use **Conventional Commits** for all git commit messages (`feat(...)`, `fix(...)`, `refactor(...)`, `test(...)`, `chore(...)`).
* Always maintain documentation integrity across docstrings and environment templates (`.env.example` and `core/.env.example`).
