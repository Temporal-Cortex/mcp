#!/usr/bin/env python3
"""
Temporal Cortex + CrewAI: DSL Integration (Simplest Approach)

Uses CrewAI's built-in mcps field on Agent for the most concise
integration. No MCPServerAdapter boilerplate needed.

Prerequisites:
  pip install crewai crewai-tools[mcp] python-dotenv
  npx @temporal-cortex/cortex-mcp auth google

Usage:
  cp .env.example .env
  python main_dsl.py
"""

import os

from crewai import Agent, Crew, Process, Task
from crewai.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

# Local Mode — runs the MCP server locally via npx
temporal_cortex = MCPServerStdio(
    command="npx",
    args=["-y", "@temporal-cortex/cortex-mcp"],
    env={
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "TIMEZONE": os.getenv("TIMEZONE", ""),
    },
)

# For Platform Mode (SSE — no local server), replace with:
# from crewai.mcp import MCPServerSSE
# temporal_cortex = MCPServerSSE(
#     url="https://mcp.temporal-cortex.com/mcp",
#     headers={"Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY')}"},
# )

scheduler = Agent(
    role="Calendar Scheduling Assistant",
    goal=(
        "Help users schedule meetings by checking current time, "
        "finding available slots, and booking conflict-free events"
    ),
    backstory=(
        "You are an expert scheduling assistant powered by Temporal "
        "Cortex. You always call get_temporal_context first to orient "
        "yourself in time — learning the current time, timezone, and "
        "DST status. You convert natural language times into precise "
        "timestamps using resolve_datetime. You discover calendars "
        "with list_calendars, check availability with find_free_slots, "
        "and book with book_slot (which uses Two-Phase Commit to "
        "prevent double-bookings). You never guess — you always use "
        "the tools."
    ),
    mcps=[temporal_cortex],
    verbose=True,
)

task = Task(
    description=(
        "Schedule a 30-minute 'Team Sync' meeting for next Tuesday "
        "at 2pm. First check the current time and timezone, then find "
        "available slots around that time, and finally book the meeting."
    ),
    expected_output=(
        "Confirmation of the booked meeting with calendar ID, title, "
        "start time, and end time in RFC 3339 format."
    ),
    agent=scheduler,
)

crew = Crew(
    agents=[scheduler],
    tasks=[task],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("SCHEDULING RESULT")
    print("=" * 60)
    print(result)
