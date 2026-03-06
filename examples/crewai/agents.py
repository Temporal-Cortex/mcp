"""
Temporal Cortex CrewAI agent definitions.

Three specialized agents that mirror the tool layer architecture:
- Temporal Analyst  -> Layer 1 (temporal context)
- Calendar Manager  -> Layers 2-3 (calendar ops, availability)
- Scheduling Coordinator -> Layer 4 (booking)
"""

from crewai import Agent


def create_temporal_analyst(tools):
    """Agent that orients in time using Layer 1 tools."""
    return Agent(
        role="Temporal Analyst",
        goal=(
            "Establish temporal context by determining the current time, "
            "timezone, and DST status, then resolve any human datetime "
            "expressions into precise RFC 3339 timestamps"
        ),
        backstory=(
            "You are a time-awareness specialist. Before any calendar "
            "operation, you call get_temporal_context to learn the current "
            "time, timezone, UTC offset, and DST status. You convert "
            "natural language like 'next Tuesday at 2pm' into exact "
            "timestamps using resolve_datetime. You never guess dates "
            "or times — you always use the tools."
        ),
        tools=tools,
        verbose=True,
    )


def create_calendar_manager(tools):
    """Agent that queries calendars using Layers 2-3 tools."""
    return Agent(
        role="Calendar Manager",
        goal=(
            "Query connected calendars to list events, find free time "
            "slots, and check availability across all providers"
        ),
        backstory=(
            "You are a calendar operations specialist. You list calendars "
            "to discover connected providers (Google, Outlook, CalDAV), "
            "query events in time ranges, and find available slots using "
            "find_free_slots. You always use provider-prefixed calendar "
            "IDs (e.g., google/primary, outlook/work) and pass RFC 3339 "
            "timestamps from the Temporal Analyst. You never assume "
            "calendar IDs — you discover them first with list_calendars."
        ),
        tools=tools,
        verbose=True,
    )


def create_scheduling_coordinator(tools):
    """Agent that books meetings using Layer 4 tools."""
    return Agent(
        role="Scheduling Coordinator",
        goal=(
            "Coordinate the scheduling workflow: use temporal context and "
            "availability data to book a conflict-free meeting"
        ),
        backstory=(
            "You are the lead scheduler. You take the resolved timestamps "
            "from the Temporal Analyst and the available slots from the "
            "Calendar Manager to select the best meeting time. You use "
            "book_slot to create the event — this tool uses Two-Phase "
            "Commit to acquire a lock, verify no conflicts exist, write "
            "the event, then release the lock. You never double-book."
        ),
        tools=tools,
        verbose=True,
    )
