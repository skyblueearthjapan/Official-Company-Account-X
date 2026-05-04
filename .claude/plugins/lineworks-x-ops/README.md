# lineworks-x-ops

Claude Code plugin for the LINEWORKS official X account 4-koma manga pipeline.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `4koma-compose` | Generate 4-panel manga plot + dialogue from a theme |
| Skill | `4koma-image-gen` | Build the image generation prompt and invoke `codex exec ... $imagegen` |
| Agent | `manga-director` | Orchestrate the full episode pipeline (4 patterns in parallel) |
| Command | `/new-4koma` | Start a new episode |
| Command | `/refine-4koma` | Refine an existing pattern |
| Command | `/finalize-4koma` | Lock in the chosen pattern as `final/` |

## Dependencies

- Codex CLI v0.128+ (subprocess), authenticated with ChatGPT subscription
- Claude Code (host)

## Configuration

Reads:
- `characters/<id>/anchor.md` for character prompt fragments
- `style-guide/<preset>/prompt-fragment.md` for style fragments
- Per-project paths assumed relative to the workspace root (`会社公式アカウントＸ運用/`)

## See also

- Spec: `docs/superpowers/specs/2026-05-03-x-account-ops-design.md`
- Runbook: `docs/runbooks/weekly-4koma-flow.md`
