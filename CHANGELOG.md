# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **ci**: Added Dependabot Docker ecosystem tracking for `debian:trixie-slim` base image in Dockerfile
- **ci**: Added Dependabot auto-merge workflow — auto-approves and merges patch updates after CI passes

## [0.4.1] - 2026-02-23

### Changed
- Version alignment with Agent Skill v0.4.1 (OpenClaw scanner remediation — removed over-broad OAuth credential requirements from metadata)

## [0.4.0] - 2026-02-23

### Added
- Cloud mode support — hosted MCP endpoint at mcp.temporal-cortex.com with Bearer token authentication

## [0.3.6] - 2026-02-23

### Changed
- Version alignment with Agent Skill v0.3.6 (OpenClaw scanner metadata remediation)

## [0.3.5] - 2026-02-23

### Security
- Improved `GOOGLE_CLIENT_SECRET` description in registry metadata to clarify conditional requirement

### Changed
- Version bump for OpenClaw scanner remediation alignment

## [0.3.4] - 2026-02-23

### Security
- Pinned npm package version in all client configuration examples for supply chain auditability

### Added
- `MICROSOFT_CLIENT_SECRET`, `GOOGLE_OAUTH_CREDENTIALS`, `REDIS_URLS` to `.mcp/server.json` registry metadata
- `MICROSOFT_CLIENT_SECRET` to README configuration and troubleshooting tables
- Microsoft Outlook and week start config to `smithery.yaml`

### Changed
- Renamed `OUTLOOK_CLIENT_ID` → `MICROSOFT_CLIENT_ID` and `OUTLOOK_CLIENT_SECRET` → `MICROSOFT_CLIENT_SECRET` in MCP server code (backward-compatible: old names still work with deprecation warning)

## [0.3.3] - 2026-02-22

### Security
- Fixed shell injection vulnerability in Agent Skill configure script

### Changed
- Version alignment with Agent Skill v0.3.3

## [0.3.2] - 2026-02-22

### Changed
- Interactive onboarding UX — timezone selection now uses a fuzzy-search picker (597 IANA zones, arrow-key navigation) instead of free-text input
- Week start configuration uses arrow-key selection (Monday/Sunday) instead of free-text input
- Warmer telemetry consent messaging with interactive confirm prompt

## [0.3.1] - 2026-02-22

### Added
- Anonymous telemetry with first-run opt-in consent — collects tool names, success/error status, platform, and version only
- `TEMPORAL_CORTEX_TELEMETRY` env var (`off`/`on`) to control telemetry without editing config files
- Consent prompt during `cortex-mcp auth` setup flows

## [0.3.0] - 2026-02-22

### Added
- **Multi-calendar provider support** — connect Google, Outlook, and CalDAV (iCloud, Fastmail) calendars simultaneously
- `cortex-mcp auth outlook` — Azure AD OAuth2 setup for Microsoft calendars
- `cortex-mcp auth caldav` — Interactive CalDAV setup with iCloud and Fastmail presets
- Provider-prefixed calendar IDs — `"google/primary"`, `"outlook/work"`, `"caldav/personal"` routing
- Multi-provider `get_availability` — unified busy/free view across all connected calendars
- Dormant guardrails module — rate limiter and booking cap ready for managed cloud (zero overhead in Local Mode)

### Changed
- Replaced "Going to Production?" section with tiered "Ready for More?" CTA (no pricing amounts)
- Updated free tier description: 3 connected calendars, 50 bookings/month, all 11 tools

### Removed
- Removed "Comparison with Alternatives" table

## [0.2.2] - 2026-02-22

### Fixed
- Fixed stdio transport immediately terminating after `initialize` — the MCP server now stays alive for the full session instead of exiting after the first handshake. All stdio-based MCP clients (Claude Desktop, Cursor, etc.) were affected.

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

[Unreleased]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.6...v0.4.0
[0.3.6]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/billylui/temporal-cortex-mcp/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/billylui/temporal-cortex-mcp/releases/tag/v0.1.1
