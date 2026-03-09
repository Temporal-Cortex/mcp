# LangGraph Integration Guide

Connect Temporal Cortex's deterministic calendar tools to LangGraph agents. This guide shows how to build scheduling agents that orient in time, query calendar availability, and book conflict-free meetings — using LangGraph's native graph control flow and `langchain-mcp-adapters` for MCP tool discovery.

## Why Temporal Cortex + LangGraph?

LangGraph gives you the orchestration graph. But your graph nodes still need **correct temporal computation** — and LLMs can't provide it.

Even the latest LLMs score below 50% on temporal reasoning tasks ([OOLONG benchmark](https://arxiv.org/abs/2511.02817)). Earlier models scored as low as 29% on scheduling and 13% on duration calculations ([Test of Time, ICLR 2025](https://arxiv.org/abs/2406.09170)). When your `StateGraph` node asks "Am I free at 3pm?" it needs deterministic tools — not LLM inference.

Existing calendar integrations are basic CRUD wrappers against a single provider. Temporal Cortex provides:

- **Deterministic datetime resolution** — `resolve_datetime` turns "next Tuesday at 2pm" into a precise RFC 3339 timestamp. No hallucination.
- **Cross-provider availability merging** — Merges free/busy data across Google Calendar, Microsoft Outlook, and CalDAV into a single view.
- **Atomic booking** — Two-Phase Commit locks the time slot, verifies no conflicts, writes the event, then releases. No double-bookings — even when parallel LangGraph nodes schedule simultaneously.
- **RFC 5545 RRULE expansion** — Deterministic recurrence rule handling powered by [Truth Engine](https://github.com/temporal-cortex/core), not LLM inference.
- **Token-efficient output** — TOON format compresses calendar data by ~40% fewer tokens than JSON, reducing costs and context window usage.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for stdio transport only — not needed for Platform Mode)
- **At least one calendar provider** configured:
  - [Google Calendar](google-cloud-setup.md) — OAuth credentials
  - [Microsoft Outlook](outlook-setup.md) — Azure AD app registration
  - [CalDAV](caldav-setup.md) — app-specific password (iCloud, Fastmail, etc.)

Install Python dependencies:

```bash
pip install langchain-mcp-adapters langgraph langchain-anthropic python-dotenv
```

Authenticate with your calendar provider:

```bash
npx @temporal-cortex/cortex-mcp auth google
```

## Quick Start: ReAct Agent

The simplest integration — a single ReAct agent with all 18 tools, using `MultiServerMCPClient` for MCP tool discovery:

```python
import asyncio
import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

model = ChatAnthropic(model="claude-sonnet-4-6")

SYSTEM_PROMPT = (
    "You schedule meetings using Temporal Cortex calendar tools.\n\n"
    "Follow this workflow:\n"
    "1. Call get_temporal_context to learn the current time and timezone\n"
    "2. Call resolve_datetime to convert human expressions to RFC 3339 timestamps\n"
    "3. Call list_calendars to discover connected calendars\n"
    "4. Call find_free_slots to check availability on the target date\n"
    "5. Call book_slot to book the meeting (Two-Phase Commit prevents double-bookings)\n\n"
    "When calling data tools (list_calendars, list_events, find_free_slots, "
    "expand_rrule, get_availability), pass format='json' for structured output.\n"
    "Always use provider-prefixed calendar IDs (e.g., google/primary).\n"
    "Never guess dates or times — always use the tools."
)

async def main():
    async with MultiServerMCPClient(
        {
            "temporal-cortex": {
                "command": "npx",
                "args": ["-y", "@temporal-cortex/cortex-mcp"],
                "env": {
                    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                    "TIMEZONE": os.getenv("TIMEZONE", ""),
                },
                "transport": "stdio",
            }
        }
    ) as client:
        tools = client.get_tools()
        agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)

        result = await agent.ainvoke(
            {"messages": [("user", "Schedule a 30-minute Team Sync for next Tuesday at 2pm.")]}
        )
        print(result["messages"][-1].content)

asyncio.run(main())
```

The `MultiServerMCPClient` launches the MCP server, discovers all 18 tools, and converts them into LangChain-compatible `StructuredTool` objects. The ReAct agent reasons over them automatically.

## Platform Mode (HTTP Transport)

Instead of running the MCP server locally, connect to the managed Temporal Cortex Platform. No Node.js or local OAuth credentials needed.

```python
async with MultiServerMCPClient(
    {
        "temporal-cortex": {
            "url": "https://mcp.temporal-cortex.com/mcp",
            "headers": {
                "Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY', '')}",
            },
            "transport": "streamable_http",
        }
    }
) as client:
    tools = client.get_tools()
    # Platform Mode discovers all 18 tools (including Open Scheduling)
    agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)
```

Get your API key from [app.temporal-cortex.com](https://app.temporal-cortex.com).

## Multi-Agent: StateGraph

For complex workflows, use a **StateGraph** with specialized nodes — this is idiomatic LangGraph. Each node is a scoped ReAct sub-agent, and the graph enforces the correct tool-calling order through explicit edges rather than LLM-driven routing.

```
temporal_analyst  →  calendar_manager  →  booking_coordinator  →  END
(Layer 1 tools)      (Layer 2 tools)      (Layer 4 tools)
```

```python
from typing import Annotated
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class SchedulingState(TypedDict):
    messages: Annotated[list, add_messages]
    temporal_context: str
    available_slots: str
    booking_result: str

async def temporal_analyst(state: SchedulingState, client) -> dict:
    tools = [t for t in client.get_tools() if t.name in {
        "get_temporal_context", "resolve_datetime",
        "convert_timezone", "compute_duration", "adjust_timestamp",
    }]
    agent = create_react_agent(model, tools, prompt="...")
    result = await agent.ainvoke({"messages": state["messages"]})
    context = result["messages"][-1].content
    return {
        "temporal_context": context,
        "messages": [AIMessage(content=f"[Temporal Analyst] {context}")],
    }

# calendar_manager and booking_coordinator follow the same pattern...

graph = StateGraph(SchedulingState)
graph.add_node("temporal_analyst", ...)
graph.add_node("calendar_manager", ...)
graph.add_node("booking_coordinator", ...)

graph.set_entry_point("temporal_analyst")
graph.add_edge("temporal_analyst", "calendar_manager")
graph.add_edge("calendar_manager", "booking_coordinator")
graph.add_edge("booking_coordinator", END)

app = graph.compile()
```

This differs from the [OpenAI Agents SDK example](../examples/openai-agents/) (Agent-as-Tool with LLM-driven routing) because LangGraph's explicit edges **guarantee** tools are called in the correct order. The LLM decides what to say, but the graph decides where to go next.

See the complete example in [`examples/langgraph/multi_agent.py`](../examples/langgraph/multi_agent.py).

## Human-in-the-Loop

Calendar booking is a sensitive action. Use LangGraph's `interrupt_before` to gate write operations while allowing read-only tools to run freely:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_react_agent(
    model,
    tools,
    prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
    interrupt_before=["tools"],
)

config = {"configurable": {"thread_id": "session-1"}}

# Start the workflow — runs until a tool call is pending
result = await agent.ainvoke(
    {"messages": [HumanMessage(content="Schedule a meeting...")]},
    config=config,
)

# Check if the pending tool is a write operation
pending_tool = result["messages"][-1].tool_calls[0]
if pending_tool["name"] in {"book_slot", "request_booking"}:
    # Pause for human approval
    approval = input("Approve? (y/n): ")
    if approval == "y":
        result = await agent.ainvoke(None, config=config)  # resume
```

This maps to the MCP tool annotations where booking tools have `readOnlyHint: false`. In production, wire the approval to a UI dialog, Slack message, or approval queue. Use `PostgresSaver` instead of `MemorySaver` for persistence across restarts.

See the complete example in [`examples/langgraph/human_in_the_loop.py`](../examples/langgraph/human_in_the_loop.py).

## Transport Options

### Local Mode (stdio — default)

Runs the MCP server locally via `npx`. No cloud account needed.

```python
{
    "temporal-cortex": {
        "command": "npx",
        "args": ["-y", "@temporal-cortex/cortex-mcp"],
        "env": {"TIMEZONE": "America/New_York"},
        "transport": "stdio",
    }
}
```

- Up to 18 tools available (Layers 0-4)
- Requires Node.js 18+ and local OAuth credentials
- In-memory locking (single-process safety)

### Platform Mode (HTTP — managed)

Connects to the Temporal Cortex Platform at `mcp.temporal-cortex.com`. No Node.js required.

```python
{
    "temporal-cortex": {
        "url": "https://mcp.temporal-cortex.com/mcp",
        "headers": {"Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY')}"},
        "transport": "streamable_http",
    }
}
```

- 18 tools available (Layers 0-4, including Open Scheduling)
- Managed OAuth lifecycle — no local credentials
- Distributed locking for multi-agent safety
- Usage metering, content firewall, caller-based policies
- Get your API key from [app.temporal-cortex.com](https://app.temporal-cortex.com)

## Tool Layer Architecture

Temporal Cortex organizes 18 tools in 5 layers. Map `StateGraph` nodes to layers for effective multi-agent workflows:

| Layer | Tools | Suggested Node Role |
|-------|-------|---------------------|
| **0 — Discovery** | `resolve_identity`* | Identity Resolver |
| **1 — Temporal Context** | `get_temporal_context`, `resolve_datetime`, `convert_timezone`, `compute_duration`, `adjust_timestamp` | Temporal Analyst |
| **2 — Calendar Ops** | `list_calendars`, `list_events`, `find_free_slots`, `expand_rrule`, `check_availability` | Calendar Manager |
| **3 — Availability** | `get_availability`, `query_public_availability`* | Availability Analyst |
| **4 — Booking** | `book_slot`, `request_booking`* | Booking Coordinator |

*Platform Mode only

## Tips for Production

- **Always call `get_temporal_context` first** — encode this in the system prompt so the agent knows the current time before any calendar operation.
- **Use `format: "json"` in system prompts** — TOON is the default output (more token-efficient), but some models may need structured JSON. Tell agents to pass `format='json'` to data tools.
- **Use Platform Mode for multi-agent graphs** — distributed locking prevents race conditions when parallel `StateGraph` nodes book simultaneously.
- **Use `PostgresSaver` in production** — `MemorySaver` is for development only. Postgres checkpoints enable time-travel debugging, persistence across restarts, and human-in-the-loop workflows.
- **System prompts matter** — include specific tool names and the expected calling order. The model uses these instructions to decide which tools to call and when.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `npx: command not found` | Install Node.js 18+ from [nodejs.org](https://nodejs.org) |
| `No credentials found` | Run `npx @temporal-cortex/cortex-mcp auth google` to authenticate |
| `401 Unauthorized` (Platform) | Verify your API key is valid at [app.temporal-cortex.com](https://app.temporal-cortex.com) |
| Agent calls wrong tools | Improve the system prompt — specify tool names and calling order |
| TOON output confusing agent | Pass `format: "json"` to data tools for structured JSON output |
| Session timeout (HTTP) | `MultiServerMCPClient` handles reconnection automatically; check network connectivity |
| `StructuredTool` sync invoke error | Use `ainvoke()` — `langchain-mcp-adapters` tools are async-only |

## Learn More

- [Temporal Cortex MCP](https://github.com/temporal-cortex/mcp) — Full documentation and setup guides
- [Tool reference](tools.md) — Complete input/output schemas for all 18 tools
- [Architecture overview](architecture.md) — System design and request flow
- [Agent Skills](https://github.com/temporal-cortex/skills) — Procedural knowledge for calendar workflows
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/) — Official LangGraph reference
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) — MCP tool bridge for LangChain/LangGraph
- [LangSmith Hub prompt](https://smith.langchain.com/hub/temporal-cortex/calendar-scheduling-agent) — Reusable scheduling agent system prompt
