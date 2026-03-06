#!/usr/bin/env python3
"""
Temporal Cortex + OpenAI Agents SDK: Multi-Agent (Agent-as-Tool)

Hub-and-spoke architecture where a Scheduling Coordinator orchestrates
two specialist sub-agents:
  - Temporal Analyst: orients in time, resolves human datetime expressions
  - Calendar Analyst: queries calendars, finds available slots

The coordinator calls sub-agents via .as_tool() and retains control of
booking (write operations) for accountability.

This pattern is idiomatic for the OpenAI Agents SDK — the coordinator
uses LLM-driven routing to decide when to delegate, rather than a
fixed sequential process.

Prerequisites:
  pip install -r requirements.txt
  Sign up at app.temporal-cortex.com, connect a calendar, and generate an API key

Usage:
  cp .env.example .env   # add your API keys
  python multi_agent.py
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

# --- Sub-agents (called as tools by the coordinator) ---

temporal_analyst = Agent(
    name="Temporal Analyst",
    instructions=(
        "You are a time-awareness specialist. Your job:\n"
        "1. Call get_temporal_context to learn the current time, timezone, "
        "UTC offset, and DST status\n"
        "2. Call resolve_datetime to convert human expressions like "
        "'next Tuesday at 2pm' into precise RFC 3339 timestamps\n"
        "3. Call convert_timezone if cross-timezone conversion is needed\n\n"
        "Always pass format='json' to data tools. Never guess dates or "
        "times — always use the tools."
    ),
    tools=[temporal_cortex],
)

calendar_analyst = Agent(
    name="Calendar Analyst",
    instructions=(
        "You are a calendar operations specialist. Your job:\n"
        "1. Call list_calendars to discover connected providers and calendar IDs\n"
        "2. Call find_free_slots to find available time windows\n"
        "3. Call check_availability to verify specific time ranges\n\n"
        "Always use provider-prefixed calendar IDs (e.g., google/primary, "
        "outlook/work). Always pass format='json' to data tools. "
        "Never assume calendar IDs — discover them first with list_calendars."
    ),
    tools=[temporal_cortex],
)

# --- Coordinator (parent agent) ---

coordinator = Agent(
    name="Scheduling Coordinator",
    instructions=(
        "You coordinate calendar scheduling by delegating to specialists:\n\n"
        "1. Ask the Temporal Analyst to orient in time and resolve any "
        "datetime expressions into RFC 3339 timestamps\n"
        "2. Ask the Calendar Analyst to discover calendars and find "
        "available time slots on the target date\n"
        "3. Select the best slot and call book_slot directly to book "
        "the meeting (Two-Phase Commit prevents double-bookings)\n\n"
        "When calling book_slot, pass format='json' for structured output. "
        "Always include: calendar_id, title, start (RFC 3339), "
        "duration_minutes. Never delegate booking to sub-agents — "
        "write operations stay with you for accountability."
    ),
    tools=[
        temporal_cortex,
        temporal_analyst.as_tool(
            tool_name="analyze_time",
            tool_description=(
                "Determine current time/timezone and resolve human datetime "
                "expressions into precise RFC 3339 timestamps."
            ),
        ),
        calendar_analyst.as_tool(
            tool_name="analyze_calendars",
            tool_description=(
                "Discover connected calendars and find available time slots "
                "on a given date."
            ),
        ),
    ],
)


async def main():
    result = await Runner.run(
        coordinator,
        "Schedule a 30-minute Team Sync for next Tuesday at 2pm.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
