# LLM-Optimized Installation Guide

This guide is designed for AI agents (e.g., Cline auto-install) to set up `@temporal-cortex/cortex-mcp`.

## Prerequisites

- Node.js 18+
- At least one calendar provider:
  - Google Calendar — [Google OAuth credentials](docs/google-cloud-setup.md)
  - Microsoft Outlook — [Azure AD app registration](docs/outlook-setup.md)
  - CalDAV (iCloud, Fastmail) — [app-specific password](docs/caldav-setup.md)

## Installation

No installation step needed. The server runs via `npx`:

```bash
npx -y @temporal-cortex/cortex-mcp
```

### Docker Alternative

```bash
docker build -t cortex-mcp https://github.com/temporal-cortex/mcp.git
docker run --rm -i \
  -e GOOGLE_CLIENT_ID=your-id -e GOOGLE_CLIENT_SECRET=your-secret \
  -v ~/.config/temporal-cortex:/root/.config/temporal-cortex \
  cortex-mcp
```

## Authentication

The fastest way to get started is the setup wizard:

```bash
npx @temporal-cortex/cortex-mcp setup
```

Or authenticate individual providers:

```bash
# Google Calendar
GOOGLE_CLIENT_ID=your-id GOOGLE_CLIENT_SECRET=your-secret npx @temporal-cortex/cortex-mcp auth google

# Microsoft Outlook
MICROSOFT_CLIENT_ID=your-id MICROSOFT_CLIENT_SECRET=your-secret npx @temporal-cortex/cortex-mcp auth outlook

# CalDAV (iCloud, Fastmail)
npx @temporal-cortex/cortex-mcp auth caldav
```

This opens a browser for OAuth consent (or prompts for CalDAV credentials). Tokens are saved to `~/.config/temporal-cortex/credentials.json`.

## MCP Client Configuration

### Claude Desktop

File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.5.7"],
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

File: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.5.7"],
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

File: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.5.7"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "TIMEZONE": "America/New_York"
      }
    }
  }
}
```

## Verification

After configuration, restart your MCP client and ask:

> "List my calendars."

The AI should use the `list_calendars` tool and return your connected calendars with provider-prefixed IDs.

## Available Tools (12)

**Layer 1 — Temporal Context** (call `get_temporal_context` first):

| Tool | Purpose |
|------|---------|
| `get_temporal_context` | Current time, timezone, UTC offset, DST status, next DST transition |
| `resolve_datetime` | Resolve `"next Tuesday at 2pm"` to RFC 3339 |
| `convert_timezone` | Convert datetimes between timezones |
| `compute_duration` | Duration between two timestamps |
| `adjust_timestamp` | DST-aware timestamp adjustment |

**Layer 2 — Calendar Operations** (TOON output by default, `format: "json"` for JSON):

| Tool | Purpose |
|------|---------|
| `list_calendars` | List all calendars across connected providers |
| `list_events` | List calendar events in a time range |
| `find_free_slots` | Find available time slots |
| `expand_rrule` | Expand recurrence rules into instances |
| `check_availability` | Check if a time slot is free |

**Layer 3-4 — Availability & Booking**:

| Tool | Purpose |
|------|---------|
| `get_availability` | Merged availability across calendars (TOON default) |
| `book_slot` | Book a slot with conflict prevention |

## Troubleshooting

- **No credentials found**: Run `npx @temporal-cortex/cortex-mcp auth` first
- **OAuth error**: Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly
- **Wrong timezone**: Set `TIMEZONE` env var (e.g., `America/New_York`) or re-run auth
- **Port conflict**: Set `OAUTH_REDIRECT_PORT` to a different port (default: 8085)
