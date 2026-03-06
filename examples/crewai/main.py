#!/usr/bin/env python3
"""
Temporal Cortex + CrewAI: Multi-Agent Calendar Scheduling

A 3-agent crew that:
1. Orients in time (get_temporal_context, resolve_datetime)
2. Queries calendar availability (list_calendars, find_free_slots)
3. Books a conflict-free meeting (book_slot with Two-Phase Commit)

Transport: stdio (local npx — no cloud account needed)

Prerequisites:
  pip install -r requirements.txt
  npx @temporal-cortex/cortex-mcp auth google   # authenticate first

Usage:
  cp .env.example .env   # add your credentials
  python main.py
"""

import os

from crewai import Crew, Process
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv

from agents import (
    create_calendar_manager,
    create_scheduling_coordinator,
    create_temporal_analyst,
)
from tasks import (
    create_book_meeting_task,
    create_find_availability_task,
    create_orient_task,
)

load_dotenv()

# Stdio transport — runs the MCP server locally via npx.
# No cloud account needed. Authenticate first:
#   npx @temporal-cortex/cortex-mcp auth google
server_params = {
    "command": "npx",
    "args": ["-y", "@temporal-cortex/cortex-mcp"],
    "env": {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "TIMEZONE": os.getenv("TIMEZONE", ""),
    },
}


def main():
    with MCPServerAdapter(server_params) as tools:
        print(f"Discovered {len(tools)} Temporal Cortex tools")

        # Create agents — all share the same tool set.
        # Each agent's backstory guides it to use the right layer of tools.
        temporal_analyst = create_temporal_analyst(tools)
        calendar_manager = create_calendar_manager(tools)
        coordinator = create_scheduling_coordinator(tools)

        # Create tasks with dependencies (orient -> query -> book)
        orient_task = create_orient_task(temporal_analyst)
        availability_task = create_find_availability_task(
            calendar_manager, context=[orient_task]
        )
        booking_task = create_book_meeting_task(
            coordinator, context=[orient_task, availability_task]
        )

        crew = Crew(
            agents=[temporal_analyst, calendar_manager, coordinator],
            tasks=[orient_task, availability_task, booking_task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        print("\n" + "=" * 60)
        print("SCHEDULING RESULT")
        print("=" * 60)
        print(result)


if __name__ == "__main__":
    main()
