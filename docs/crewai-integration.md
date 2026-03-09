# CrewAI Integration Guide

Connect Temporal Cortex's deterministic calendar tools to CrewAI agents. This guide shows how to build scheduling crews that orient in time, query calendar availability, and book conflict-free meetings — using CrewAI's native MCP support.

## Why Temporal Cortex + CrewAI?

LLMs score below 50% on temporal reasoning tasks ([OOLONG benchmark](https://arxiv.org/abs/2511.02817)). Earlier models scored as low as 29% on scheduling and 13% on duration calculations ([Test of Time, ICLR 2025](https://arxiv.org/abs/2406.09170)). When your CrewAI scheduling agent asks "Am I free at 3pm?" it needs deterministic tools — not LLM inference.

Existing calendar integrations are basic CRUD wrappers against a single provider. Temporal Cortex provides:

- **Deterministic datetime resolution** — `resolve_datetime` turns "next Tuesday at 2pm" into a precise RFC 3339 timestamp. No hallucination.
- **Cross-provider availability merging** — Merges free/busy data across Google Calendar, Microsoft Outlook, and CalDAV into a single view.
- **Atomic booking** — Two-Phase Commit locks the time slot, verifies no conflicts, writes the event, then releases. No double-bookings.
- **RFC 5545 RRULE expansion** — Deterministic recurrence rule handling powered by [Truth Engine](https://github.com/temporal-cortex/core), not LLM inference.
- **Token-efficient output** — TOON format compresses calendar data by ~40% fewer tokens than JSON.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for stdio transport only — not needed for Platform Mode)
- **At least one calendar provider** configured:
  - [Google Calendar](google-cloud-setup.md) — OAuth credentials
  - [Microsoft Outlook](outlook-setup.md) — Azure AD app registration
  - [CalDAV](caldav-setup.md) — app-specific password (iCloud, Fastmail, etc.)

Install Python dependencies:

```bash
pip install crewai crewai-tools[mcp] python-dotenv
```

Authenticate with your calendar provider:

```bash
npx @temporal-cortex/cortex-mcp auth google
```

## Option 1: DSL Integration (Recommended)

The simplest way to connect Temporal Cortex to a CrewAI agent — use the `mcps` field directly on the agent:

```python
import os
from crewai import Agent, Crew, Process, Task
from crewai.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

temporal_cortex = MCPServerStdio(
    command="npx",
    args=["-y", "@temporal-cortex/cortex-mcp"],
    env={
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "TIMEZONE": os.getenv("TIMEZONE", ""),
    },
)

scheduler = Agent(
    role="Calendar Scheduling Assistant",
    goal="Schedule meetings using deterministic calendar tools",
    backstory=(
        "You always call get_temporal_context first to orient in time, "
        "then resolve_datetime for precise timestamps, list_calendars "
        "to discover providers, find_free_slots to check availability, "
        "and book_slot to book with Two-Phase Commit safety."
    ),
    mcps=[temporal_cortex],
    verbose=True,
)

task = Task(
    description="Schedule a 30-min Team Sync for next Tuesday at 2pm.",
    expected_output="Booking confirmation with calendar ID, title, start/end times.",
    agent=scheduler,
)

crew = Crew(agents=[scheduler], tasks=[task], process=Process.sequential, verbose=True)
result = crew.kickoff()
```

CrewAI auto-discovers all 18 Temporal Cortex tools from the MCP server. The agent's backstory guides it to call tools in the correct order.

## Option 2: MCPServerAdapter (Multi-Agent)

For more complex workflows, use `MCPServerAdapter` with multiple specialized agents:

```python
import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv

load_dotenv()

server_params = {
    "command": "npx",
    "args": ["-y", "@temporal-cortex/cortex-mcp"],
    "env": {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "TIMEZONE": os.getenv("TIMEZONE", ""),
    },
}

with MCPServerAdapter(server_params) as tools:
    temporal_analyst = Agent(
        role="Temporal Analyst",
        goal="Orient in time and resolve datetime expressions",
        backstory="You call get_temporal_context then resolve_datetime.",
        tools=tools, verbose=True,
    )

    calendar_manager = Agent(
        role="Calendar Manager",
        goal="Query calendars and find available slots",
        backstory="You call list_calendars then find_free_slots.",
        tools=tools, verbose=True,
    )

    coordinator = Agent(
        role="Scheduling Coordinator",
        goal="Book conflict-free meetings",
        backstory="You use book_slot with Two-Phase Commit safety.",
        tools=tools, verbose=True,
    )

    orient = Task(
        description="Get current time and resolve 'next Tuesday at 2pm'.",
        expected_output="Current time and resolved RFC 3339 timestamp.",
        agent=temporal_analyst,
    )
    find_slots = Task(
        description="Find available 30-min slots on the target date.",
        expected_output="Available slots with start/end in RFC 3339.",
        agent=calendar_manager, context=[orient],
    )
    book = Task(
        description="Book 'Team Sync' in the best available slot.",
        expected_output="Booking confirmation with event details.",
        agent=coordinator, context=[orient, find_slots],
    )

    crew = Crew(
        agents=[temporal_analyst, calendar_manager, coordinator],
        tasks=[orient, find_slots, book],
        process=Process.sequential, verbose=True,
    )
    result = crew.kickoff()
```

See the complete example with separate modules in [`examples/crewai/`](../examples/crewai/).

## Transport Options

### Local Mode (stdio — default)

Runs the MCP server locally via `npx`. No cloud account needed.

```python
from crewai.mcp import MCPServerStdio

temporal_cortex = MCPServerStdio(
    command="npx",
    args=["-y", "@temporal-cortex/cortex-mcp"],
    env={"TIMEZONE": "America/New_York"},
)
```

- Up to 18 tools available (Layers 0-4)
- Requires Node.js 18+ and local OAuth credentials
- In-memory locking (single-process safety)

### Platform Mode (SSE — managed)

Connects to the Temporal Cortex Platform at `mcp.temporal-cortex.com`. No Node.js required.

```python
from crewai.mcp import MCPServerSSE

temporal_cortex = MCPServerSSE(
    url="https://mcp.temporal-cortex.com/mcp",
    headers={"Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY')}"},
)
```

- 18 tools available (Layers 0-4, including Open Scheduling)
- Managed OAuth lifecycle — no local credentials
- Distributed locking for multi-agent safety
- Usage metering, content firewall, caller-based policies
- Get your API key from [app.temporal-cortex.com](https://app.temporal-cortex.com)

## Tool Layer Architecture

Temporal Cortex organizes 18 tools in 5 layers. Map agent roles to layers for effective multi-agent crews:

| Layer | Tools | Suggested Agent Role |
|-------|-------|---------------------|
| **0 — Discovery** | `resolve_identity`* | Identity Resolver |
| **1 — Temporal Context** | `get_temporal_context`, `resolve_datetime`, `convert_timezone`, `compute_duration`, `adjust_timestamp` | Temporal Analyst |
| **2 — Calendar Ops** | `list_calendars`, `list_events`, `find_free_slots`, `expand_rrule`, `check_availability` | Calendar Manager |
| **3 — Availability** | `get_availability`, `query_public_availability`* | Availability Analyst |
| **4 — Booking** | `book_slot`, `request_booking`* | Scheduling Coordinator |

*Platform Mode only

## Tips for Production

- **Always call `get_temporal_context` first** — encode this in the agent's backstory so it knows the current time before any calendar operation.
- **Use `format: "json"`** when agents need structured parsing. TOON is the default output (more token-efficient), but JSON is available via the `format` parameter on data tools.
- **Use Platform Mode for multi-agent coordination** — distributed locking prevents race conditions when multiple agents book simultaneously.
- **Set `verbose=True` during development** to see which tools each agent calls and in what order.
- **Agent backstories matter** — the backstory guides tool selection. Include specific tool names and the expected calling order.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `npx: command not found` | Install Node.js 18+ from [nodejs.org](https://nodejs.org) |
| `No credentials found` | Run `npx @temporal-cortex/cortex-mcp auth google` to authenticate |
| SSE connection timeout | Verify your API key is valid and the Platform endpoint is reachable |
| Agent calls wrong tools | Improve the agent's backstory — specify tool names and calling order |
| TOON output confusing agent | Pass `format: "json"` to data tools for structured JSON output |
| Tool names have prefix | `MCPServerAdapter` prepends server name to tool names — agent backstories should use unprefixed names (CrewAI handles mapping) |

## Learn More

- [Temporal Cortex MCP](https://github.com/temporal-cortex/mcp) — Full documentation and setup guides
- [Tool reference](tools.md) — Complete input/output schemas for all 18 tools
- [Architecture overview](architecture.md) — System design and request flow
- [Agent Skills](https://github.com/temporal-cortex/skills) — Procedural knowledge for calendar workflows
- [CrewAI MCP documentation](https://docs.crewai.com/en/mcp/overview) — CrewAI's MCP integration guide
