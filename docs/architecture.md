# Architecture

High-level overview of how the Temporal Cortex MCP server works.

## Overview

The MCP server is a single Rust binary that communicates with AI clients (Claude Desktop, Cursor, Windsurf) over **stdio** — the standard MCP transport protocol. It runs locally on your machine as a child process of the MCP client.

```
┌─────────────────┐     stdio      ┌─────────────────┐     HTTPS     ┌──────────────┐
│   MCP Client    │ ◄────────────► │   cortex-mcp    │ ◄──────────► │ Google       │
│ (Claude Desktop,│                │   (Rust binary)  │              │ Calendar API │
│  Cursor, etc.)  │                └─────────────────┘              └──────────────┘
└─────────────────┘
```

## Distribution

The binary is distributed via npm as `@temporal-cortex/cortex-mcp`. When you run `npx @temporal-cortex/cortex-mcp`, npm downloads the correct platform-specific binary (macOS ARM64/x64, Linux x64/ARM64, Windows x64) via optional dependencies.

This means no Rust toolchain is required — `npx` handles everything.

## Key Components

### Truth Engine

Handles all date and time computation deterministically:

- **RRULE expansion**: Converts recurrence rules (RFC 5545) into concrete event instances. Handles DST transitions, `BYSETPOS`, `EXDATE`, leap years, and cross-year boundaries correctly.
- **Availability merging**: Combines events from multiple calendars into a unified busy/free view with configurable privacy controls.
- **Conflict detection**: Determines whether a proposed time slot overlaps with existing events.

Truth Engine is open source and available as a standalone library: [truth-engine on crates.io](https://crates.io/crates/truth-engine), [npm](https://www.npmjs.com/package/@temporal-cortex/truth-engine), and [PyPI](https://pypi.org/project/temporal-cortex-toon/).

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

## MCP Protocol

The server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification using the rmcp Rust crate. It registers 6 tools with JSON Schema parameter definitions that MCP clients use for tool calling.

Communication is over stdio (stdin/stdout). The server reads JSON-RPC requests from stdin and writes responses to stdout. All logging goes to stderr to avoid interfering with the protocol transport.
