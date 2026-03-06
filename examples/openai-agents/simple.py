#!/usr/bin/env python3
"""
Temporal Cortex + OpenAI Agents SDK: Minimal Example

Connects to the Temporal Cortex Platform via HostedMCPTool to schedule
a meeting using deterministic calendar tools. OpenAI handles the MCP
connection server-side — no local MCP process needed.

Prerequisites:
  pip install -r requirements.txt
  Sign up at app.temporal-cortex.com and generate an API key

Usage:
  cp .env.example .env   # add your API keys
  python simple.py
"""

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
        "5. Call book_slot to book the meeting (Two-Phase Commit prevents double-bookings)\n\n"
        "When calling data tools (list_calendars, list_events, find_free_slots, "
        "expand_rrule, get_availability), pass format='json' for structured output.\n"
        "Always use provider-prefixed calendar IDs (e.g., google/primary).\n"
        "Never guess dates or times — always use the tools."
    ),
    tools=[temporal_cortex],
)


async def main():
    result = await Runner.run(
        agent,
        "Schedule a 30-minute Team Sync for next Tuesday at 2pm.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
