# LangGraph Integration

Connect Temporal Cortex calendar tools to LangGraph agents using `langchain-mcp-adapters`. LangGraph auto-discovers all Temporal Cortex tools via MCP — no wrapper needed.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for `npx` — stdio transport only, not needed for Platform Mode)
- **At least one calendar provider** configured ([Google](../../docs/google-cloud-setup.md), [Outlook](../../docs/outlook-setup.md), or [CalDAV](../../docs/caldav-setup.md))
- **Anthropic API key** ([console.anthropic.com](https://console.anthropic.com/))

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Authenticate with your calendar provider
npx @temporal-cortex/cortex-mcp auth google

# 3. Configure environment
cp .env.example .env
# Edit .env with your Anthropic API key and calendar credentials

# 4. Run the example
python simple.py
```

## What These Examples Do

Four examples demonstrating different LangGraph integration patterns:

| Example | Pattern | Description |
|---------|---------|-------------|
| `simple.py` | ReAct agent | Minimal scheduling agent with stdio transport (~70 lines) |
| `simple_platform.py` | ReAct agent | Same agent with HTTP transport — no Node.js needed |
| `multi_agent.py` | StateGraph | Three specialized nodes with deterministic routing |
| `human_in_the_loop.py` | Interrupt | Booking approval via LangGraph's `interrupt_before` |

## Files

| File | Description |
|------|-------------|
| `simple.py` | Single ReAct agent with all 18 tools — orient, query, book |
| `simple_platform.py` | Same agent connecting to managed Platform at `mcp.temporal-cortex.com` |
| `multi_agent.py` | StateGraph: Temporal Analyst → Calendar Manager → Booking Coordinator |
| `human_in_the_loop.py` | Read-only tools auto-proceed; booking pauses for human approval |
| `.env.example` | Environment variable template |
| `requirements.txt` | Python dependencies |

## Agent Architecture

The `multi_agent.py` example uses a **StateGraph** with deterministic routing, which is idiomatic for LangGraph:

```
temporal_analyst  →  calendar_manager  →  booking_coordinator  →  END
(Layer 1 tools)      (Layer 2 tools)      (Layer 4 tools)
```

Each node is a scoped ReAct sub-agent. The graph guarantees the correct tool-calling order (orient → query → book) through explicit edges rather than LLM-driven routing.

This differs from the [OpenAI Agents SDK example](../openai-agents/) (which uses Agent-as-Tool with LLM-driven routing) and the [CrewAI example](../crewai/) (which uses a sequential crew process).

## Human-in-the-Loop

Calendar booking is a sensitive action. The `human_in_the_loop.py` example uses LangGraph's `interrupt_before` to gate write operations:

- Read-only tools (`get_temporal_context`, `list_calendars`, `find_free_slots`, etc.) execute automatically
- Write tools (`book_slot`, `request_booking`) pause the graph for human approval
- This maps directly to the MCP tool annotations where booking tools have `readOnlyHint: false`

In production, wire the approval to a UI dialog, Slack message, or approval queue. Use `PostgresSaver` instead of `MemorySaver` for persistence across restarts.

## Learn More

- [LangGraph integration guide](../../docs/langgraph-integration.md)
- [Temporal Cortex tool reference](../../docs/tools.md)
- [Architecture overview](../../docs/architecture.md)
- [Agent Skills](https://github.com/temporal-cortex/skills)
- [LangSmith Hub prompt](https://smith.langchain.com/hub/temporal-cortex/calendar-scheduling-agent)
