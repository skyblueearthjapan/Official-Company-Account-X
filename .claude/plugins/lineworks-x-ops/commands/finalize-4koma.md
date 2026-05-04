---
description: Lock in one pattern as the final version of an episode.
argument-hint: "<episode-id> <pattern-id>"
---

# /finalize-4koma

Mark one pattern as the chosen final version for an episode.

## Usage

```
/finalize-4koma 001-2026-05-12-設計室の朝 pattern-c
```

## What this does

1. Copies `episodes/<ep-id>/patterns/<pattern-id>/{plot.md, prompt.md, generated*.png}` into `episodes/<ep-id>/final/`
2. Renames the latest `generated*.png` to `final.png`
3. Updates `episodes/<ep-id>/README.md` to record the chosen pattern
4. Creates `episodes/<ep-id>/notes.md` (if not present) and prompts the user to fill in:
   - Why this pattern was chosen
   - Any post-generation manual edits needed (Phase 2 work)
   - Lessons learned for the next episode

## Action

```bash
WORKSPACE="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
EP_DIR="$WORKSPACE/episodes/<ep-id>"
PATTERN_DIR="$EP_DIR/patterns/<pattern-id>"
FINAL_DIR="$EP_DIR/final"

mkdir -p "$FINAL_DIR"
cp "$PATTERN_DIR/plot.md" "$FINAL_DIR/plot.md"
cp "$PATTERN_DIR/prompt.md" "$FINAL_DIR/prompt.md"

# Find the latest generated*.png (highest version number, or unsuffixed)
LATEST=$(ls -t "$PATTERN_DIR"/generated*.png | head -1)
cp "$LATEST" "$FINAL_DIR/final.png"
```

Update `$EP_DIR/README.md` with: "Final: pattern-c (selected on YYYY-MM-DD)".

Create `$EP_DIR/notes.md` with template:

```markdown
# Episode <ep-id> Notes

## Chosen pattern
<pattern-id>

## Why
<...>

## Manual edits needed
<...>

## Lessons learned
<...>
```

Report back with the final.png path and prompt the user to fill in `notes.md`.
