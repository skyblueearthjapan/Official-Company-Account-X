---
name: 4koma-image-gen
description: Use when converting a 4-panel manga plot into a generated watercolor image. Reads plot.md, character anchors, and a style preset; assembles the codex prompt; invokes codex exec with reference images attached; copies the output PNG into the pattern folder.
---

# 4koma-image-gen

Convert one `plot.md` into one `generated.png` via Codex `$imagegen`.

## Inputs

- `pattern_dir` (required) — absolute path to `episodes/<id>/patterns/<pattern_id>/`
- `style_preset` (optional) — `shinkai_default` (default) | `picturebook` | `ghibli_bg`
- `workspace_root` (required) — absolute path to project root, for resolving characters/ and style-guide/

## Pipeline

### Step 1: Pre-flight check

Verify Codex auth is fresh by running:

```bash
codex exec --skip-git-repo-check --ephemeral "Reply: OK" </dev/null 2>&1 | tail -5
```

If output contains `401`, `token_expired`, or `refresh token was already used` — abort and refer the user to `docs/runbooks/codex-relogin.md`.

### Step 2: Compose the prompt

Use `scripts/compose-prompt.sh` to assemble:

```
[BASE]
A 4-panel manga (yonkoma) in vertical layout, watercolor style, no speech bubbles initially.
Panels are clearly separated with thin borders.
Read top-to-bottom.

[STYLE]
{contents of style-guide/<preset>/prompt-fragment.md}

[CHARACTERS]
{for each cast member listed in plot.md, append contents of characters/<id>/anchor.md}

[SCENE]
{render the 4 panels from plot.md as English scene descriptions}
- Panel 1: <scene + character actions>
- Panel 2: ...
- Panel 3: ...
- Panel 4: ...

[CONSTRAINTS]
- Watercolor aesthetic only — no manga screen tones, no photorealism.
- No real customer products. No company logos other than LINEWORKS where appropriate.
- Characters must remain recognizable across panels.

$imagegen
```

Save the assembled prompt to `<pattern_dir>/prompt.md`.

### Step 3: Collect reference images

```bash
REFS=()
for char_id in <cast members>; do
  for img in "$WORKSPACE_ROOT/characters/$char_id/reference/"*.png; do
    [[ -f "$img" ]] && REFS+=(-i "$img")
  done
done
for img in "$WORKSPACE_ROOT/style-guide/$STYLE_PRESET/samples/"*.png; do
  [[ -f "$img" ]] && REFS+=(-i "$img")
done
```

### Step 4: Invoke Codex

Use `scripts/invoke-codex.sh`:

```bash
codex exec \
  --skip-git-repo-check \
  --ephemeral \
  "${REFS[@]}" \
  "$(cat <pattern_dir>/prompt.md)" \
  </dev/null \
  > "<pattern_dir>/codex.stdout.log" 2>&1
```

Capture the session ID from the stdout log (line `session id: ...`).

### Step 5: Move the generated image

```bash
SID=$(grep -oP 'session id: \K[a-f0-9-]+' "<pattern_dir>/codex.stdout.log" | head -1)
SRC=$(ls "$HOME/.codex/generated_images/$SID/"ig_*.png 2>/dev/null | head -1)
cp "$SRC" "<pattern_dir>/generated.png"
```

If multiple PNGs exist (rare), copy the first; record others in `<pattern_dir>/extras/`.

### Step 6: Validate

- File exists at `<pattern_dir>/generated.png`
- File size > 100KB (rough sanity)
- File is a valid PNG (`file <pattern_dir>/generated.png` reports PNG image data)

If any validation fails, log to `<pattern_dir>/error.log` and exit non-zero (manga-director will surface this to user).

## Backend abstraction (future)

This skill abstracts the image generation backend. Phase 2+ alternatives:
- MCP-based: replace `codex exec` call with MCP `codex` tool invocation via Claude Code
- Direct API: invoke OpenAI Image API with `OPENAI_API_KEY`

The interface remains: `(pattern_dir, style_preset) → generated.png`.
