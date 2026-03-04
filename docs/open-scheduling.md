# Open Scheduling

Open Scheduling lets any person or agent book time with a Temporal Cortex user through a public Temporal Link. No authentication is required to query availability or book a meeting — the calendar owner configures their availability rules, connects their calendars, and shares a single URL.

This enables two core interaction modes:

- **Human-to-agent** — A person visits `book.temporal-cortex.com/{slug}` or shares the link with an AI assistant that books on their behalf.
- **Agent-to-agent** — An AI agent discovers another agent's scheduling endpoint via the Agent Card and negotiates a meeting time programmatically using the A2A JSON-RPC interface.

## Setup

Open Scheduling is configured through the Temporal Cortex dashboard at `app.temporal-cortex.com`.

1. **Choose a slug** — Navigate to **Settings > Open Scheduling** and set a unique slug (e.g., `jane-doe`). This becomes your Temporal Link: `book.temporal-cortex.com/jane-doe`.
2. **Enable the toggle** — Flip **Open Scheduling** to active. Your availability and booking endpoints go live immediately.
3. **Connect calendars** — Under **Calendars**, connect at least one calendar provider (Google Calendar, Outlook, or CalDAV). Select which calendars contribute to your availability and which calendar receives new bookings.
4. **Configure availability rules** (optional) — Set working hours, minimum notice period, buffer between meetings, and maximum advance booking window.

Once enabled, four public endpoints become available under your slug.

## Temporal Links

A Temporal Link is a stable URL that resolves to a user's Open Scheduling profile:

```
book.temporal-cortex.com/{slug}
```

When visited in a browser, the link renders a booking page showing the user's available time slots. When accessed programmatically, the underlying API endpoints return structured JSON responses.

Temporal Links are permanent as long as the slug is reserved. Disabling Open Scheduling returns `404` on all endpoints until re-enabled.

## Agent Card

Every Open Scheduling profile exposes a discoverable Agent Card following the A2A (Agent-to-Agent) protocol.

### Request

```
GET /public/{slug}/.well-known/agent-card.json
```

### Response

```json
{
  "name": "Jane Doe",
  "description": "Schedule a meeting with Jane Doe via Temporal Cortex",
  "url": "https://book.temporal-cortex.com/jane-doe",
  "capabilities": {
    "a2a": "https://book.temporal-cortex.com/public/jane-doe/a2a",
    "availability": "https://book.temporal-cortex.com/public/jane-doe/availability",
    "booking": "https://book.temporal-cortex.com/public/jane-doe/book"
  },
  "provider": {
    "name": "Temporal Cortex",
    "url": "https://temporal-cortex.com"
  },
  "version": "1.0"
}
```

The Agent Card allows any A2A-compatible agent to discover scheduling capabilities without prior configuration.

## Public Availability API

Query a user's available time slots for a given date.

### Request

```
GET /public/{slug}/availability?date=YYYY-MM-DD
```

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | `string` | Yes | Date in `YYYY-MM-DD` format |
| `duration` | `integer` | No | Minimum slot duration in minutes (default: 30) |
| `timezone` | `string` | No | IANA timezone for response times (default: user's configured timezone) |

### Example

```bash
curl "https://book.temporal-cortex.com/public/jane-doe/availability?date=2026-03-10&duration=30&timezone=America/New_York"
```

### Response

```json
{
  "slug": "jane-doe",
  "date": "2026-03-10",
  "timezone": "America/New_York",
  "slots": [
    {
      "start": "2026-03-10T09:00:00-05:00",
      "end": "2026-03-10T09:30:00-05:00"
    },
    {
      "start": "2026-03-10T10:00:00-05:00",
      "end": "2026-03-10T10:30:00-05:00"
    },
    {
      "start": "2026-03-10T14:00:00-05:00",
      "end": "2026-03-10T15:00:00-05:00"
    }
  ]
}
```

If the user has disabled Open Scheduling or the slug does not exist, the endpoint returns `404`.

## Public Booking API

Book a time slot on the user's default calendar.

### Request

```
POST /public/{slug}/book
Content-Type: application/json
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | `string` | Yes | RFC 3339 start time with timezone offset |
| `end` | `string` | Yes | RFC 3339 end time with timezone offset |
| `title` | `string` | Yes | Meeting title (sanitized by the content safety firewall) |
| `attendee_email` | `string` | Yes | Email of the person requesting the meeting |
| `attendee_name` | `string` | No | Display name of the attendee |
| `description` | `string` | No | Meeting description (sanitized by the content safety firewall) |

### Example

```bash
curl -X POST "https://book.temporal-cortex.com/public/jane-doe/book" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2026-03-10T10:00:00-05:00",
    "end": "2026-03-10T10:30:00-05:00",
    "title": "Intro call",
    "attendee_email": "alex@example.com",
    "attendee_name": "Alex Chen"
  }'
