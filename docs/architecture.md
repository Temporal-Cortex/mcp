# Architecture

High-level overview of how the Temporal Cortex MCP server works.

## Overview

The MCP server is a single Rust binary that communicates with AI clients (Claude Desktop, Cursor, Windsurf) over **stdio** or **streamable HTTP**. It runs locally on your machine.

```
┌─────────────────┐  stdio / HTTP  ┌─────────────────┐     HTTPS     ┌──────────────┐
│   MCP Client    │ ◄────────────► │   cortex-mcp    │ ◄──────────► │ Google       │
│ (Claude Desktop,│                │   (Rust binary)  │              │ Calendar API │
│  Cursor, etc.)  │                └─────────────────┘              └──────────────┘
└─────────────────┘
```

## Tool Layers

The 11 tools are organized into 4 layers. Agents work top-down: orient in time, then query calendars, then book.

```
Layer 4: Booking          [book_slot]                                        — Safe mutation
Layer 3: Availability     [get_availability]                                 — Cross-calendar query
Layer 2: Calendar Ops     [list_events, find_free_slots, expand_rrule,       — Calendar data
                           check_availability]
Layer 1: Temporal Context  [get_temporal_context, resolve_datetime,            — Time awareness
                            convert_timezone, compute_duration,
                            adjust_timestamp]
```

### Typical Agent Workflow

```
1. get_temporal_context           → "It's Friday 2:30 PM EST, DST inactive"
2. resolve_datetime("next Tue     → "2026-02-24T14:00:00-05:00"
   at 2pm")
3. find_free_slots(start, end)   → [14:00-15:00, 16:00-17:00]
4. book_slot(start, end, title)  → Lock → Verify → Write → Done
```

### Layer 1 — Temporal Context

AI agents call `get_temporal_context` first to learn the current time, timezone, UTC offset, and DST status. Then `resolve_datetime` converts human expressions like `"next Tuesday at 2pm"` into precise RFC 3339 timestamps that Layer 2-4 tools accept.

Layer 1 tools are pure computation — no calendar API calls, no network. They use the OS clock (`chrono::Utc::now()`) and the `chrono-tz` crate for timezone handling.

### Timezone Resolution

Timezone is resolved in this order (first match wins):

1. **Tool parameter** — explicit `timezone` on the API call
2. **`TIMEZONE` env var** — session-level override
3. **Config file** — `~/.config/temporal-cortex/config.json` (set during `cortex-mcp auth`)
4. **OS detection** — `iana-time-zone` crate reads the system timezone
5. **Error** — never silently falls back to UTC

## Distribution

The binary is distributed via npm as `@temporal-cortex/cortex-mcp`. When you run `npx @temporal-cortex/cortex-mcp`, npm downloads the correct platform-specific binary (macOS ARM64/x64, Linux x64/ARM64, Windows x64) via optional dependencies.

This means no Rust toolchain is required — `npx` handles everything.

### Docker

A Docker image is also available for containerized deployments and CI pipelines:

```bash
docker build -t cortex-mcp https://github.com/billylui/temporal-cortex-mcp.git
docker run --rm -i cortex-mcp
```

The Dockerfile uses a multi-stage build: the first stage installs the npm package to extract the platform binary, and the final image is a minimal Debian Trixie slim with just the binary and CA certificates. No Node.js runtime is included in the final image.

## Key Components

### Truth Engine

Handles all date and time computation deterministically:

- **Temporal resolution**: Converts human expressions (`"next Tuesday at 2pm"`, `"tomorrow morning"`, `"+2h"`) into precise RFC 3339 timestamps. 60+ expression patterns supported.
- **Timezone conversion**: DST-aware conversion between IANA timezones with offset and DST status reporting.
- **Duration computation**: Precise duration between two timestamps with days/hours/minutes breakdown.
- **Timestamp adjustment**: DST-aware adjustment (`"+1d"` across spring-forward = same wall-clock, not +24 hours).
- **RRULE expansion**: Converts recurrence rules (RFC 5545) into concrete event instances. Handles DST transitions, `BYSETPOS`, `EXDATE`, leap years, and cross-year boundaries correctly.
- **Availability merging**: Combines events from multiple calendars into a unified busy/free view with configurable privacy controls.
- **Conflict detection**: Determines whether a proposed time slot overlaps with existing events.

Truth Engine is open source and available as a standalone library: [truth-engine on crates.io](https://crates.io/crates/truth-engine), [npm](https://www.npmjs.com/package/@temporal-cortex/truth-engine), and [PyPI](https://pypi.org/project/temporal-cortex-toon/). 510+ Rust tests, ~9,000 property-based tests.

### TOON (Token-Oriented Object Notation)

A data format designed for LLM consumption. Calendar data encoded in TOON uses approximately 40% fewer tokens than equivalent JSON, reducing API costs and freeing context window space for the conversation.

TOON roundtrips perfectly — encode to TOON, decode back to the original data structure with zero loss. The MCP server offers TOON as an optional output format for `list_events`.

### Two-Phase Commit (Booking Safety)

When `book_slot` is called, the server follows a strict protocol:

1. **Prepare**: Acquire an exclusive lock on the time slot. Check the shadow calendar for any overlapping events or active holds.
2. **Commit**: If the slot is free, create the event in Google Calendar and record it in the shadow calendar.
3. **Abort**: If any step fails (lock acquisition, conflict detected, API error), release the lock and return an error.

This prevents double-booking even when multiple AI agents attempt to book the same time slot simultaneously.

### Content Sanitization

All user-provided text (event summaries, descriptions) passes through a prompt injection firewall before reaching the calendar API. This prevents malicious content from being written to the calendar via AI agents.

## Operating Modes

The server operates in two modes, auto-detected at startup:

### Lite Mode (Default)

Activated when `REDIS_URLS` is **not** set.

- **Locking**: In-memory lock manager (single-process safety)
- **Credentials**: Local file store at `~/.config/temporal-cortex/credentials.json`
- **Provider**: Google Calendar (single account)
- **Use case**: Individual developers, local AI assistants

### Full Mode

Activated when `REDIS_URLS` **is** set.

- **Locking**: Redis-based distributed locking (Redlock algorithm with 3-node quorum)
- **Credentials**: Enterprise credential management
- **Provider**: Multiple providers and accounts
- **Use case**: Production deployments, multi-agent environments

There is no manual mode flag — the server inspects the environment and selects the appropriate mode automatically.

## Transport Modes

The server supports two MCP transports, auto-detected at startup:

### Stdio (Default)

Standard MCP transport. The server reads JSON-RPC requests from stdin and writes responses to stdout. All logging goes to stderr to avoid interfering with the protocol transport.

### Streamable HTTP (when `HTTP_PORT` is set)

Per MCP 2025-11-25 spec. The server listens on `http://{HTTP_HOST}:{HTTP_PORT}/mcp` with SSE streaming, session management (`Mcp-Session-Id` header), and Origin validation. Requests with an invalid `Origin` header are rejected with HTTP 403.

## MCP Protocol

The server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification using the rmcp Rust crate. It registers 11 tools with JSON Schema parameter definitions that MCP clients use for tool calling.
