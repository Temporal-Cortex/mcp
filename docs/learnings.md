# Learnings and Key Decisions

Documenting the reasoning behind key decisions made during the development and launch of the Temporal Cortex MCP server.

## Why "cortex-mcp" and Not "calendar-mcp"

The npm package was originally named `@temporal-cortex/calendar-mcp` during development. We renamed to `@temporal-cortex/cortex-mcp` before the first publish for three reasons:

1. **Name collision**: At least 3 other repos use "calendar-mcp" (rauf543/deciduus, etc.). In directory listings where only the unscoped name appears, we'd be indistinguishable.
2. **Binary alignment**: The Rust binary is `cortex-mcp`. Having the npm bin command match means `ps aux | grep cortex-mcp` finds the same process name shown in MCP configs.
3. **Brand recognition**: `cortex-mcp` is distinctive in tool listings while the `@temporal-cortex/` scope communicates it's part of the Temporal Cortex ecosystem.

Precedent: repo names and npm names don't need to match exactly. `nspady/google-calendar-mcp` publishes as `@cocal/google-calendar-mcp` on npm.

## Why This Is a Documentation Repo (Not a Code Repo)

The MCP server source code lives in a private repository. This public repo follows the pattern used by commercial CLI tools (ngrok, tailscale, 1password-cli) that have public GitHub repos for documentation, issues, and community engagement while keeping source private.

Benefits:
- **Directory indexing**: Smithery, Glama, PulseMCP, and mcp.so crawl public GitHub repos. No public repo = invisible.
- **Trust signal**: Developers evaluating whether to grant OAuth calendar access can inspect the tool documentation, architecture, and issue history.
- **Community hub**: Issues filed here are visible to all users, creating a shared knowledge base.
- **SEO**: GitHub repos rank well for "{product} MCP server" searches.

The tradeoff is documentation drift — tool schemas here must stay in sync with the source. We mitigate this by keeping the tool reference tightly coupled to npm package versions.

## Why the `<product>-mcp` Naming Convention

Analysis of 100+ servers on [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) shows that 90%+ use kebab-case with `-mcp` suffix. Including "mcp" in the name is critical for directory crawler discovery — many indexers filter by name pattern.

## Directory Submission Strategy

Different directories have different discovery mechanisms:

| Directory | Discovery Method | What's Needed |
|-----------|-----------------|---------------|
| Smithery | `smithery.yaml` in repo root | YAML config file |
| Glama | Auto-indexes GitHub repos with `glama.json` | JSON metadata file |
| Official MCP Registry | `mcp-publisher` CLI + `mcpName` in package.json | `.mcp/server.json` + npm publish |
| PulseMCP | Crawls npm packages with "mcp" keyword | npm keywords + public repo |
| mcp.so | GitHub/npm aggregator | npm package + public repo |
| Cline Marketplace | GitHub Issue on cline/mcp-marketplace | Public repo + 400x400 logo + `llms-install.md` |
| Awesome MCP Servers | PR to punkpeye/awesome-mcp-servers | One-line description |

All submissions require the npm package to be published first. Directory crawlers verify that `npx @temporal-cortex/cortex-mcp` actually resolves to a working package.

## The Open-Core Boundary

What's open source (in [temporal-cortex-core](https://github.com/billylui/temporal-cortex-core)):
- Truth Engine: RRULE expansion, availability merging, conflict detection
- TOON: Token-Oriented Object Notation encoder/decoder
- Published to crates.io, npm, and PyPI

What's commercial (private):
- Calendar provider integrations (Google, Outlook, CalDAV)
- Two-Phase Commit booking safety layer
- Distributed locking (Redlock)
- OAuth credential management
- Content sanitization firewall
- Usage metering and billing
- The MCP server binary itself

The open-core model works as a funnel: developers discover Truth Engine or TOON, see the MCP server as the productized version, and enterprise users upgrade to the Platform for multi-provider, multi-tenant deployments.
