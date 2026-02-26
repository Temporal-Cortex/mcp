# Configuration Guide

Complete reference for all Temporal Cortex MCP server configuration options, including environment variables, config files, timezone setup, week start, multi-calendar configuration, and calendar labeling.

## Configuration Hierarchy

The MCP server reads configuration from multiple sources. For settings that overlap, later sources override earlier ones:

1. **Built-in defaults** — sensible defaults for all optional settings
2. **Config file** — `~/.config/temporal-cortex/config.json` (set during `cortex-mcp auth` or `cortex-mcp setup`)
3. **Environment variables** — override config file values per-session
4. **Tool parameters** — override everything for individual tool calls (where supported)

## Environment Variables

### Calendar Provider Credentials

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLIENT_ID` | For Google | Google OAuth Client ID from [Cloud Console](https://console.cloud.google.com/apis/credentials). Format: `123456789-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | For Google | Google OAuth Client Secret. Format: `GOCSPX-...` |
| `GOOGLE_OAUTH_CREDENTIALS` | No | Path to Google OAuth JSON credentials file (alternative to `CLIENT_ID` + `CLIENT_SECRET`). The server reads `installed.client_id` and `installed.client_secret` from this file. |
| `MICROSOFT_CLIENT_ID` | For Outlook | Azure AD application (client) ID from [Azure Portal](https://portal.azure.com/). Format: UUID |
| `MICROSOFT_CLIENT_SECRET` | For Outlook | Azure AD client secret value (not the Secret ID) |

> **CalDAV note:** CalDAV credentials (iCloud, Fastmail, custom servers) are entered interactively during `cortex-mcp auth caldav` and stored in the credentials file. No environment variables are needed for CalDAV.

### Timezone and Locale

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TIMEZONE` | No | Auto-detected | IANA timezone override (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`). Overrides stored config and OS detection. |
| `WEEK_START` | No | `monday` | Week start day: `monday` (ISO 8601 standard) or `sunday`. Affects "start of week", "next week", "this week", and related expressions. |

**Timezone resolution order** (first match wins):

1. **Tool parameter** — explicit `timezone` on the API call
2. **`TIMEZONE` env var** — session-level override
3. **Config file** — `~/.config/temporal-cortex/config.json` (set during setup)
4. **OS detection** — reads the system timezone via `iana-time-zone`
5. **Error** — never silently falls back to UTC

> **Best practice:** Run `cortex-mcp setup` or `cortex-mcp auth` to set your timezone in the config file. Use the `TIMEZONE` env var only for temporary overrides (e.g., when traveling).

**Week start resolution order:**

1. **`WEEK_START` env var** — session-level override
2. **Config file** — `~/.config/temporal-cortex/config.json`
3. **Default** — `monday` (ISO 8601)

### Transport Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HTTP_PORT` | No | — | Port for HTTP transport. When set, enables streamable HTTP mode instead of stdio. |
| `HTTP_HOST` | No | `127.0.0.1` | Bind address for HTTP transport. Use `0.0.0.0` only behind a reverse proxy. |
| `ALLOWED_ORIGINS` | No | — | Comma-separated allowed Origin headers for HTTP mode (e.g., `http://localhost:3000,https://app.example.com`). All cross-origin requests are rejected if unset. |

### Booking and Locking

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TENANT_ID` | No | Auto-generated | UUID for tenant isolation. Auto-generated on first run. |
| `LOCK_TTL_SECS` | No | `30` | Lock time-to-live in seconds for Two-Phase Commit booking safety. Range: 5-300. |
| `REDIS_URLS` | No | — | Comma-separated Redis URLs. When set, activates Platform Mode with distributed locking (Redlock). |

### Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OAUTH_REDIRECT_PORT` | No | `8085` | Port for the local OAuth callback server during `auth` flows. Change if port 8085 is in use. |

### Telemetry

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TEMPORAL_CORTEX_TELEMETRY` | No | Prompt on first run | Override telemetry consent: `off` to disable, `on` to enable anonymous usage analytics. Non-interactive sessions (MCP stdio) auto-opt-out. |

## Config File

The config file at `~/.config/temporal-cortex/config.json` stores persistent preferences. It is created during `cortex-mcp auth` or `cortex-mcp setup`.

Example:

```json
{
  "timezone": "America/New_York",
  "week_start": "monday",
  "telemetry": false,
  "providers": ["google", "caldav"]
}
```

| Field | Description |
|-------|-------------|
| `timezone` | IANA timezone string |
| `week_start` | `"monday"` or `"sunday"` |
| `telemetry` | `true` or `false` |
| `providers` | Array of configured provider names |

You can edit this file directly, but running `cortex-mcp setup` is recommended for interactive validation.

## Credentials File

Calendar provider tokens are stored at `~/.config/temporal-cortex/credentials.json`. This file is created and managed by the auth flows. Do not edit it manually.

The file contains OAuth tokens (Google, Outlook) and CalDAV credentials (username, password, URL). It is read on every server startup to authenticate with calendar providers.

> **Security:** The credentials file contains sensitive tokens. Ensure appropriate file permissions (`chmod 600 ~/.config/temporal-cortex/credentials.json`). Do not commit it to version control.

## Multi-Calendar Setup

Temporal Cortex supports connecting multiple calendar providers simultaneously. Each provider is authenticated independently:

```bash
# Connect Google Calendar
npx @temporal-cortex/cortex-mcp auth google

