# Tool Reference

Complete reference for the 6 MCP tools provided by `@temporal-cortex/cortex-mcp`.

All datetime parameters use [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) format (e.g., `2026-03-15T14:00:00Z` or `2026-03-15T10:00:00-04:00`).

---

## list_events

List calendar events in a time range.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID to list events from |
| `start` | string | Yes | Start of time range (RFC 3339) |
| `end` | string | Yes | End of time range (RFC 3339) |
| `format` | string | No | Output format: `"toon"` or `"json"` (default: `"json"`) |

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
