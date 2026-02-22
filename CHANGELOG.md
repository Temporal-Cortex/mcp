# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Replaced "Going to Production?" section with tiered "Ready for More?" CTA (no pricing amounts)
- Updated free tier description: 3 connected calendars, 50 bookings/month, all 11 tools

### Removed
- Removed "Comparison with Alternatives" table

## [0.2.1] - 2026-02-20

### Added
- `WEEK_START` env var — configure whether weeks start on Monday (ISO 8601, default) or Sunday
- Week start configuration in auth flow — prompted after timezone confirmation
- 16 compound period expressions: `"start of last week"`, `"end of next month"`, `"start of next quarter"`, etc.
- `get_temporal_context` now returns `week_start` field so AI agents know the user's preference

## [0.2.0] - 2026-02-20

### Added
- 5 new Layer 1 temporal context tools (total: 11 tools across 4 layers):
  - `get_temporal_context` — Current time, timezone, UTC offset, DST status, day of week
  - `resolve_datetime` — Parse human expressions ("next Tuesday at 2pm", "tomorrow morning", "+3h") to RFC 3339
  - `convert_timezone` — DST-aware timezone conversion between IANA timezones
  - `compute_duration` — Duration between two timestamps with days/hours/minutes breakdown
  - `adjust_timestamp` — DST-aware timestamp adjustment (compound format: `+1d2h30m`)
- Timezone configuration in auth flow — auto-detects OS timezone, prompts user to confirm
- `TIMEZONE` env var for session-level timezone override
- Streamable HTTP transport mode — set `HTTP_PORT` to serve MCP over HTTP with SSE streaming and session management
- Origin validation middleware (MCP 2025-11-25 §4.3) — rejects cross-origin requests with HTTP 403
- `HTTP_HOST` env var for configurable bind address (default: `127.0.0.1`)
- `ALLOWED_ORIGINS` env var for cross-origin allowlist

## [0.1.1] - 2026-02-18

### Added

- Initial release of `@temporal-cortex/cortex-mcp`
- 6 MCP tools: `list_events`, `find_free_slots`, `book_slot`, `expand_rrule`, `check_availability`, `get_availability`
- Lite Mode: zero-infrastructure single Google Calendar setup
- Atomic booking with lock-verify-write conflict prevention via Two-Phase Commit
- TOON-compressed output (~40% fewer tokens than JSON)
- OAuth PKCE flow with local credential persistence
- Deterministic RRULE expansion via Truth Engine (DST-aware, BYSETPOS, leap years)
- RRULE Challenge CLI command for demonstrating edge case handling

[Unreleased]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/billylui/temporal-cortex-mcp/releases/tag/v0.1.1
