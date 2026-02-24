# LLM-Optimized Installation Guide

This guide is designed for AI agents (e.g., Cline auto-install) to set up `@temporal-cortex/cortex-mcp`.

## Prerequisites

- Node.js 18+
- A Google account with Google Calendar
- Google OAuth credentials ([setup guide](docs/google-cloud-setup.md))

## Installation

No installation step needed. The server runs via `npx`:

```bash
npx -y @temporal-cortex/cortex-mcp
```

### Docker Alternative

```bash
docker build -t cortex-mcp https://github.com/billylui/temporal-cortex-mcp.git
docker run --rm -i \
  -e GOOGLE_CLIENT_ID=your-id -e GOOGLE_CLIENT_SECRET=your-secret \
  -v ~/.config/temporal-cortex:/root/.config/temporal-cortex \
  cortex-mcp
```

## Authentication

Before first use, set up Google OAuth:

```bash
GOOGLE_CLIENT_ID=your-id GOOGLE_CLIENT_SECRET=your-secret npx @temporal-cortex/cortex-mcp auth
```

This opens a browser for Google consent. Tokens are saved to `~/.config/temporal-cortex/credentials.json`.

## MCP Client Configuration

### Claude Desktop

File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "npx",
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.4.3"],
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
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.4.3"],
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
      "args": ["-y", "@temporal-cortex/cortex-mcp@0.4.3"],
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

> "What meetings do I have today?"

The AI should use the `list_events` tool and return your calendar events.

## Available Tools (11)

**Layer 1 — Temporal Context** (call `get_temporal_context` first):

| Tool | Purpose |
|------|---------|
| `get_temporal_context` | Current time, timezone, UTC offset, DST status |
| `resolve_datetime` | Resolve `"next Tuesday at 2pm"` to RFC 3339 |
| `convert_timezone` | Convert datetimes between timezones |
| `compute_duration` | Duration between two timestamps |
| `adjust_timestamp` | DST-aware timestamp adjustment |

**Layer 2-4 — Calendar Operations, Availability, Booking**:

| Tool | Purpose |
|------|---------|
| `list_events` | List calendar events in a time range |
| `find_free_slots` | Find available time slots |
| `book_slot` | Book a slot with conflict prevention |
| `expand_rrule` | Expand recurrence rules into instances |
| `check_availability` | Check if a time slot is free |
| `get_availability` | Merged availability across calendars |

## Troubleshooting

- **No credentials found**: Run `npx @temporal-cortex/cortex-mcp auth` first
- **OAuth error**: Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly
- **Wrong timezone**: Set `TIMEZONE` env var (e.g., `America/New_York`) or re-run auth
- **Port conflict**: Set `OAUTH_REDIRECT_PORT` to a different port (default: 8085)
