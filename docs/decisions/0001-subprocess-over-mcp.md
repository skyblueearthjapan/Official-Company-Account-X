# ADR 0001: Use Codex `exec` subprocess over MCP for Phase 1

- **Status:** Accepted
- **Date:** 2026-05-03
- **Deciders:** 今泉課長

## Context

Phase 1 needs to call OpenAI's `gpt-image-2` via Codex CLI from Claude Code. Three integration paths exist:

1. **Subprocess** — Claude Code Bash → `codex exec ... $imagegen`
2. **MCP** — Claude Code → MCP → `codex mcp-server` (exposes `codex` tool)
3. **Direct API** — Claude Code → OpenAI Image API (uses `OPENAI_API_KEY`)

Phase 0 verification confirmed all three are technically viable. ChatGPT Team subscription is the desired billing path.

## Decision

Use **subprocess (`codex exec`)** as the Phase 1 default.

## Rationale

- Codex MCP server exposes a single `codex` tool that wraps the entire Codex agent — it does not expose `$imagegen` as a granular tool. The behavioral difference between MCP and subprocess is minimal.
- Subprocess gives transparent stdin/stdout, predictable file outputs at `~/.codex/generated_images/<sid>/ig_*.png`, and trivial debugging.
- MCP adds a long-running server lifecycle to manage with no compensating benefit for our use case.
- Direct API would bypass the ChatGPT Team subscription quota and incur per-image billing. Reserved as fallback for emergencies / bulk generation only.

## Consequences

- Image generation is invoked via `codex exec --skip-git-repo-check --ephemeral -i <ref>... "<prompt> $imagegen"` and a Bash script reads the resulting PNG out of `~/.codex/generated_images/`.
- The `4koma-image-gen` skill abstracts the backend so MCP / direct API can be swapped in later (Phase 2+) without changing callers.
- Image generation cost is bounded by ChatGPT Team plan quota (~22K tokens / image observed in Phase 0).

## Reconsider when

- Subprocess startup latency or file plumbing becomes a recurring pain point
- A future Codex version exposes `$imagegen` as a dedicated MCP tool with structured image return
- Quota hits force a switch to direct API billing
