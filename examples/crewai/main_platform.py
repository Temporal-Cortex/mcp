#!/usr/bin/env python3
"""
Temporal Cortex + CrewAI: Platform Mode (SSE Transport)

Same 3-agent crew as main.py, but connects to the managed
Temporal Cortex Platform instead of running locally.

Benefits over Local Mode:
  - No Node.js or npx required
  - No local OAuth credentials to manage
  - Multi-agent coordination with distributed locking
  - Usage metering and content firewall
  - 3 additional Open Scheduling tools (15 total)

Prerequisites:
  pip install -r requirements.txt
  Sign up at app.temporal-cortex.com and generate an API key

Usage:
  cp .env.example .env   # add your API key
  python main_platform.py
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

# SSE transport — connects to the managed Temporal Cortex Platform.
# No local server process, no Node.js required.
# Get your API key from app.temporal-cortex.com
server_params = {
    "url": "https://mcp.temporal-cortex.com/mcp",
    "transport": "sse",
    "headers": {
        "Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY', '')}",
    },
}


def main():
    with MCPServerAdapter(server_params) as tools:
        # Platform Mode discovers all 15 tools (including Open Scheduling)
        print(f"Discovered {len(tools)} Temporal Cortex tools")

        temporal_analyst = create_temporal_analyst(tools)
        calendar_manager = create_calendar_manager(tools)
        coordinator = create_scheduling_coordinator(tools)

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
