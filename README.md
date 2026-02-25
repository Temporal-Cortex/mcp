# Temporal Cortex MCP

[![CI](https://github.com/billylui/temporal-cortex-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/billylui/temporal-cortex-mcp/actions/workflows/ci.yml)
[![npm version](https://img.shields.io/npm/v/@temporal-cortex/cortex-mcp)](https://www.npmjs.com/package/@temporal-cortex/cortex-mcp)
[![npm downloads](https://img.shields.io/npm/dm/@temporal-cortex/cortex-mcp)](https://www.npmjs.com/package/@temporal-cortex/cortex-mcp)
[![Smithery](https://smithery.ai/badge/@temporal-cortex/cortex-mcp)](https://smithery.ai/server/@temporal-cortex/cortex-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**v0.4.5** · February 2026 · [Changelog](CHANGELOG.md) · **Website:** [temporal-cortex.com](https://temporal-cortex.com)

Temporal Cortex is a Model Context Protocol server that gives AI agents deterministic calendar capabilities — temporal context, datetime resolution, multi-calendar availability merging across Google Calendar, Microsoft Outlook, and CalDAV, and conflict-free booking with Two-Phase Commit. Powered by [Truth Engine](https://github.com/billylui/temporal-cortex-core). Install: `npx @temporal-cortex/cortex-mcp`.

<a href="https://insiders.vscode.dev/redirect/mcp/install?name=temporal-cortex-mcp&inputs=%7B%22google_client_id%22%3A%22%22%2C%22google_client_secret%22%3A%22%22%7D&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40temporal-cortex%2Fcortex-mcp%22%5D%2C%22env%22%3A%7B%22GOOGLE_CLIENT_ID%22%3A%22%24%7Binput%3Agoogle_client_id%7D%22%2C%22GOOGLE_CLIENT_SECRET%22%3A%22%24%7Binput%3Agoogle_client_secret%7D%22%7D%7D"><img src="https://img.shields.io/badge/VS_Code-Install_MCP_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
<a href="https://cursor.com/install-mcp?name=temporal-cortex&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkB0ZW1wb3JhbC1jb3J0ZXgvY29ydGV4LW1jcCJdLCJlbnYiOnsiR09PR0xFX0NMSUVOVF9JRCI6InlvdXItY2xpZW50LWlkLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiR09PR0xFX0NMSUVOVF9TRUNSRVQiOiJ5b3VyLWNsaWVudC1zZWNyZXQifX0%3D"><img src="https://img.shields.io/badge/Cursor-Install_MCP_Server-black?style=flat-square&logo=cursor&logoColor=white" alt="Install in Cursor"></a>

## Why do AI agents fail at calendar tasks?

LLMs get date and time tasks wrong roughly 60% of the time ([AuthenHallu benchmark](https://arxiv.org/abs/2510.10539)). Ask "What time is it?" and the model hallucinates. Ask "Schedule for next Tuesday at 2pm" and it picks the wrong Tuesday. Ask "Am I free at 3pm?" and it checks the wrong timezone. Then it double-books your calendar.

Most Calendar MCP servers are thin CRUD wrappers that pass these failures through to a single calendar provider — no temporal awareness, no conflict detection, no safety net.

## What makes Temporal Cortex different from other calendar MCP servers?

- **Temporal awareness** — Agents call `get_temporal_context` to know the actual time and timezone. `resolve_datetime` turns `"next Tuesday at 2pm"` into a precise RFC 3339 timestamp. No hallucination.
- **Atomic booking** — Lock the time slot, verify no conflicts exist, then write. Two agents booking the same 2pm slot? Exactly one succeeds. The other gets a clear error. No double-bookings.
- **Computed availability** — Merges free/busy data across multiple calendars into a single unified view. The AI sees actual availability, not a raw dump of events to misinterpret.
- **Deterministic RRULE expansion** — Handles DST transitions, `BYSETPOS=-1` (last weekday of month), `EXDATE` with timezones, leap year recurrences, and `INTERVAL>1` with `BYDAY`. Powered by [Truth Engine](https://github.com/billylui/temporal-cortex-core), not LLM inference.
- **Token-efficient output** — TOON format compresses calendar data to ~40% fewer tokens than standard JSON, reducing costs and context window usage.

## What do I need to run Temporal Cortex?

- **Node.js 18+** (for `npx` to download and run the binary) or **Docker**
- **At least one calendar provider**:
  - **Google Calendar** — requires [Google OAuth credentials](docs/google-cloud-setup.md)
  - **Microsoft Outlook** — requires Azure AD app registration (`MICROSOFT_CLIENT_ID`)
  - **CalDAV** (iCloud, Fastmail, etc.) — requires an app-specific password

## How do I install Temporal Cortex?

**Set up in 3 steps:**

1. **Install prerequisites** — Node.js 18+ (or Docker) and at least one calendar provider (Google Calendar, Microsoft Outlook, or CalDAV).
2. **Add the MCP configuration** to your AI client's config file (see client-specific examples below).
3. **Run the auth flow** — `npx @temporal-cortex/cortex-mcp auth google` (or `outlook` / `caldav`). This authenticates and configures timezone, week start, and telemetry preferences.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.4.5"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "TIMEZONE": "America/New_York"
      }
    }
  }
}
```

### Cursor

Add to Cursor's MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.4.5"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "TIMEZONE": "America/New_York"
      }
    }
  }
}
```

### Windsurf

Add to Windsurf's MCP config (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.4.5"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "TIMEZONE": "America/New_York"
      }
    }
  }
}
```

### Docker

```bash
docker run --rm -i \
  -e GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret" \
  -e TIMEZONE="America/New_York" \
  -v ~/.config/temporal-cortex:/root/.config/temporal-cortex \
  cortex-mcp
```

Build the image first: `docker build -t cortex-mcp .` (or build directly from the repo: `docker build -t cortex-mcp https://github.com/billylui/temporal-cortex-mcp.git`).

> **Need Google OAuth credentials?** See [docs/google-cloud-setup.md](docs/google-cloud-setup.md) for a step-by-step guide. For Outlook, add `MICROSOFT_CLIENT_ID`. For CalDAV (iCloud/Fastmail), no env vars needed — run `auth caldav` and enter your app-specific password.

## How do I authenticate with calendar providers?

On first run, the server needs calendar provider credentials. Run the auth flow for each provider you want to connect:

```bash
# Google Calendar (default)
npx @temporal-cortex/cortex-mcp auth google

# Microsoft Outlook
npx @temporal-cortex/cortex-mcp auth outlook

# CalDAV (iCloud, Fastmail, or custom server)
npx @temporal-cortex/cortex-mcp auth caldav

# Docker (interactive auth — needs terminal + browser)
docker run --rm -it \
  -e GOOGLE_CLIENT_ID="your-id" -e GOOGLE_CLIENT_SECRET="your-secret" \
  -p 8085:8085 \
  -v ~/.config/temporal-cortex:/root/.config/temporal-cortex \
  cortex-mcp auth google
```

Each auth flow saves credentials to `~/.config/temporal-cortex/credentials.json` and registers the provider in `~/.config/temporal-cortex/config.json`. You can connect multiple providers — the server discovers all configured providers on startup and merges their calendars into a unified view.

During auth, the server guides you through interactive setup:
- **Timezone** — auto-detects your system timezone and opens a fuzzy-search picker with all 597 IANA timezones (type to filter, arrow keys to navigate)
- **Week start** — arrow-key selection between Monday (ISO standard) and Sunday
- **Telemetry** — optional anonymous usage data (default: off)

All preferences are stored in `~/.config/temporal-cortex/config.json` and used by all temporal tools. You can override them per-session with the `TIMEZONE` and `WEEK_START` env vars.

After authentication, verify it works by asking your AI assistant: *"What time is it?"* — the agent should call `get_temporal_context` and return your current local time.

For a guided workflow, install the [calendar-scheduling Agent Skill](https://github.com/billylui/temporal-cortex-skill) to teach your AI agent the orient-resolve-query-book pattern.

## Cloud Mode

Instead of running the MCP server locally via `npx`, you can connect to the managed cloud endpoint. Cloud Mode requires no Node.js installation and no local OAuth credentials.

**Getting started:**

1. Sign up at [app.temporal-cortex.com](https://app.temporal-cortex.com).
2. Connect your Google Calendar or Microsoft Outlook account via OAuth in the dashboard.
3. Generate an API key from the dashboard.
4. Add the MCP config to your AI client (see examples below).

### Claude Desktop (Cloud)

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "url": "https://mcp.temporal-cortex.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Cursor (Cloud)

Add to Cursor's MCP settings (`~/.cursor/mcp.json`) using the same format:

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "url": "https://mcp.temporal-cortex.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**Benefits over Local Mode:**

- **No OAuth credentials to manage** -- calendar connections are handled in the dashboard via standard OAuth flows.
- **No Node.js required** -- the client connects directly to the cloud endpoint over HTTP.
- **Usage dashboard** -- monitor tool calls, connected calendars, and billing from [app.temporal-cortex.com](https://app.temporal-cortex.com).
- **Managed calendar connections** -- token refresh, re-authentication, and provider health are handled server-side.

All 11 tools and 4 layers work identically in Cloud Mode. The only difference is transport: the client sends requests to the cloud endpoint instead of a local stdio process.

## What tools does Temporal Cortex provide?

Temporal Cortex exposes 11 Model Context Protocol tools organized in 4 layers:

### Layer 1 — Temporal Context

| Tool | Description |
|------|-------------|
| `get_temporal_context` | Returns the current time, timezone, UTC offset, DST status, and day of week for the configured locale. Call this tool first in any calendar session. |
| `resolve_datetime` | Resolves human language expressions like "next Tuesday at 2pm" or "tomorrow morning" into precise RFC 3339 timestamps. |
| `convert_timezone` | Converts any RFC 3339 datetime from one IANA timezone to another, reporting the target timezone's DST status. |
| `compute_duration` | Computes the duration between two timestamps, returning days, hours, minutes, and a human-readable string. |
| `adjust_timestamp` | Adjusts a timestamp by a compound duration like "+1d2h30m" with DST-aware day-level shifts that preserve wall-clock time. |

### Layer 2 — Calendar Operations

| Tool | Description |
|------|-------------|
| `list_events` | Lists calendar events within a time range, supporting provider-prefixed IDs and TOON output format for approximately 40% fewer tokens. |
| `find_free_slots` | Finds available time slots in a calendar by computing gaps between events, with support for minimum slot duration. |
| `expand_rrule` | Expands RFC 5545 recurrence rules into concrete datetime instances, handling DST transitions, BYSETPOS, leap years, and EXDATE exclusions deterministically. |
| `check_availability` | Checks whether a specific time slot is available by examining both calendar events and active booking locks. |

### Layer 3 — Availability

| Tool | Description |
|------|-------------|
| `get_availability` | Merges free/busy data across multiple calendars into a single unified view with configurable privacy levels (Opaque or Full). |

### Layer 4 — Booking

| Tool | Description |
|------|-------------|
| `book_slot` | Books a calendar slot using Two-Phase Commit: acquires a time-range lock, verifies no conflicts exist, writes the event, then releases the lock. |

See [docs/tools.md](docs/tools.md) for full input/output schemas and usage examples.

## How does Temporal Cortex handle recurrence rules?

Most AI models and calendar tools silently fail on recurrence rule edge cases. Run the challenge to see the difference:

```bash
npx @temporal-cortex/cortex-mcp rrule-challenge
```

### 5 cases where LLMs consistently fail

**1. "Third Tuesday of every month" across DST (March 2026, America/New_York)**

The third Tuesday is March 17. Spring-forward on March 8 shifts UTC offsets from -05:00 to -04:00. LLMs often produce the wrong UTC time or skip the month entirely.

**2. "Last Friday of every month" (BYSETPOS=-1)**

`RRULE:FREQ=MONTHLY;BYDAY=FR;BYSETPOS=-1` — LLMs frequently return the first Friday instead of the last, or fail to handle months with 4 vs 5 Fridays.

**3. "Every weekday except holidays" (EXDATE with timezone)**

`EXDATE` values with explicit timezone offsets require exact matching against generated instances. LLMs often ignore EXDATE entirely or apply it to the wrong date.

**4. "Biweekly on Monday, Wednesday, Friday" (INTERVAL=2 + BYDAY)**

`RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR` — The `INTERVAL=2` applies to weeks, not individual days. LLMs frequently generate every-week occurrences instead of every-other-week.

**5. "February 29 yearly" (leap year recurrence)**

`RRULE:FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29` — Should only produce instances in leap years (2028, 2032...). LLMs often generate Feb 28 or Mar 1 in non-leap years.

Truth Engine handles all of these deterministically using the [RFC 5545](https://www.rfc-editor.org/rfc/rfc5545) specification. No inference, no hallucination.

## How does the MCP server architecture work?

The MCP server is a single Rust binary distributed via npm and Docker. It runs locally on your machine and communicates with MCP clients over stdio (standard input/output) or streamable HTTP.

**Request flow in 4 stages:**

1. **Receive** — The server accepts JSON-RPC messages from MCP clients over stdio (default) or streamable HTTP (when `HTTP_PORT` is set).
2. **Resolve** — Truth Engine converts human datetime expressions into precise UTC timestamps, handling timezone conversion and DST transitions deterministically.
3. **Compute** — For availability queries, the engine merges free/busy data across all connected calendar providers. For RRULE expansion, it generates concrete instances following RFC 5545 rules.
4. **Execute** — For booking operations, Two-Phase Commit acquires a lock, verifies the slot is free, writes the event, and releases the lock. Failure at any step triggers rollback.

TOON (Token-Oriented Object Notation) compresses calendar data for LLM consumption — approximately 40% fewer tokens than JSON, with perfect roundtrip fidelity.

### Stdio vs HTTP Transport

Transport mode is auto-detected — set `HTTP_PORT` to switch from stdio to HTTP.

- **Stdio** (default): Standard MCP transport for local clients (Claude Desktop, VS Code, Cursor). The server reads/writes JSON-RPC messages over stdin/stdout.
- **HTTP** (when `HTTP_PORT` is set): Streamable HTTP transport per MCP 2025-11-25 spec. The server listens on `http://{HTTP_HOST}:{HTTP_PORT}/mcp` with SSE streaming, session management (`Mcp-Session-Id` header), and Origin validation. Requests with an invalid `Origin` header are rejected with HTTP 403.

```bash
# HTTP mode example
HTTP_PORT=8009 npx @temporal-cortex/cortex-mcp@0.4.5
```

### Local Mode vs Platform Mode

Mode is auto-detected — there is no configuration flag.

- **Local Mode** (default): No infrastructure required. Uses in-memory locking and local file credential storage. Supports multiple calendar providers (Google, Outlook, CalDAV) with multi-calendar availability merging. Designed for individual developers.
- **Platform Mode** (activated when `REDIS_URLS` is set): Uses Redis-based distributed locking (Redlock) for multi-process safety. Designed for production deployments with multiple concurrent agents.

## How do I configure Temporal Cortex?

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | For Google | — | Google OAuth Client ID from [Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `GOOGLE_CLIENT_SECRET` | For Google | — | Google OAuth Client Secret |
| `GOOGLE_OAUTH_CREDENTIALS` | No | — | Path to Google OAuth JSON credentials file (alternative to `CLIENT_ID` + `CLIENT_SECRET`) |
| `MICROSOFT_CLIENT_ID` | For Outlook | — | Azure AD application (client) ID for Outlook calendar access |
| `MICROSOFT_CLIENT_SECRET` | For Outlook | — | Azure AD client secret for Outlook calendar access |
| `TIMEZONE` | No | auto-detected | IANA timezone override (e.g., `America/New_York`). Overrides stored config and OS detection. |
| `WEEK_START` | No | `monday` | Week start day: `monday` (ISO 8601) or `sunday`. Affects "start of week", "next week", etc. |
| `REDIS_URLS` | No | — | Comma-separated Redis URLs. When set, activates Platform Mode with distributed locking. |
| `TENANT_ID` | No | auto-generated | UUID for tenant isolation |
| `LOCK_TTL_SECS` | No | `30` | Lock time-to-live in seconds |
| `OAUTH_REDIRECT_PORT` | No | `8085` | Port for the local OAuth callback server |
| `HTTP_PORT` | No | — | Port for HTTP transport. When set, enables streamable HTTP mode instead of stdio. |
| `HTTP_HOST` | No | `127.0.0.1` | Bind address for HTTP transport. Use `0.0.0.0` only behind a reverse proxy. |
| `ALLOWED_ORIGINS` | No | — | Comma-separated allowed Origin headers for HTTP mode (e.g., `http://localhost:3000`). All cross-origin requests rejected if unset. |

At least one calendar provider must be configured. See [docs/google-cloud-setup.md](docs/google-cloud-setup.md) for Google setup. CalDAV providers (iCloud, Fastmail) use app-specific passwords configured via `cortex-mcp auth caldav`.

## How do I troubleshoot common issues?

| Problem | Solution |
|---------|----------|
| "No credentials found" | Run `npx @temporal-cortex/cortex-mcp auth google` (or `outlook` / `caldav`) to authenticate |
| OAuth error / "Access blocked" | Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (or `MICROSOFT_CLIENT_ID` and `MICROSOFT_CLIENT_SECRET` for Outlook) are correct. Ensure the OAuth consent screen is configured. |
| Port 8085 already in use | Set `OAUTH_REDIRECT_PORT` to a different port (e.g., `8086`) |
| Server not appearing in MCP client | Ensure Node.js 18+ is installed (`node --version`). Check your MCP client's logs for errors. |
| Provider not discovered on startup | Verify the provider is registered in `~/.config/temporal-cortex/config.json` (run `auth` again if needed) |

See [docs/google-cloud-setup.md](docs/google-cloud-setup.md) for detailed Google OAuth troubleshooting.

## Frequently Asked Questions

### Does Temporal Cortex work without internet access?

Layer 1 tools (temporal context, datetime resolution, timezone conversion, duration computation, timestamp adjustment) are pure computation and need no network access. Calendar tools (Layers 2-4) require network access to reach Google Calendar, Microsoft Outlook, or CalDAV APIs. The MCP server itself runs locally on your machine.

### Which AI clients are supported?

Any Model Context Protocol-compatible client works. Tested configurations are provided for Claude Desktop, Claude Code, VS Code with GitHub Copilot, Cursor, and Windsurf. The server uses stdio transport by default and also supports streamable HTTP transport for custom integrations.

### Can I connect multiple calendar providers simultaneously?

Yes. Run the auth flow for each provider (Google, Outlook, CalDAV) separately. The server discovers all configured providers on startup and merges their calendars into a unified availability view. Use provider-prefixed IDs like `google/primary` or `outlook/work` to target specific calendars.

### How does Two-Phase Commit prevent double-bookings?

When `book_slot` is called, the server acquires a time-range lock, verifies no conflicting events or active locks exist, writes the event to the calendar API, then releases the lock. If any step fails, the operation rolls back. Two agents booking the same slot simultaneously will have exactly one succeed and the other receive a clear error.

### What is TOON and why does it reduce costs?

TOON (Token-Oriented Object Notation) compresses calendar payloads by approximately 40% compared to JSON (38% on a Google Calendar event schema benchmark) while maintaining perfect roundtrip fidelity. Fewer tokens means lower API costs and more room in the LLM context window. Use `format: "toon"` with `list_events` to enable it.

### How does Temporal Cortex handle daylight saving time?

All temporal tools are DST-aware. `adjust_timestamp` with "+1d" across a spring-forward boundary preserves wall-clock time (1:00 AM EST becomes 1:00 AM EDT). RRULE expansion keeps recurring events at their local time across DST transitions. `get_temporal_context` reports whether DST is currently active.

### What is the difference between Local Mode and Platform Mode?

Local Mode (default) uses in-memory locking and local file storage with no infrastructure required. Platform Mode activates when `REDIS_URLS` is set, using Redis-based distributed locking (Redlock) for multi-process safety in production deployments with multiple concurrent agents.

### How accurate is the 60% hallucination statistic?

The figure comes from the AuthenHallu benchmark ([arXiv:2510.10539](https://arxiv.org/abs/2510.10539)), which measures LLM factual accuracy across categories. Date and time tasks showed the lowest accuracy, with models producing incorrect answers approximately 60% of the time. Temporal Cortex replaces LLM inference with deterministic computation for all calendar math.

### Is there a managed cloud option?

A managed cloud deployment is available for teams that need zero-setup hosting, managed OAuth, and multi-agent coordination. Self-hosted enterprise options include SSO, audit logging, and data residency controls. [Sign up for early access](https://tally.so/r/aQ66W2).

## Does Temporal Cortex collect telemetry?

During setup, an interactive prompt asks if you'd like to share anonymous usage data (default: off).

**Collected:** tool names, success/error counts, platform, version. **Never collected:** calendar data, events, or personal info.

Non-interactive sessions (MCP stdio) auto-opt-out. Change your choice anytime:

```bash
export TEMPORAL_CORTEX_TELEMETRY=off
```

## How do I teach my AI agent the scheduling workflow?

The **[calendar-scheduling](https://github.com/billylui/temporal-cortex-skill)** Agent Skill teaches AI agents the correct workflow for using these tools — from temporal orientation through conflict-free booking. Install it to give your agent procedural knowledge for calendar operations:

```bash
# Claude Code
cp -r temporal-cortex-skill/calendar-scheduling ~/.claude/skills/
```

The skill follows the [Agent Skills specification](https://agentskills.io/specification) and works with Claude Code, OpenAI Codex, Google Gemini, GitHub Copilot, Cursor, and 20+ other platforms.

## What is the computation layer behind Temporal Cortex?

The computation layer is open source:

- **[temporal-cortex-core](https://github.com/billylui/temporal-cortex-core)** — Truth Engine (temporal resolution, RRULE expansion, availability merging, timezone conversion) + TOON (token compression)
- Available on [crates.io](https://crates.io/crates/truth-engine), [npm](https://www.npmjs.com/package/@temporal-cortex/truth-engine), and [PyPI](https://pypi.org/project/temporal-cortex-toon/)
- 510+ Rust tests, 42 JS tests, 30 Python tests, ~9,000 property-based tests

## Contributing

Bug reports and feature requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
