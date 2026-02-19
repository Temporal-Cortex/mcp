# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] - Unreleased

### Added

- Initial release of `@temporal-cortex/cortex-mcp`
- 6 MCP tools: `list_events`, `find_free_slots`, `book_slot`, `expand_rrule`, `check_availability`, `get_availability`
- Lite Mode: zero-infrastructure single Google Calendar setup
- Atomic booking with lock-verify-write conflict prevention via Two-Phase Commit
- TOON-compressed output (~40% fewer tokens than JSON)
- OAuth PKCE flow with local credential persistence
- Deterministic RRULE expansion via Truth Engine (DST-aware, BYSETPOS, leap years)
- RRULE Challenge CLI command for demonstrating edge case handling
