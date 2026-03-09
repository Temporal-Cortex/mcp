# OpenAI Agents SDK Integration Guide

Connect Temporal Cortex's deterministic calendar tools to OpenAI agents using `HostedMCPTool`. OpenAI handles the MCP connection server-side via the Responses API — no local MCP process, no Node.js, no infrastructure to manage.

## Why Temporal Cortex + OpenAI Agents SDK?

LLMs score below 50% on temporal reasoning tasks ([OOLONG benchmark](https://arxiv.org/abs/2511.02817)). Earlier models scored as low as 29% on scheduling and 13% on duration calculations ([Test of Time, ICLR 2025](https://arxiv.org/abs/2406.09170)). When your agent asks "Am I free at 3pm?" it needs deterministic tools — not LLM inference.

Existing calendar integrations are basic CRUD wrappers against a single provider. Temporal Cortex provides:

- **Deterministic datetime resolution** — `resolve_datetime` turns "next Tuesday at 2pm" into a precise RFC 3339 timestamp. No hallucination.
- **Cross-provider availability merging** — Merges free/busy data across Google Calendar, Microsoft Outlook, and CalDAV into a single view.
- **Atomic booking** — Two-Phase Commit locks the time slot, verifies no conflicts, writes the event, then releases. No double-bookings.
- **RFC 5545 RRULE expansion** — Deterministic recurrence rule handling powered by [Truth Engine](https://github.com/temporal-cortex/core), not LLM inference.
- **Token-efficient output** — TOON format compresses calendar data by ~40% fewer tokens than JSON.

## Prerequisites

- **Python 3.10+**
- **OpenAI API key** ([platform.openai.com](https://platform.openai.com/api-keys)) — requires access to the Responses API
- **Temporal Cortex Platform API key** ([app.temporal-cortex.com](https://app.temporal-cortex.com))

Install Python dependencies:

```bash
pip install openai-agents python-dotenv
```

## Quick Start: Single Agent

The simplest integration — a single agent with all 18 tools:

```python
import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, HostedMCPTool, Runner

load_dotenv()

temporal_cortex = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "temporal-cortex",
        "server_url": "https://mcp.temporal-cortex.com/mcp",
        "headers": {
            "Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY', '')}",
        },
        "require_approval": "never",
    }
)

agent = Agent(
    name="Calendar Scheduler",
    instructions=(
        "You schedule meetings using Temporal Cortex calendar tools.\n\n"
        "Follow this workflow:\n"
        "1. Call get_temporal_context to learn the current time and timezone\n"
        "2. Call resolve_datetime to convert human expressions to RFC 3339 timestamps\n"
        "3. Call list_calendars to discover connected calendars\n"
        "4. Call find_free_slots to check availability on the target date\n"
        "5. Call book_slot to book the meeting\n\n"
        "When calling data tools, pass format='json' for structured output.\n"
        "Always use provider-prefixed calendar IDs (e.g., google/primary)."
    ),
    tools=[temporal_cortex],
)

async def main():
    result = await Runner.run(
        agent,
        "Schedule a 30-minute Team Sync for next Tuesday at 2pm.",
    )
    print(result.final_output)

asyncio.run(main())
```

The agent auto-discovers all 18 tools from the MCP server. The instructions guide it to call tools in the correct order.

## Multi-Agent: Agent-as-Tool (Hub-and-Spoke)

For complex workflows, use the **Agent-as-Tool** pattern — a coordinator calls specialist sub-agents via `.as_tool()`:

```
Scheduling Coordinator (parent agent)
├── calls Temporal Analyst.as_tool()   → orient in time, resolve datetimes
├── calls Calendar Analyst.as_tool()   → find availability, check calendars
└── executes book_slot directly        → booking stays with coordinator
```

This is idiomatic for the OpenAI Agents SDK. The coordinator retains control and delegates narrow subtasks to specialists, rather than handing off the entire conversation.

```python
from agents import Agent, HostedMCPTool

temporal_cortex = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "temporal-cortex",
        "server_url": "https://mcp.temporal-cortex.com/mcp",
        "headers": {
            "Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY', '')}",
        },
        "require_approval": "never",
    }
)

temporal_analyst = Agent(
    name="Temporal Analyst",
    instructions=(
        "Call get_temporal_context to learn the current time, timezone, "
        "and DST status. Use resolve_datetime to convert human expressions "
        "to RFC 3339 timestamps. Pass format='json' to data tools."
    ),
    tools=[temporal_cortex],
)

calendar_analyst = Agent(
    name="Calendar Analyst",
    instructions=(
        "Call list_calendars to discover providers. Use find_free_slots "
        "to find available windows. Always use provider-prefixed calendar "
        "IDs. Pass format='json' to data tools."
    ),
    tools=[temporal_cortex],
)

coordinator = Agent(
    name="Scheduling Coordinator",
    instructions=(
        "Delegate time resolution to the Temporal Analyst and calendar "
        "queries to the Calendar Analyst. Then call book_slot directly "
        "to book the meeting. Never delegate booking to sub-agents."
    ),
    tools=[
        temporal_cortex,
        temporal_analyst.as_tool(
            tool_name="analyze_time",
            tool_description="Resolve datetime expressions into RFC 3339 timestamps.",
        ),
        calendar_analyst.as_tool(
            tool_name="analyze_calendars",
            tool_description="Discover calendars and find available time slots.",
        ),
    ],
)
```

See the complete example in [`examples/openai-agents/multi_agent.py`](../examples/openai-agents/multi_agent.py).

## Approval Workflows

Calendar booking is a sensitive action. Use `require_approval` to gate write operations while allowing read-only tools to run freely:

```python
temporal_cortex = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "temporal-cortex",
        "server_url": "https://mcp.temporal-cortex.com/mcp",
        "headers": {
            "Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY', '')}",
        },
        "require_approval": {
            "book_slot": "always",
            "request_booking": "always",
        },
    }
)
```

This maps to the MCP tool annotations where booking tools have `readOnlyHint: false`. The Responses API pauses execution and invokes your approval callback before the tool runs.

In production, wire the approval to a UI dialog, Slack message, or approval queue. See [`examples/openai-agents/human_in_the_loop.py`](../examples/openai-agents/human_in_the_loop.py).

## How HostedMCPTool Works

`HostedMCPTool` delegates the entire MCP round-trip to OpenAI's Responses API:

1. You declare the MCP server URL and auth headers
2. The Responses API connects to `mcp.temporal-cortex.com/mcp` using Streamable HTTP transport
3. It calls `tools/list` to discover available tools
4. The model invokes tools directly — no callbacks to your Python process
5. Tool results flow back into the model's context

This means no local MCP process, no `npx`, no Node.js runtime needed. The trade-off: you need an OpenAI API key with Responses API access, and the agent runs on OpenAI's infrastructure.

## Tool Layer Architecture

Temporal Cortex organizes 18 tools in 5 layers. Map agent roles to layers for effective multi-agent workflows:

| Layer | Tools | Suggested Agent Role |
|-------|-------|---------------------|
| **0 — Discovery** | `resolve_identity`* | Identity Resolver |
| **1 — Temporal Context** | `get_temporal_context`, `resolve_datetime`, `convert_timezone`, `compute_duration`, `adjust_timestamp` | Temporal Analyst |
| **2 — Calendar Ops** | `list_calendars`, `list_events`, `find_free_slots`, `expand_rrule`, `check_availability` | Calendar Manager |
| **3 — Availability** | `get_availability`, `query_public_availability`* | Availability Analyst |
| **4 — Booking** | `book_slot`, `request_booking`* | Scheduling Coordinator |

*Platform Mode only

## Tips for Production

- **Always call `get_temporal_context` first** — encode this in the agent instructions so it knows the current time before any calendar operation.
- **Use `format: "json"` in agent instructions** — TOON is the default output (more token-efficient), but OpenAI models may not understand the format. Tell agents to pass `format='json'` to data tools.
- **Use the Agent-as-Tool pattern for multi-agent** — the coordinator retains context across delegations. Handoffs lose the scheduling thread.
- **Gate booking tools with `require_approval`** — calendar writes are sensitive. Default to `"always"` for `book_slot` and `request_booking` in production.
- **Agent instructions matter** — include specific tool names and the expected calling order. The model uses instructions to decide which tools to call.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Verify your Temporal Cortex API key is valid at [app.temporal-cortex.com](https://app.temporal-cortex.com) |
| `HostedMCPTool` not available | Requires `openai-agents>=0.1.0` and Responses API access |
| TOON output confusing the model | Add `"pass format='json' to data tools"` in agent instructions |
| Too many tools in context | Use `allowed_tools` in the tool config to filter visible tools |
| Sub-agent not calling tools | Ensure sub-agents have `HostedMCPTool` in their `tools` list |
| Agent skips availability check | Add explicit step numbering in agent instructions |

## Learn More

- [Temporal Cortex MCP](https://github.com/temporal-cortex/mcp) — Full documentation and setup guides
- [Tool reference](tools.md) — Complete input/output schemas for all 18 tools
- [Architecture overview](architecture.md) — System design and request flow
- [Agent Skills](https://github.com/temporal-cortex/skills) — Procedural knowledge for calendar workflows
- [OpenAI Agents SDK documentation](https://openai.github.io/openai-agents-python/) — Official SDK reference
- [OpenAI MCP guide](https://developers.openai.com/cookbook/examples/mcp/mcp_tool_guide/) — General MCP tool patterns
