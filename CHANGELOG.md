# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.6] - 2026-02-28

### Fixed
- **npm-publish**: Fixed npm publish failure caused by `--provenance` flag (SLSA requires public source repos)

### Changed
- Version alignment with Platform v0.5.6 and Skills v0.5.6

## [0.5.5] - 2026-02-28

### Added
- **supply-chain**: SHA256 checksums (`SHA256SUMS.txt`) now attached to GitHub Releases

### Changed
- Version alignment with Skills v0.5.5 and Platform v0.5.5

## [0.5.4] - 2026-02-28

### Changed
- Version alignment with Skills v0.5.4 (ClawHub scanner remediation: runtime transparency, npx pinning, zero-setup rewording)

## [0.5.3] - 2026-02-28

### Changed
- Version alignment with Skills v0.5.3 (skill restructure: 4→3 skills, merged calendars+booking into scheduling)

## [0.5.2] - 2026-02-27

### Fixed
- Fixed MCP Registry OIDC namespace — `.mcp/server.json` name aligned to `io.github.temporal-cortex/mcp` matching lowercase GitHub org

### Changed
- GitHub org renamed from `Temporal-Cortex` to `temporal-cortex` (lowercase)

## [0.5.1] - 2026-02-27

### Changed
- **repo**: Migrated GitHub organization from `billylui/*` to `temporal-cortex/*` — all repository URLs, CHANGELOG comparison links, and cross-repo references updated
- Renamed "Cloud Mode" to "Temporal Cortex Platform" throughout documentation
- Updated Platform Mode description to emphasize full capability set (safety, metering, policies)
- Fixed FAQ link: replaced tally.so early access form with live app.temporal-cortex.com
- Replaced misattributed AuthenHallu citation with Test of Time (ICLR 2025) and OOLONG benchmarks for temporal reasoning accuracy claims

## [0.5.0] - 2026-02-26

### Added
- `list_calendars` tool (Layer 2) — lists all calendars across connected providers with provider-prefixed IDs, names, colors, and access roles
- `discover_calendars` MCP prompt template (4th prompt, joining `schedule_meeting`, `check_schedule`, `convert_time`)
- `cortex-mcp setup` wizard — guided first-run experience covering provider auth, timezone, week start, and MCP client configuration
- DST prediction in `get_temporal_context` — returns `next_dst_transition`, `next_dst_direction`, and `days_until_dst_transition`
- Comprehensive provider setup documentation:
  - [Microsoft Outlook setup guide](docs/outlook-setup.md) — Azure AD app registration with permissions and troubleshooting
  - [CalDAV setup guide](docs/caldav-setup.md) — iCloud app-specific password, Fastmail, and custom CalDAV server
  - [Configuration guide](docs/configuration-guide.md) — all environment variables, timezone, week start, multi-calendar, output format
  - [First Run Guide](docs/first-run-guide.md) — getting started in 5 minutes tutorial

### Changed
- TOON is now the default output format for all data tools (`list_calendars`, `list_events`, `find_free_slots`, `expand_rrule`, `get_availability`). JSON available via explicit `format: "json"`.
- Tool count increased from 11 to 12 (addition of `list_calendars`)
- Google Cloud setup guide expanded with detailed prerequisites, verification steps, additional troubleshooting scenarios, and revoking access instructions
- README updated to reference `cortex-mcp setup` as the primary installation path
- TOON claim standardized to "~40% fewer tokens" across all documentation
- Registry metadata (`.mcp/server.json`) updated to "12 deterministic calendar tools"

## [0.4.5] - 2026-02-25

### Added
- Tool annotations on all 11 tools — `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` for quality scoring and agent trust decisions
- 3 MCP prompt templates — `schedule_meeting`, `check_schedule`, `convert_time`
- 2 MCP resources — `cortex://docs/tool-usage-guide` and `cortex://docs/rrule-reference`
- ServerInfo display name, icon (SVG), description, and website URL
- Server instructions in `InitializeResult`

### Changed
- Server card updated with tool annotations, icon, and prompts/resources capabilities
- Improved `smithery.yaml` config schema — enum, examples, constraints, title, and description
- ServerCapabilities now advertises tools, prompts, and resources

## [0.4.4] - 2026-02-25

### Added
- MCP Server Card endpoint (`/.well-known/mcp/server-card.json`) for pre-connection tool discovery (SEP-1649) — enables Smithery and other registries to list all 11 tools without requiring authentication

## [0.4.3] - 2026-02-24

### Changed
- Version alignment with Agent Skill v0.4.3 (AEO description optimization — front-loaded action verbs, user-language triggers, ClawHub truncation resilience)

## [0.4.2] - 2026-02-24

### Changed
- Version alignment with Agent Skill v0.4.2 (OpenClaw scanner remediation — removed mislabeled `primaryEnv`, removed optional env vars from required list, added provenance metadata)
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

[Unreleased]: https://github.com/temporal-cortex/mcp/compare/v0.5.3...HEAD
[0.5.3]: https://github.com/temporal-cortex/mcp/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/temporal-cortex/mcp/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/temporal-cortex/mcp/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/temporal-cortex/mcp/compare/v0.4.5...v0.5.0
[0.4.5]: https://github.com/temporal-cortex/mcp/compare/v0.4.4...v0.4.5
[0.4.4]: https://github.com/temporal-cortex/mcp/compare/v0.4.3...v0.4.4
[0.4.3]: https://github.com/temporal-cortex/mcp/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/temporal-cortex/mcp/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/temporal-cortex/mcp/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/temporal-cortex/mcp/compare/v0.3.6...v0.4.0
[0.3.6]: https://github.com/temporal-cortex/mcp/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/temporal-cortex/mcp/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/temporal-cortex/mcp/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/temporal-cortex/mcp/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/temporal-cortex/mcp/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/temporal-cortex/mcp/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/temporal-cortex/mcp/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/temporal-cortex/mcp/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/temporal-cortex/mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/temporal-cortex/mcp/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/temporal-cortex/mcp/releases/tag/v0.1.1
