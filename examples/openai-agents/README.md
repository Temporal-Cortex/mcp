# OpenAI Agents SDK Integration

Connect Temporal Cortex calendar tools to OpenAI agents using `HostedMCPTool`. OpenAI handles the MCP connection server-side via the Responses API — no local MCP process needed.

## Prerequisites

- **Python 3.10+**
- **OpenAI API key** ([platform.openai.com](https://platform.openai.com/api-keys))
- **Temporal Cortex Platform API key** ([app.temporal-cortex.com](https://app.temporal-cortex.com))

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI and Temporal Cortex API keys

# 3. Run the example
python simple.py
```

## What These Examples Do

Three examples demonstrating different integration patterns:

| Example | Pattern | Description |
|---------|---------|-------------|
| `simple.py` | Single agent | Minimal scheduling agent (~60 lines) |
| `multi_agent.py` | Agent-as-Tool | Coordinator orchestrates specialist sub-agents |
| `human_in_the_loop.py` | Approval gates | Fine-grained `require_approval` for booking tools |

All examples connect to the managed Temporal Cortex Platform at `mcp.temporal-cortex.com` — no Node.js, no local OAuth credentials, no infrastructure to manage.

## Files

| File | Description |
|------|-------------|
| `simple.py` | Single agent with all 15 tools — orient, query, book |
| `multi_agent.py` | Hub-and-spoke pattern: coordinator calls Temporal Analyst and Calendar Analyst as tools |
| `human_in_the_loop.py` | Approval workflow for write tools (`book_slot`, `request_booking`) |
| `.env.example` | Environment variable template |
| `requirements.txt` | Python dependencies |

## Agent Architecture

The `multi_agent.py` example uses the **Agent-as-Tool** pattern (hub-and-spoke), which is idiomatic for the OpenAI Agents SDK:

```
Scheduling Coordinator (parent agent)
├── calls Temporal Analyst.as_tool()   → orient in time, resolve datetimes
├── calls Calendar Analyst.as_tool()   → find availability, check calendars
└── executes book_slot directly        → booking stays with coordinator
```

The coordinator holds the `HostedMCPTool` and delegates temporal/calendar queries to sub-agents via `.as_tool()`. Booking stays with the coordinator because it is a write operation requiring full context.

This differs from the [CrewAI example](../crewai/) (which uses a sequential process) because the OpenAI SDK uses LLM-driven routing rather than explicit state machines.

## Approval Workflows

Calendar booking is a sensitive action. The `human_in_the_loop.py` example shows how to gate write operations:

```python
"require_approval": {
    "book_slot": "always",        # Two-Phase Commit booking
    "request_booking": "always",  # Open Scheduling booking request
}
```

Read-only tools (`get_temporal_context`, `list_calendars`, `find_free_slots`, etc.) run without approval. This maps directly to the MCP tool annotations where booking tools have `readOnlyHint: false`.

## Learn More

- [OpenAI Agents SDK integration guide](../../docs/openai-agents-integration.md)
- [Temporal Cortex tool reference](../../docs/tools.md)
- [Architecture overview](../../docs/architecture.md)
- [Agent Skills](https://github.com/temporal-cortex/skills)
