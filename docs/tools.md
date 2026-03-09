# Tool Reference

Complete reference for the up to 18 MCP tools provided by `@temporal-cortex/cortex-mcp`. The 15 core tools are always available; 3 additional Open Scheduling tools are available in Platform Mode.

All datetime parameters use [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) format (e.g., `2026-03-15T14:00:00Z` or `2026-03-15T10:00:00-04:00`).

These tools are available over both **stdio** (default) and **streamable HTTP** transports. Set `HTTP_PORT` to enable HTTP mode. See the main [README](../README.md) for transport configuration.

## Tool Annotations

[MCP tool annotations](https://modelcontextprotocol.io/specification/2025-03-26/server/tools#annotations) describe the behavior profile of each tool, helping clients make informed decisions about tool approval and safety.

| Tool | `readOnlyHint` | `destructiveHint` | `idempotentHint` | `openWorldHint` |
|------|:-:|:-:|:-:|:-:|
| `get_temporal_context` | true | false | true | false |
| `resolve_datetime` | true | false | true | false |
| `convert_timezone` | true | false | true | false |
| `compute_duration` | true | false | true | false |
| `adjust_timestamp` | true | false | true | false |
| `list_calendars` | true | false | true | true |
| `list_events` | true | false | true | true |
| `find_free_slots` | true | false | true | true |
| `book_slot` | **false** | false | **false** | true |
| `expand_rrule` | true | false | true | false |
| `check_availability` | true | false | true | true |
| `get_availability` | true | false | true | true |
| `resolve_identity` | true | false | true | true |
| `query_public_availability` | true | false | true | true |
| `request_booking` | **false** | false | **false** | true |

- **`book_slot`** and **`request_booking`** are the tools that modify external state (create calendar events). They are not idempotent — calling them twice with the same parameters creates two events. They are not destructive — they never delete or overwrite existing events.
- All other tools are read-only and idempotent (safe to retry).
- Layer 1 temporal tools and `expand_rrule` are closed-world (`openWorldHint: false`) — they perform pure computation without external API calls.
- The 3 Platform Mode tools (`resolve_identity`, `query_public_availability`, `request_booking`) are only registered when the server runs in Platform Mode. They are not available in Local Mode.

---

## Layer 1 — Temporal Context

These tools help AI agents orient themselves in time. **Call `get_temporal_context` first** to know the current time and timezone before making calendar queries.

---

## get_temporal_context

Get the current time, timezone, and calendar metadata. This is the entry point — agents should call this first to orient themselves in time.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `timezone` | string | No | IANA timezone (e.g., `"America/New_York"`). Omit to use the configured timezone. |

### Output

```json
{
  "utc": "2026-02-20T15:30:00+00:00",
  "local": "2026-02-20T10:30:00-05:00",
  "timezone": "America/New_York",
  "timezone_configured": true,
  "utc_offset": "-05:00",
  "dst_active": false,
  "day_of_week": "Friday",
  "iso_week": 8,
  "is_weekday": true,
  "day_of_year": 51,
  "next_dst_transition": "2026-03-08T07:00:00+00:00",
  "next_dst_direction": "spring-forward",
  "days_until_dst_transition": 16
}
```

- `timezone_configured: false` means no default timezone is set. The agent should prompt the user to configure one.
- `dst_active` compares the current UTC offset to January 1st (standard time) offset.
- `next_dst_transition`, `next_dst_direction`, and `days_until_dst_transition` are only present for timezones that observe DST. They predict the next upcoming transition (spring-forward or fall-back) by scanning forward up to 400 days.

### Example

> "What time is it?"

```json
{}
```

Or with explicit timezone:

```json
{
  "timezone": "Asia/Tokyo"
}
```

---

## resolve_datetime

Resolve a human time expression into a precise RFC 3339 datetime. Supports 60+ expression patterns.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `expression` | string | Yes | Time expression (e.g., `"next Tuesday at 2pm"`, `"tomorrow morning"`, `"+3h"`) |
| `timezone` | string | No | IANA timezone. Omit to use configured timezone. |

### Output

```json
{
  "resolved_utc": "2026-02-24T19:00:00+00:00",
  "resolved_local": "2026-02-24T14:00:00-05:00",
  "timezone": "America/New_York",
  "interpretation": "Tuesday, February 24, 2026 at 2:00 PM"
}
```

### Supported Expressions

| Category | Examples |
|----------|---------|
| Anchored | `"now"`, `"today"`, `"tomorrow"`, `"yesterday"` |
| Weekday | `"next Monday"`, `"this Friday"`, `"last Wednesday"` |
| Time-of-day | `"morning"` (09:00), `"noon"`, `"evening"` (18:00), `"eob"` (17:00) |
| Explicit time | `"2pm"`, `"2:30pm"`, `"14:00"` |
| Offsets | `"+2h"`, `"-30m"`, `"in 2 hours"`, `"3 days ago"` |
| Combined | `"next Tuesday at 2pm"`, `"tomorrow morning"`, `"next Friday evening"` |
| Period boundaries | `"start of week"`, `"end of month"`, `"next quarter"` |
| Ordinal | `"first Monday of March"`, `"third Friday of next month"` |
| Passthrough | Any RFC 3339 or ISO 8601 date is returned as-is |

### Example

> "When is next Tuesday at 2pm?"

```json
{
  "expression": "next Tuesday at 2pm"
}
```

---

## convert_timezone

Convert an RFC 3339 datetime to a different IANA timezone.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `datetime` | string | Yes | RFC 3339 datetime to convert |
| `target_timezone` | string | Yes | Target IANA timezone |

### Output

```json
{
  "utc": "2026-03-15T18:00:00+00:00",
  "local": "2026-03-15T11:00:00-07:00",
  "timezone": "America/Los_Angeles",
  "utc_offset": "-07:00",
  "dst_active": true
}
```

### Example

> "What time is 6pm UTC in Pacific time?"

```json
{
  "datetime": "2026-03-15T18:00:00Z",
  "target_timezone": "America/Los_Angeles"
}
```

---

## compute_duration

Compute the duration between two timestamps.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start` | string | Yes | First timestamp (RFC 3339) |
| `end` | string | Yes | Second timestamp (RFC 3339) |

### Output

```json
{
  "total_seconds": 30600,
  "days": 0,
  "hours": 8,
  "minutes": 30,
  "seconds": 0,
  "human_readable": "8 hours, 30 minutes"
}
```

### Example

> "How long is my meeting from 9am to 5:30pm?"

```json
{
  "start": "2026-03-16T13:00:00Z",
  "end": "2026-03-16T21:30:00Z"
}
```

---

## adjust_timestamp

Adjust a timestamp by a duration, with DST awareness.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `datetime` | string | Yes | RFC 3339 datetime to adjust |
| `adjustment` | string | Yes | Duration adjustment (e.g., `"+2h"`, `"-30m"`, `"+1d2h30m"`) |
| `timezone` | string | No | IANA timezone for day-level adjustments. Omit to use configured timezone. |

### Output

```json
{
  "original": "2026-03-08T01:00:00-05:00",
  "adjusted_utc": "2026-03-09T05:00:00+00:00",
  "adjusted_local": "2026-03-09T01:00:00-04:00",
  "adjustment_applied": "+1d"
}
```

### Duration Format

- Single unit: `"+2h"`, `"-30m"`, `"+3d"`, `"+1w"`, `"+90s"`
- Compound: `"+1d2h30m"`, `"-2w3d"`
- Must start with `+` or `-`

### DST Behavior

`"+1d"` across DST spring-forward maintains the same wall-clock time (not +24 hours). In the example above, adding 1 day to 1:00 AM EST produces 1:00 AM EDT — the UTC offset changes from -05:00 to -04:00.

### Example

> "What time is 2 hours and 30 minutes from now?"

```json
{
  "datetime": "2026-03-16T14:00:00-04:00",
  "adjustment": "+2h30m"
}
```

---

## Layer 2 — Calendar Operations

---

## list_calendars

Discover all connected calendars across providers with labels and metadata. Call this first to learn what calendars are available before querying events or availability.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `provider` | string | No | Filter to a specific provider (`"google"`, `"outlook"`, `"caldav"`). Omit to list all. |
| `format` | string | No | Output format: `"toon"` (default) or `"json"`. |

### Output

```json
{
  "content": "...",
  "format": "toon",
  "total": 3
}
```

The `content` field contains an array of calendar entries:

```json
[
  {
    "id": "google/primary",
    "provider": "google",
    "name": "My Calendar",
    "label": "Work",
    "primary": true,
    "access_role": "owner"
  }
]
```

- `id` is a provider-prefixed calendar ID (e.g., `"google/primary"`, `"outlook/calendar-uuid"`). Use this value in other tools like `list_events` and `book_slot`.
- `label` is the user-defined display name set during `cortex-mcp setup`. It is `null` if no label was configured.
- When `format` is `"toon"`, the `content` field contains TOON-encoded data (~40% fewer tokens than JSON).

### Example

> "What calendars do I have connected?"

```json
{}
```

Or filtered to one provider:

```json
{
  "provider": "google"
}
```

---

## list_events

List calendar events in a time range.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID to list events from |
| `start` | string | Yes | Start of time range (RFC 3339) |
| `end` | string | Yes | End of time range (RFC 3339) |
| `format` | string | No | Output format: `"toon"` (default) or `"json"`. |

### Output

```json
{
  "content": "...",
  "format": "json",
  "count": 5
}
```

When `format` is `"toon"`, the `content` field contains TOON-encoded calendar data (~40% fewer tokens than JSON).

### Example

> "List my events for tomorrow"

```json
{
  "calendar_id": "primary",
  "start": "2026-03-16T00:00:00Z",
  "end": "2026-03-17T00:00:00Z",
  "format": "toon"
}
```

---

## find_free_slots

Find available free time slots in a calendar within a time window.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID to check for free slots |
| `start` | string | Yes | Start of search window (RFC 3339) |
| `end` | string | Yes | End of search window (RFC 3339) |
| `min_duration_minutes` | integer | No | Minimum slot duration in minutes (default: 30) |
| `format` | string | No | Output format: `"toon"` (default) or `"json"`. |

### Output

```json
{
  "slots": [
    {
      "start": "2026-03-16T10:00:00Z",
      "end": "2026-03-16T12:00:00Z",
      "duration_minutes": 120
    }
  ],
  "count": 3
}
```

### Example

> "Find me a 1-hour slot tomorrow afternoon"

```json
{
  "calendar_id": "primary",
  "start": "2026-03-16T12:00:00-04:00",
  "end": "2026-03-16T18:00:00-04:00",
  "min_duration_minutes": 60
}
```

---

## book_slot

Book a calendar slot using Two-Phase Commit for safe, conflict-free booking.

This is the flagship safety feature. The booking flow:
1. **Lock** — Acquire an exclusive lock on the time slot
2. **Verify** — Check the shadow calendar for conflicts
3. **Write** — Create the event in Google Calendar
4. **Release** — Release the lock

If any step fails, everything rolls back. Two concurrent agents booking the same slot: exactly one succeeds.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID to book in |
| `start` | string | Yes | Start time (RFC 3339) |
| `end` | string | Yes | End time (RFC 3339) |
| `summary` | string | Yes | Event title |
| `description` | string | No | Event description |
| `attendees` | string[] | No | List of attendee email addresses |

### Output

```json
{
  "success": true,
  "event_id": "abc123",
  "booking_id": "def456",
  "summary": "Team Standup",
  "start": "2026-03-16T14:00:00Z",
  "end": "2026-03-16T14:30:00Z"
}
```

### Example

> "Book a 30-minute meeting with alice@example.com tomorrow at 2pm"

```json
{
  "calendar_id": "primary",
  "start": "2026-03-16T14:00:00-04:00",
  "end": "2026-03-16T14:30:00-04:00",
  "summary": "Meeting with Alice",
  "attendees": ["alice@example.com"]
}
```

### Edge Cases

- If the slot is already booked, returns an error with the conflicting event details
- Content (summary, description) is checked against the prompt injection firewall before booking
- Lock TTL defaults to 30 seconds (configurable via `LOCK_TTL_SECS`)

---

## expand_rrule

Expand a recurrence rule (RRULE) into concrete event instances. Uses Truth Engine for deterministic, RFC 5545-compliant expansion.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `rrule` | string | Yes | RFC 5545 RRULE string (e.g., `"FREQ=WEEKLY;BYDAY=MO,WE,FR"`) |
| `dtstart` | string | Yes | Local datetime for the start (e.g., `"2026-03-01T09:00:00"`) |
| `duration_minutes` | integer | No | Duration of each instance in minutes (default: 60) |
| `timezone` | string | Yes | IANA timezone (e.g., `"America/New_York"`) |
| `count` | integer | No | Maximum number of instances to return |
| `format` | string | No | Output format: `"toon"` (default) or `"json"`. |

### Output

```json
{
  "instances": [
    {
      "start": "2026-03-02T14:00:00Z",
      "end": "2026-03-02T15:00:00Z"
    }
  ],
  "count": 10
}
```

### Example

> "When does 'every last Friday of the month' happen in 2026?"

```json
{
  "rrule": "FREQ=MONTHLY;BYDAY=FR;BYSETPOS=-1",
  "dtstart": "2026-01-01T10:00:00",
  "timezone": "America/New_York",
  "count": 12
}
```

### Notes

- `dtstart` is a **local** datetime (no timezone suffix). The `timezone` parameter determines how it maps to UTC.
- `UNTIL` values in the RRULE must be in UTC when `dtstart` has a timezone.
- All DST transitions are handled correctly — spring-forward gaps are skipped, fall-back ambiguities are resolved.

---

## check_availability

Check if a specific calendar time slot is available (not occupied by an event or held by an active booking lock).

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID to check |
| `start` | string | Yes | Start of the time slot (RFC 3339) |
| `end` | string | Yes | End of the time slot (RFC 3339) |

### Output

```json
{
  "available": true
}
```

### Example

> "Am I free at 3pm tomorrow?"

```json
{
  "calendar_id": "primary",
  "start": "2026-03-16T15:00:00-04:00",
  "end": "2026-03-16T15:30:00-04:00"
}
```

---

## get_availability

Get unified availability across multiple calendars. Merges events from all specified calendars into a single busy/free view with privacy controls.

This is the multi-calendar aggregation tool — it combines multiple calendars into one availability picture.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start` | string | Yes | Start of availability window (RFC 3339) |
| `end` | string | Yes | End of availability window (RFC 3339) |
| `privacy` | string | No | `"opaque"` (default) hides source counts, `"full"` shows them |
| `min_free_slot_minutes` | integer | No | Minimum free slot duration in minutes (default: 30) |
| `calendar_ids` | string[] | No | Calendar IDs to query (default: `["primary"]`) |
| `format` | string | No | Output format: `"toon"` (default) or `"json"`. |

### Output

```json
{
  "busy": [
    {
      "start": "2026-03-16T14:00:00Z",
      "end": "2026-03-16T15:00:00Z",
      "source_count": 1
    }
  ],
  "free": [
    {
      "start": "2026-03-16T09:00:00Z",
      "end": "2026-03-16T14:00:00Z",
      "duration_minutes": 300
    }
  ],
  "calendars_merged": 2,
  "privacy": "opaque"
}
```

### Privacy Modes

- **`opaque`** (default): `source_count` is always reported as `0`. The caller sees busy/free blocks but cannot infer how many calendars contributed to a busy block.
- **`full`**: `source_count` shows the actual number of calendars with overlapping events in each busy block.

### Example

> "Show my availability across work and personal calendars for next week"

```json
{
  "start": "2026-03-16T00:00:00-04:00",
  "end": "2026-03-23T00:00:00-04:00",
  "calendar_ids": ["work@example.com", "personal@gmail.com"],
  "min_free_slot_minutes": 60,
  "privacy": "full"
}
```

---

## Platform Mode — Open Scheduling Tools

The following 3 tools are only available in **Platform Mode** (when the server is connected to the Temporal Cortex Platform). They enable AI agents to discover other users, query their public availability, and request bookings — without requiring the caller to have an API key for the target user.

---

## resolve_identity

Resolve an identity (email address, slug, or URL) to a Temporal Cortex user's Open Scheduling profile. Use this to discover whether someone has Open Scheduling enabled before querying their availability.

**Platform Mode only.**

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identity` | string | Yes | The identity to resolve — an email address, slug, or Temporal Link URL (e.g., `"alice@example.com"`, `"alice"`, `"book.temporal-cortex.com/alice"`) |

### Output

```json
{
  "found": true,
  "slug": "alice",
  "display_name": "Alice Johnson",
  "open_scheduling_enabled": true
}
```

- `found: false` means no Temporal Cortex user matches the given identity.
- `open_scheduling_enabled: false` means the user exists but has not enabled Open Scheduling — availability and booking are not publicly queryable.

### Example

> "Can I schedule a meeting with alice@example.com?"

```json
{
  "identity": "alice@example.com"
}
```

---

## query_public_availability

Query another user's public availability by slug. Returns available time slots for a given date and duration. No API key for the target user is required — the target must have Open Scheduling enabled.

**Platform Mode only.**

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slug` | string | Yes | The target user's slug (e.g., `"alice"`) |
| `date` | string | Yes | The date to query (ISO 8601 date, e.g., `"2026-03-15"`) |
| `duration_minutes` | integer | No | Desired meeting duration in minutes (default: 30) |
| `timezone` | string | No | IANA timezone for the response (e.g., `"America/New_York"`). Defaults to the target user's configured timezone. |

### Output

```json
{
  "slug": "alice",
  "date": "2026-03-15",
  "timezone": "America/New_York",
  "slots": [
    {
      "start": "2026-03-15T09:00:00-04:00",
      "end": "2026-03-15T09:30:00-04:00"
    },
    {
      "start": "2026-03-15T10:00:00-04:00",
      "end": "2026-03-15T10:30:00-04:00"
    }
  ]
}
```

### Example

> "When is Alice free next Monday for a 1-hour meeting?"

```json
{
  "slug": "alice",
  "date": "2026-03-16",
  "duration_minutes": 60,
  "timezone": "America/New_York"
}
```

---

## request_booking

Request a booking on another user's public calendar by slug. Creates a calendar event on the target user's behalf. The target must have Open Scheduling enabled. This tool is not idempotent — calling it twice creates two separate bookings.

**Platform Mode only.**

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slug` | string | Yes | The target user's slug (e.g., `"alice"`) |
| `start` | string | Yes | Start time (RFC 3339) |
| `end` | string | Yes | End time (RFC 3339) |
| `title` | string | Yes | Event title |
| `attendee_email` | string | Yes | Email address of the person requesting the booking |
| `attendee_name` | string | No | Display name of the person requesting the booking |
| `description` | string | No | Event description |

### Output

```json
{
  "booking_id": "b1234567-89ab-cdef-0123-456789abcdef",
  "status": "confirmed",
  "calendar_event": {
    "id": "evt_abc123",
    "summary": "Meeting with Bob",
    "start": "2026-03-16T14:00:00-04:00",
    "end": "2026-03-16T14:30:00-04:00"
  }
}
```

### Example

> "Book a 30-minute meeting with Alice next Monday at 2pm"

```json
{
  "slug": "alice",
  "start": "2026-03-16T14:00:00-04:00",
  "end": "2026-03-16T14:30:00-04:00",
  "title": "Meeting with Bob",
  "attendee_email": "bob@example.com",
  "attendee_name": "Bob Smith"
}
```