# Connect Microsoft Outlook
npx @temporal-cortex/cortex-mcp auth outlook

# Connect CalDAV (iCloud, Fastmail, etc.)
npx @temporal-cortex/cortex-mcp auth caldav
```

On startup, the server discovers all configured providers and merges their calendars into a unified view.

### Provider-Prefixed Calendar IDs

When multiple providers are connected, calendar IDs are prefixed with the provider name:

| Provider | ID Format | Examples |
|----------|-----------|---------|
| Google | `google/<calendar_id>` | `google/primary`, `google/work@gmail.com` |
| Outlook | `outlook/<calendar_name>` | `outlook/Calendar`, `outlook/Work` |
| CalDAV | `caldav/<calendar_name>` | `caldav/Home`, `caldav/Personal` |

Use `list_calendars` to discover all available calendars and their prefixed IDs.

### Cross-Calendar Availability

The `get_availability` tool merges free/busy data across all specified calendars:

```json
{
  "start": "2026-03-16T00:00:00-04:00",
  "end": "2026-03-17T00:00:00-04:00",
  "calendar_ids": ["google/primary", "outlook/Calendar", "caldav/Home"]
}
```

This returns a single unified busy/free view. Privacy mode controls whether the response reveals how many calendars contributed to each busy block.

### Calendar Targeting

Most tools accept a `calendar_id` parameter to target a specific calendar:

- **Single provider:** Use the simple ID (e.g., `primary`)
- **Multi-provider:** Use the prefixed ID (e.g., `google/primary`, `outlook/Calendar`)

If you only have one provider connected, you can omit the prefix.

## Output Format Configuration

Data tools support two output formats:

| Format | Description | Default |
|--------|-------------|---------|
| `toon` | TOON (Token-Oriented Object Notation) — ~40% fewer tokens than JSON | Yes |
| `json` | Standard JSON | No |

TOON is the default output format for all data tools: `list_calendars`, `list_events`, `find_free_slots`, `expand_rrule`, and `get_availability`. To get JSON output, pass `format: "json"` as a tool parameter.

TOON roundtrips perfectly — encode to TOON, decode back to the original data structure with zero loss.

## Operating Modes

The server auto-detects its operating mode based on the environment.

### Local Mode (Default)

Active when `REDIS_URLS` is **not** set.

- In-memory lock manager (single-process safety)
- Local file credential storage (`~/.config/temporal-cortex/`)
- All 12 tools available
- No external infrastructure required

### Platform Mode

Active when `DATABASE_URL` **is** set (managed service at mcp.temporal-cortex.com).

- Postgres-backed credentials with managed OAuth lifecycle
- Bearer token authentication via API keys
- Redis-based distributed locking (Redlock algorithm) for multi-agent safety
- Usage metering, caller-based policies, and content firewall
- Designed for teams and production deployments

There is no manual mode flag — the server inspects the environment and selects the appropriate mode automatically.

## Example Configurations

### Minimal (Google Calendar only)

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Multi-Provider (Google + Outlook)

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-google-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-google-secret",
        "MICROSOFT_CLIENT_ID": "your-azure-app-id",
        "MICROSOFT_CLIENT_SECRET": "your-azure-secret",
        "TIMEZONE": "America/New_York",
        "WEEK_START": "sunday"
      }
    }
  }
}
```

### HTTP Transport

```json
{
  "env": {
    "HTTP_PORT": "8009",
    "HTTP_HOST": "127.0.0.1",
    "ALLOWED_ORIGINS": "http://localhost:3000"
  }
}
```

### Docker with Volume Mount

```bash
docker run --rm -i \
  -e GOOGLE_CLIENT_ID="your-id" \
  -e GOOGLE_CLIENT_SECRET="your-secret" \
  -e TIMEZONE="Europe/London" \
  -v ~/.config/temporal-cortex:/root/.config/temporal-cortex \
  cortex-mcp
```

## Next Steps

- [First Run Guide](first-run-guide.md) — getting started in 5 minutes
- [Google Calendar Setup](google-cloud-setup.md) — Google OAuth credential setup
- [Outlook Setup](outlook-setup.md) — Azure AD app registration
- [CalDAV Setup](caldav-setup.md) — iCloud, Fastmail, and custom CalDAV servers
