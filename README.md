# Temporal Cortex MCP

[![CI](https://github.com/billylui/temporal-cortex-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/billylui/temporal-cortex-mcp/actions/workflows/ci.yml)
[![npm version](https://img.shields.io/npm/v/@temporal-cortex/cortex-mcp)](https://www.npmjs.com/package/@temporal-cortex/cortex-mcp)
[![npm downloads](https://img.shields.io/npm/dm/@temporal-cortex/cortex-mcp)](https://www.npmjs.com/package/@temporal-cortex/cortex-mcp)
[![Smithery](https://smithery.ai/badge/@temporal-cortex/cortex-mcp)](https://smithery.ai/server/@temporal-cortex/cortex-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**The complete temporal stack for AI agents. Context. Computation. Calendars. Correct.**

<a href="https://insiders.vscode.dev/redirect/mcp/install?name=temporal-cortex-mcp&inputs=%7B%22google_client_id%22%3A%22%22%2C%22google_client_secret%22%3A%22%22%7D&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40temporal-cortex%2Fcortex-mcp%22%5D%2C%22env%22%3A%7B%22GOOGLE_CLIENT_ID%22%3A%22%24%7Binput%3Agoogle_client_id%7D%22%2C%22GOOGLE_CLIENT_SECRET%22%3A%22%24%7Binput%3Agoogle_client_secret%7D%22%7D%7D"><img src="https://img.shields.io/badge/VS_Code-Install_MCP_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
<a href="https://cursor.com/install-mcp?name=temporal-cortex&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkB0ZW1wb3JhbC1jb3J0ZXgvY29ydGV4LW1jcCJdLCJlbnYiOnsiR09PR0xFX0NMSUVOVF9JRCI6InlvdXItY2xpZW50LWlkLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiR09PR0xFX0NMSUVOVF9TRUNSRVQiOiJ5b3VyLWNsaWVudC1zZWNyZXQifX0%3D"><img src="https://img.shields.io/badge/Cursor-Install_MCP_Server-black?style=flat-square&logo=cursor&logoColor=white" alt="Install in Cursor"></a>

## The Problem

LLMs get date and time tasks wrong roughly 60% of the time ([AuthenHallu benchmark](https://arxiv.org/abs/2407.12282)). Ask "What time is it?" and the model hallucinates. Ask "Schedule for next Tuesday at 2pm" and it picks the wrong Tuesday. Ask "Am I free at 3pm?" and it checks the wrong timezone. Then it double-books your calendar.

Every other Calendar MCP server is a thin CRUD wrapper that passes these failures through to Google Calendar — no temporal awareness, no conflict detection, no safety net.

## What's Different

- **Temporal awareness** — Agents call `get_temporal_context` to know the actual time and timezone. `resolve_datetime` turns `"next Tuesday at 2pm"` into a precise RFC 3339 timestamp. No hallucination.
- **Atomic booking** — Lock the time slot, verify no conflicts exist, then write. Two agents booking the same 2pm slot? Exactly one succeeds. The other gets a clear error. No double-bookings.
- **Computed availability** — Merges free/busy data across multiple calendars into a single unified view. The AI sees actual availability, not a raw dump of events to misinterpret.
- **Deterministic RRULE expansion** — Handles DST transitions, `BYSETPOS=-1` (last weekday of month), `EXDATE` with timezones, leap year recurrences, and `INTERVAL>1` with `BYDAY`. Powered by [Truth Engine](https://github.com/billylui/temporal-cortex-core), not LLM inference.
- **Token-efficient output** — TOON format compresses calendar data to ~40% fewer tokens than standard JSON, reducing costs and context window usage.

## Prerequisites

- **Node.js 18+** (for `npx` to download and run the binary)
- **At least one calendar provider**:
  - **Google Calendar** — requires [Google OAuth credentials](docs/google-cloud-setup.md)
  - **Microsoft Outlook** — requires Azure AD app registration (`MICROSOFT_CLIENT_ID`)
  - **CalDAV** (iCloud, Fastmail, etc.) — requires an app-specific password

## Quick Start

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp"],
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
      "args": ["-y", "@temporal-cortex/cortex-mcp"],
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
      "args": ["-y", "@temporal-cortex/cortex-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "TIMEZONE": "America/New_York"
      }
    }
  }
}
```

> **Need Google OAuth credentials?** See [docs/google-cloud-setup.md](docs/google-cloud-setup.md) for a step-by-step guide. For Outlook, add `MICROSOFT_CLIENT_ID`. For CalDAV (iCloud/Fastmail), no env vars needed — run `auth caldav` and enter your app-specific password.

## First-Time Setup

On first run, the server needs calendar provider credentials. Run the auth flow for each provider you want to connect:

```bash
# Google Calendar (default)
npx @temporal-cortex/cortex-mcp auth google

# Microsoft Outlook
npx @temporal-cortex/cortex-mcp auth outlook

# CalDAV (iCloud, Fastmail, or custom server)
npx @temporal-cortex/cortex-mcp auth caldav
```

Each auth flow saves credentials to `~/.config/temporal-cortex/credentials.json` and registers the provider in `~/.config/temporal-cortex/config.json`. You can connect multiple providers — the server discovers all configured providers on startup and merges their calendars into a unified view.

During auth, the server detects your system timezone and prompts you to confirm or override it, then asks for your preferred week start day (Monday or Sunday). Both are stored in `~/.config/temporal-cortex/config.json` and used by all temporal tools. You can override them per-session with the `TIMEZONE` and `WEEK_START` env vars.

After authentication, verify it works by asking your AI assistant: *"What time is it?"* — the agent should call `get_temporal_context` and return your current local time.

## Available Tools (11)

### Layer 1 — Temporal Context

| Tool | Description |
|------|-------------|
| `get_temporal_context` | Current time, timezone, UTC offset, DST status, day of week. **Call this first.** |
| `resolve_datetime` | Resolve human expressions (`"next Tuesday at 2pm"`, `"tomorrow morning"`, `"+2h"`) to RFC 3339. |
| `convert_timezone` | Convert any RFC 3339 datetime between IANA timezones. |
| `compute_duration` | Duration between two timestamps (days, hours, minutes, human-readable). |
| `adjust_timestamp` | DST-aware timestamp adjustment (`"+1d"` across spring-forward = same wall-clock). |

### Layer 2 — Calendar Operations

| Tool | Description |
|------|-------------|
| `list_events` | List calendar events in a time range. Supports provider-prefixed IDs (`google/primary`). Output in TOON (~40% fewer tokens) or JSON. |
| `find_free_slots` | Find available time slots in a calendar. Supports provider-prefixed IDs. Computes actual gaps between events. |
| `expand_rrule` | Expand recurrence rules into concrete instances. Handles DST, BYSETPOS, leap years. |
| `check_availability` | Check if a specific time slot is available against events and active locks. |

### Layer 3 — Availability

| Tool | Description |
|------|-------------|
| `get_availability` | Merged free/busy view across multiple calendars with privacy controls. |

### Layer 4 — Booking

| Tool | Description |
|------|-------------|
| `book_slot` | Book a calendar slot safely. Lock → verify → write with Two-Phase Commit. |

See [docs/tools.md](docs/tools.md) for full input/output schemas and usage examples.

## The RRULE Challenge

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

## How It Works

The MCP server is a single Rust binary distributed via npm. It runs locally on your machine and communicates with MCP clients over stdio (standard input/output) or streamable HTTP.

- **Truth Engine** handles all date/time computation: temporal resolution, timezone conversion, RRULE expansion, availability merging, conflict detection. Deterministic, not inference-based.
- **TOON** (Token-Oriented Object Notation) compresses calendar data for LLM consumption — fewer tokens, same information.
- **Two-Phase Commit** ensures booking safety: acquire lock, verify the slot is free, write the event, release lock. If any step fails, everything rolls back.

### Stdio vs HTTP Transport

Transport mode is auto-detected — set `HTTP_PORT` to switch from stdio to HTTP.

- **Stdio** (default): Standard MCP transport for local clients (Claude Desktop, VS Code, Cursor). The server reads/writes JSON-RPC messages over stdin/stdout.
- **HTTP** (when `HTTP_PORT` is set): Streamable HTTP transport per MCP 2025-11-25 spec. The server listens on `http://{HTTP_HOST}:{HTTP_PORT}/mcp` with SSE streaming, session management (`Mcp-Session-Id` header), and Origin validation. Requests with an invalid `Origin` header are rejected with HTTP 403.

```bash
# HTTP mode example
HTTP_PORT=8009 npx @temporal-cortex/cortex-mcp
```

### Local Mode vs Platform Mode

Mode is auto-detected — there is no configuration flag.

- **Local Mode** (default): No infrastructure required. Uses in-memory locking and local file credential storage. Supports multiple calendar providers (Google, Outlook, CalDAV) with multi-calendar availability merging. Designed for individual developers.
- **Platform Mode** (activated when `REDIS_URLS` is set): Uses Redis-based distributed locking (Redlock) for multi-process safety. Designed for production deployments with multiple concurrent agents.

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | For Google | — | Google OAuth Client ID from [Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `GOOGLE_CLIENT_SECRET` | For Google | — | Google OAuth Client Secret |
| `GOOGLE_OAUTH_CREDENTIALS` | No | — | Path to Google OAuth JSON credentials file (alternative to `CLIENT_ID` + `CLIENT_SECRET`) |
| `MICROSOFT_CLIENT_ID` | For Outlook | — | Azure AD application (client) ID for Outlook calendar access |
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

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No credentials found" | Run `npx @temporal-cortex/cortex-mcp auth google` (or `outlook` / `caldav`) to authenticate |
| OAuth error / "Access blocked" | Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (or `MICROSOFT_CLIENT_ID` for Outlook) are correct. Ensure the OAuth consent screen is configured. |
| Port 8085 already in use | Set `OAUTH_REDIRECT_PORT` to a different port (e.g., `8086`) |
| Server not appearing in MCP client | Ensure Node.js 18+ is installed (`node --version`). Check your MCP client's logs for errors. |
| Provider not discovered on startup | Verify the provider is registered in `~/.config/temporal-cortex/config.json` (run `auth` again if needed) |

See [docs/google-cloud-setup.md](docs/google-cloud-setup.md) for detailed Google OAuth troubleshooting.

## Ready for More?

The open-source MCP server gives you full multi-calendar intelligence: connect Google, Outlook, and CalDAV simultaneously, with unified availability merging and conflict-free booking. When you're ready for more:

**Managed Cloud (Free)** — Zero-setup hosting with managed OAuth and dashboard UI. Up to 3 connected calendars, 50 bookings/month, all 11 tools.
→ [Sign up for early access](https://tally.so/r/aQ66W2)

**Open Scheduling (Pro)** — Let external agents and people book time with you. Shareable availability, inbound booking API, caller-based policies, and unlimited calendar connections.
→ [Request Early Access](https://tally.so/r/aQ66W2)

**Enterprise** — Self-hosted platform deployment, SSO/SAML, audit log export, data residency, and compliance documentation.
→ [Contact us](https://tally.so/r/aQ66W2)

## Built on Temporal Cortex Core

The computation layer is open source:

- **[temporal-cortex-core](https://github.com/billylui/temporal-cortex-core)** — Truth Engine (temporal resolution, RRULE expansion, availability merging, timezone conversion) + TOON (token compression)
- Available on [crates.io](https://crates.io/crates/truth-engine), [npm](https://www.npmjs.com/package/@temporal-cortex/truth-engine), and [PyPI](https://pypi.org/project/temporal-cortex-toon/)
- 510+ Rust tests, 42 JS tests, 30 Python tests, ~9,000 property-based tests

## Contributing

Bug reports and feature requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
