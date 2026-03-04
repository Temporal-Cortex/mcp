# First Run Guide

Get Temporal Cortex running with your AI agent in 5 minutes.

## Before You Start

You need:

- **Node.js 18+** — verify with `node --version`
- **An MCP-compatible AI client** — Claude Desktop, Cursor, Windsurf, VS Code with GitHub Copilot, or Claude Code
- **A calendar account** — Google Calendar, Microsoft Outlook, or CalDAV (iCloud, Fastmail)

If you need to set up provider credentials first, see the provider guides:
- [Google Calendar Setup](google-cloud-setup.md) — create Google OAuth credentials (~10 min)
- [Microsoft Outlook Setup](outlook-setup.md) — create Azure AD app registration (~10 min)
- [CalDAV Setup](caldav-setup.md) — get an app-specific password (~5 min)

## Step 1: Run the Setup Wizard

The setup wizard handles authentication, timezone, and MCP client configuration in one guided flow:

```bash
npx @temporal-cortex/cortex-mcp setup
```

The wizard will:

1. **Select a provider** — choose Google Calendar, Microsoft Outlook, or CalDAV
2. **Authenticate** — complete the OAuth flow (Google/Outlook) or enter CalDAV credentials
3. **Configure timezone** — auto-detects your system timezone and lets you confirm or change it via fuzzy search (597 IANA timezones)
4. **Configure week start** — choose Monday (ISO standard) or Sunday
5. **Telemetry preference** — optional anonymous usage data (default: off)
6. **Generate MCP config** — outputs the JSON config snippet for your AI client

> **Alternative:** If you prefer manual setup, skip the wizard and follow the steps in the [README](../README.md#how-do-i-install-temporal-cortex).

## Step 2: Add the MCP Configuration

Copy the JSON config from the wizard output into your AI client's configuration file.

### Claude Desktop

File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

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

### Cursor

File: `~/.cursor/mcp.json`

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

### Windsurf

File: `~/.codeium/windsurf/mcp_config.json`

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

### Claude Code

No config file needed. Add directly from the command line:

```bash
claude mcp add temporal-cortex -- npx -y @temporal-cortex/cortex-mcp
```

> **Note:** For Claude Code, set provider credentials as environment variables in your shell profile or use the `cortex-mcp setup` wizard which stores them in the config file.

## Step 3: Restart and Verify

1. **Restart your AI client** — close and reopen Claude Desktop, Cursor, or Windsurf. For Claude Code, start a new session.
2. **Ask a test question** — try one of these:

| Test | What to Expect |
|------|----------------|
| "What time is it?" | Agent calls `get_temporal_context` and returns your local time with timezone |
| "List my calendars." | Agent calls `list_calendars` and returns your calendars with provider-prefixed IDs |
| "What meetings do I have today?" | Agent calls `list_events` and returns today's events |
| "Am I free at 3pm tomorrow?" | Agent calls `check_availability` and confirms whether the slot is open |

If the agent successfully calls Temporal Cortex tools and returns calendar data, you are set up correctly.

## What to Try Next

Once you have verified the basic setup, try these workflows:

### Scheduling a Meeting

> "Schedule a 30-minute meeting with alice@example.com tomorrow at 2pm called 'Project Sync'."

The agent should:
1. Call `get_temporal_context` to orient in time
2. Call `resolve_datetime` to parse "tomorrow at 2pm"
3. Call `check_availability` to verify the slot is free
4. Call `book_slot` to create the event

### Finding Free Time

> "When am I free for a 1-hour meeting this week?"

The agent should:
1. Call `get_temporal_context` for current time
2. Call `resolve_datetime` for "this week" boundaries
3. Call `find_free_slots` with a 60-minute minimum

### Cross-Calendar Availability

> "Show my availability across all calendars for next Monday."

The agent should:
1. Call `list_calendars` to discover all connected calendars
2. Call `get_availability` with all calendar IDs

### Timezone Conversion

> "What time is 3pm Tokyo time in New York?"

The agent should call `convert_timezone` and return the converted time with DST information.

## Adding the Agent Skill (Optional)

The **[Temporal Cortex Agent Skills](https://github.com/temporal-cortex/skills)** teach your AI agent the correct workflow pattern for calendar operations — orient, resolve, query, book. Install them for more reliable scheduling behavior:

```bash
# Claude Code
npx skills add temporal-cortex/skills
```

The skill is optional but recommended. It follows the [Agent Skills specification](https://agentskills.io/specification) and works with 26+ AI platforms.

## Troubleshooting

### Server not appearing in MCP client

1. Verify Node.js 18+ is installed: `node --version`
2. Verify the config file path is correct for your client
3. Check your client's MCP logs for errors
4. Try running the server manually to check for errors: `npx @temporal-cortex/cortex-mcp`

### "No credentials found"

Run the auth flow for your provider:

```bash
npx @temporal-cortex/cortex-mcp auth google   # or outlook / caldav
```

Or use the setup wizard: `npx @temporal-cortex/cortex-mcp setup`

### Wrong timezone

Set the `TIMEZONE` environment variable, or re-run the setup wizard:

```bash
npx @temporal-cortex/cortex-mcp setup
```

### Agent not using Temporal Cortex tools

Some AI clients need to be explicitly told to use the MCP tools. Try being specific:

> "Use the Temporal Cortex tools to check my calendar for tomorrow."

Or install the [Temporal Cortex Agent Skills](https://github.com/temporal-cortex/skills) for automatic tool routing.

## Next Steps

- [Configuration Guide](configuration-guide.md) — all environment variables, multi-calendar setup, output format configuration
- [Google Calendar Setup](google-cloud-setup.md) — detailed Google OAuth walkthrough
- [Outlook Setup](outlook-setup.md) — Azure AD app registration
- [CalDAV Setup](caldav-setup.md) — iCloud, Fastmail, and custom CalDAV servers
- [Tool Reference](tools.md) — full input/output schemas for all 12 tools
