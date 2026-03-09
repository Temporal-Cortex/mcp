# CrewAI Integration

Connect Temporal Cortex calendar tools to CrewAI agents using the native MCPServerAdapter. No wrapper needed — CrewAI's MCP support auto-discovers all Temporal Cortex tools.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for `npx` — stdio transport only)
- **At least one calendar provider** configured ([Google](../../docs/google-cloud-setup.md), [Outlook](../../docs/outlook-setup.md), or [CalDAV](../../docs/caldav-setup.md))
- **crewai** and **crewai-tools** with MCP support installed

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Authenticate with your calendar provider
npx @temporal-cortex/cortex-mcp auth google

# 3. Configure environment
cp .env.example .env
# Edit .env with your Google OAuth credentials

# 4. Run the example
python main.py
```

## What This Example Does

A 3-agent scheduling crew that mirrors Temporal Cortex's tool layer architecture:

| Agent | Role | Tools Used |
|-------|------|------------|
| **Temporal Analyst** | Orient in time | `get_temporal_context`, `resolve_datetime` (Layer 1) |
| **Calendar Manager** | Query calendars | `list_calendars`, `find_free_slots` (Layers 2-3) |
| **Scheduling Coordinator** | Book meetings | `check_availability`, `book_slot` (Layer 4) |

The crew follows the deterministic workflow: **orient → query → book**.

## Files

| File | Description |
|------|-------------|
| `main.py` | 3-agent crew with stdio transport (Local Mode — runs via npx) |
| `main_platform.py` | Same crew with SSE transport (Platform Mode — connects to mcp.temporal-cortex.com) |
| `main_dsl.py` | Simplest integration using CrewAI's DSL `mcps` field (~30 lines) |
| `agents.py` | Agent definitions with roles and backstories |
| `tasks.py` | Task definitions with context dependencies |
| `.env.example` | Environment variable template |
| `requirements.txt` | Python dependencies |

## Transport Options

| Transport | Mode | When to Use |
|-----------|------|-------------|
| **stdio** (default) | Local Mode | Development, individual use, no cloud account needed |
| **SSE** | Platform Mode | Production, teams, managed OAuth, distributed locking, 18 tools |

Stdio runs the MCP server locally via `npx`. SSE connects to the managed Platform at `mcp.temporal-cortex.com` — no Node.js required, but needs an API key from [app.temporal-cortex.com](https://app.temporal-cortex.com).

## Learn More

- [CrewAI integration guide](../../docs/crewai-integration.md)
- [Temporal Cortex tool reference](../../docs/tools.md)
- [Architecture overview](../../docs/architecture.md)
- [Agent Skills](https://github.com/temporal-cortex/skills)
