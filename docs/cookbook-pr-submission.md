# OpenAI Cookbook PR Submission Guide

Step-by-step instructions for submitting the "Deterministic Calendar Scheduling with MCP" notebook to the OpenAI Cookbook.

## Pre-Submission

1. **Fork** `openai/openai-cookbook` on GitHub
2. **Clone** your fork locally

## Files to Add/Modify

### 1. Copy notebook

```bash
cp examples/openai-agents/deterministic_calendar_scheduling_with_mcp.ipynb \
   <cookbook-fork>/examples/mcp/deterministic_calendar_scheduling_with_mcp.ipynb
```

### 2. Append to `registry.yaml`

Add this entry at the end of the file (maintain YAML formatting):

```yaml
- title: Deterministic Calendar Scheduling with MCP
  path: examples/mcp/deterministic_calendar_scheduling_with_mcp.ipynb
  slug: deterministic-calendar-scheduling-with-mcp
  description: Build a scheduling agent that never hallucinates dates using MCP tools for deterministic datetime resolution, cross-provider availability merging, and Two-Phase Commit booking.
  date: 2026-03-06
  authors:
    - billylui
  tags:
    - mcp
    - responses
```

### 3. Append to `authors.yaml`

Add this entry (alphabetical order by key):

```yaml
billylui:
  name: "Billy Lui"
  website: "https://github.com/billylui"
  avatar: "https://avatars.githubusercontent.com/u/billylui?v=4"
```

**Note**: Replace the avatar URL with the actual GitHub avatar URL. Find it by visiting `https://github.com/billylui` and right-clicking the profile image → Copy Image Address.

## PR Title

```
Add: Deterministic Calendar Scheduling with MCP
```

## PR Description

Use this template (the repo auto-populates the checklist from `.github/pull_request_template.md`):

```markdown
## Summary

Adds a Jupyter notebook demonstrating deterministic calendar scheduling using
HostedMCPTool with the OpenAI Agents SDK. The notebook connects to a calendar
MCP server (Temporal Cortex) to build a scheduling agent that resolves
datetime expressions, checks calendar availability, and books meetings with
Two-Phase Commit safety.

## Motivation

The existing MCP Tool Guide covers e-commerce (Shopify), DevOps (Sentry/GitHub),
and messaging (Twilio) examples, but has no calendar or scheduling content.
Calendar scheduling is a high-demand use case where LLMs consistently fail —
scoring below 50% on temporal reasoning benchmarks (OOLONG, Test of Time).
This notebook fills that gap by showing how MCP tools provide deterministic
datetime handling that eliminates hallucinated dates and double-bookings.

## For new content

- [x] I have added a new entry in registry.yaml (and in authors.yaml)
      so that my content renders on the cookbook website.
- [x] I have conducted a self-review of my content based on the contribution guidelines:
  - [x] Relevance: Uses OpenAI Agents SDK + Responses API with HostedMCPTool
  - [x] Uniqueness: First calendar/scheduling MCP example in the cookbook
  - [x] Spelling and Grammar: Reviewed and proofread
  - [x] Clarity: Progressive structure — setup → connect → build agent → add approval gates → explanation
  - [x] Correctness: Code executes successfully against live MCP server
  - [x] Completeness: References OOLONG/Test-of-Time benchmarks, links to tool docs and MCP guide
```

## Quality Self-Assessment

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Relevance | 4 | Uses Responses API + Agents SDK + HostedMCPTool (core OpenAI tech) |
| Uniqueness | 4 | Zero calendar/scheduling content exists in the cookbook |
| Spelling/Grammar | 3 | Proofread, no errors |
| Clarity | 4 | Progressive: setup → connect → agent → approval → explanation |
| Correctness | 3 | Code tested against live MCP server (outputs not saved in notebook — matches mcp_tool_guide.ipynb pattern) |
| Completeness | 3 | Cites academic benchmarks, links to tool reference, MCP guide, Agent Skills |

All scores ≥ 3. Ready for submission.

## CI Check

The `Validate Notebooks` workflow runs `nbformat.read(path, as_version=4)` on changed `.ipynb` files.
Our notebook passes this check (verified locally).

## Review Timeline

- Reviews are "best-effort" — no guaranteed timeline
- PRs with no activity for 60 days get "Stale" label, closed after 10 more days
- Recent community PRs were merged within days to weeks
- Respond promptly to reviewer feedback to avoid going stale

## After Merge

The notebook will be available at:
`https://cookbook.openai.com/examples/mcp/deterministic-calendar-scheduling-with-mcp`