```

### Response (201 Created)

```json
{
  "booking_id": "bk_a1b2c3d4e5f6",
  "status": "confirmed",
  "calendar_event": {
    "start": "2026-03-10T10:00:00-05:00",
    "end": "2026-03-10T10:30:00-05:00",
    "title": "Intro call",
    "attendee_email": "alex@example.com"
  }
}
```

### Error Response (409 Conflict)

```json
{
  "error": "slot_unavailable",
  "message": "The requested time slot is no longer available."
}
```

Bookings use the same Two-Phase Commit protocol as the `book_slot` MCP tool: lock, verify, write, release. If the slot becomes unavailable between the availability query and the booking request, the endpoint returns `409`.

## A2A JSON-RPC

The A2A endpoint supports JSON-RPC 2.0 for agent-to-agent scheduling negotiation.

```
POST /public/{slug}/a2a
Content-Type: application/json
```

### Method: `query_availability`

Query available time slots programmatically.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "query_availability",
  "params": {
    "date": "2026-03-10",
    "duration": 30,
    "timezone": "America/New_York"
  },
  "id": 1
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "slots": [
      {
        "start": "2026-03-10T09:00:00-05:00",
        "end": "2026-03-10T09:30:00-05:00"
      },
      {
        "start": "2026-03-10T14:00:00-05:00",
        "end": "2026-03-10T15:00:00-05:00"
      }
    ]
  },
  "id": 1
}
```

### Method: `book_slot`

Book a time slot via JSON-RPC.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "book_slot",
  "params": {
    "start": "2026-03-10T14:00:00-05:00",
    "end": "2026-03-10T14:30:00-05:00",
    "title": "Strategy sync",
    "attendee_email": "agent@example.com"
  },
  "id": 2
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "booking_id": "bk_x7y8z9w0v1u2",
    "status": "confirmed"
  },
  "id": 2
}
```

**Error (slot taken):**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Slot unavailable",
    "data": {
      "reason": "slot_conflict"
    }
  },
  "id": 2
}
```

### Example: Agent-to-Agent Booking

```bash
curl -X POST "https://book.temporal-cortex.com/public/jane-doe/a2a" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "query_availability",
    "params": { "date": "2026-03-10", "duration": 60 },
    "id": 1
  }'
```

## Identity Resolution

Resolve a known identity (email address) to a Temporal Link slug.

### Request

```
GET /resolve?identity=email@example.com
```

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identity` | `string` | Yes | Email address to resolve |

### Example

```bash
curl "https://book.temporal-cortex.com/resolve?identity=jane@example.com"
```

### Response (200 OK)

```json
{
  "identity": "jane@example.com",
  "slug": "jane-doe",
  "url": "https://book.temporal-cortex.com/jane-doe",
  "agent_card": "https://book.temporal-cortex.com/public/jane-doe/.well-known/agent-card.json"
}
```

### Response (404 Not Found)

```json
{
  "error": "identity_not_found",
  "message": "No Open Scheduling profile is associated with this identity."
}
```

Only users who have explicitly enabled Open Scheduling and linked their email are discoverable. The endpoint does not confirm or deny the existence of an email address for users without Open Scheduling enabled.

## Rate Limits

Public endpoints are rate-limited per IP address to prevent abuse.

| Endpoint | Limit | Window |
|----------|-------|--------|
| `GET /public/{slug}/availability` | 60 requests | per minute |
| `POST /public/{slug}/book` | 10 bookings | per hour |
| `POST /public/{slug}/a2a` (`query_availability`) | 60 requests | per minute |
| `POST /public/{slug}/a2a` (`book_slot`) | 10 bookings | per hour |
| `GET /resolve` | 30 requests | per minute |
| `GET /.well-known/agent-card.json` | 60 requests | per minute |

When the limit is exceeded, the endpoint returns `429 Too Many Requests` with a `Retry-After` header indicating seconds until the next request is allowed.

## Security

Open Scheduling endpoints are designed to be publicly accessible without authentication, with the following safeguards:

- **No authentication required for availability queries.** Anyone with the slug can check available times. This is intentional — availability is non-sensitive scheduling metadata.
- **`attendee_email` is required for booking.** Every booking request must include a valid email address. This provides an audit trail and enables confirmation emails.
- **Content sanitization.** All user-provided strings (`title`, `description`, `attendee_name`) pass through the content safety firewall before reaching the calendar provider. Prompt injection attempts, malicious content, and zero-width Unicode characters are stripped or rejected.
- **Rate limiting.** Per-IP rate limits prevent enumeration attacks on the `/resolve` endpoint and booking spam on the `/book` endpoint.
- **Two-Phase Commit for booking integrity.** Bookings use the same lock-verify-write-release protocol as the MCP `book_slot` tool, preventing double-bookings even under concurrent requests.
- **Slug privacy.** Slugs are chosen by the user and are not enumerable. The `/resolve` endpoint only returns results for users who have explicitly opted in.
- **HTTPS only.** All endpoints are served over TLS. HTTP requests are redirected to HTTPS.
