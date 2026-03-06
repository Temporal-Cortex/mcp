#!/usr/bin/env python3
"""
Temporal Cortex + OpenAI Agents SDK: Human-in-the-Loop Approval

Demonstrates fine-grained approval gates for calendar booking.
Read-only tools (temporal context, calendar queries) run freely,
while write operations (book_slot, request_booking) require
explicit human approval before execution.

This maps to the MCP tool annotations where booking tools have
readOnlyHint: false (they modify calendar state).

Prerequisites:
  pip install -r requirements.txt
  Sign up at app.temporal-cortex.com, connect a calendar, and generate an API key

Usage:
  cp .env.example .env   # add your API keys
  python human_in_the_loop.py
"""

import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, HostedMCPTool, Runner

load_dotenv()

# Fine-grained approval: only booking tools require human sign-off.
# All read-only tools (get_temporal_context, list_calendars,
# find_free_slots, etc.) execute without interruption.
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

agent = Agent(
    name="Calendar Scheduler",
    instructions=(
        "You schedule meetings using Temporal Cortex calendar tools.\n\n"
        "Follow this workflow:\n"
        "1. Call get_temporal_context to learn the current time and timezone\n"
        "2. Call resolve_datetime to convert human expressions to RFC 3339 timestamps\n"
        "3. Call list_calendars to discover connected calendars\n"
        "4. Call find_free_slots to check availability on the target date\n"
        "5. Present the available slots and your recommendation to the user\n"
        "6. Call book_slot to book (requires human approval)\n\n"
        "When calling data tools (list_calendars, list_events, find_free_slots, "
        "expand_rrule, get_availability), pass format='json' for structured output.\n"
        "Always use provider-prefixed calendar IDs (e.g., google/primary).\n"
        "Never guess dates or times — always use the tools."
    ),
    tools=[temporal_cortex],
)


async def main():
    # When the agent calls book_slot or request_booking, the Runner
    # pauses and invokes the approval callback. In a production app,
    # you would wire this to a UI confirmation dialog, Slack message,
    # or approval queue.
    result = await Runner.run(
        agent,
        "Schedule a 30-minute Team Sync for next Tuesday at 2pm.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
