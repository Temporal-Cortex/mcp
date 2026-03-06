"""
Temporal Cortex CrewAI task definitions.

Tasks follow the orient-resolve-query-book workflow that mirrors
the MCP server's tool layer architecture.
"""

from crewai import Task


def create_orient_task(agent):
    """Task 1: Orient in time (Layer 1)."""
    return Task(
        description=(
            "Get the current temporal context: call get_temporal_context "
            "to learn the current time, timezone, UTC offset, and DST "
            "status. Then resolve the meeting time expression "
            "'next Tuesday at 2pm' into a precise RFC 3339 timestamp "
            "using resolve_datetime."
        ),
        expected_output=(
            "The current local time, timezone, DST status, and the "
            "resolved RFC 3339 timestamp for 'next Tuesday at 2pm'."
        ),
        agent=agent,
    )


def create_find_availability_task(agent, context):
    """Task 2: Find available slots (Layers 2-3)."""
    return Task(
        description=(
            "Using the resolved timestamp from the previous task, "
            "find available time slots on the target date. First call "
            "list_calendars to discover connected providers and their "
            "calendar IDs. Then call find_free_slots for the primary "
            "calendar on the target date to find 30-minute available "
            "windows. Report all available slots."
        ),
        expected_output=(
            "A list of connected calendars and available 30-minute time "
            "slots on the target date, with start/end times in RFC 3339 "
            "format and the calendar ID to use for booking."
        ),
        agent=agent,
        context=context,
    )


def create_book_meeting_task(agent, context):
    """Task 3: Book the meeting (Layer 4)."""
    return Task(
        description=(
            "From the available slots found in the previous task, "
            "select the slot closest to 2pm and book a 30-minute meeting "
            "titled 'Team Sync'. Use the book_slot tool with the "
            "calendar ID from the Calendar Manager. The book_slot tool "
            "uses Two-Phase Commit to prevent double-bookings."
        ),
        expected_output=(
            "Confirmation that the meeting was booked, including the "
            "calendar ID, event title, start time, and end time."
        ),
        agent=agent,
        context=context,
    )
