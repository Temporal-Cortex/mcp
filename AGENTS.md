# Temporal Cortex MCP

Public documentation repo for the Temporal Cortex MCP server (`@temporal-cortex/cortex-mcp`). Source code is in a private repository — this repo contains user-facing docs, setup guides, integration examples, directory configs, and the Dockerfile.

## Structure

- `README.md` — Main user-facing docs (Q&A format: each section is a question)
- `CHANGELOG.md` — Release history
- `docs/` — Setup guides (google-cloud-setup, outlook-setup, caldav-setup), tool reference, integration guides (CrewAI, OpenAI Agents SDK), architecture overview
- `examples/` — Integration examples: `crewai/`, `langgraph/`, `openai-agents/`, config snippets (claude-desktop.json, cursor.json, windsurf.json)
- `Dockerfile` — Multi-stage build wrapping the npm binary
- `smithery.yaml` — Smithery directory config
- `glama.json` — Glama directory metadata (maintainers field only; Docker config is in Glama dashboard)
- `.mcp/server.json` — MCP Registry metadata
- `assets/` — Icons and logos

## Build & Test

No build system — this is a docs-only repo. To verify changes:

```
npx markdown-link-check README.md   # check links
```

Ensure version numbers match across README.md, Dockerfile, and smithery.yaml.

## Conventions

- Pin npm version (`@temporal-cortex/cortex-mcp@X.Y.Z`) in Dockerfile, smithery.yaml, and `.mcp/server.json`
- Do NOT pin npm versions in user-facing docs — always use `@temporal-cortex/cortex-mcp` (latest)
- Keep tool counts (18), layer numbers (0-4), and tool lists in sync with the source
- README uses Q&A format: each `##` section is a question starting with "How", "What", "Can"
- No pricing or business strategy content (public repo)

## Adding Examples

Follow the pattern in `examples/crewai/`:
- `README.md` with prerequisites, quick start, file descriptions
- `.env.example` with required environment variables
- `requirements.txt` for Python dependencies
- Both Local Mode (stdio) and Platform Mode (HTTP) variants where applicable

## Boundaries

- Always: verify version numbers match across README, Dockerfile, smithery.yaml after version bumps
- Ask first: changing tool descriptions, parameter schemas, or layer assignments
- Never: include API keys, secrets, or pricing information
