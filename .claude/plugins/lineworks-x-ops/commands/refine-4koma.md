---
description: Refine an existing 4-koma pattern by re-generating with modified instructions.
argument-hint: "<episode-id> <pattern-id> <修正指示>"
---

# /refine-4koma

Refine one pattern of an existing episode.

## Usage

```
/refine-4koma 001-2026-05-12-設計室の朝 pattern-c "3コマ目の構図をもっと引きにして、セバスチャンを左側に"
```

## What this does

1. Loads the existing `episodes/<ep-id>/patterns/<pattern-id>/plot.md`
2. Applies the user's instruction to modify either the plot or the image prompt (or both)
3. Re-runs `4koma-image-gen` to produce `generated_v2.png` (or `_v3`, `_v4`...)
4. Preserves prior versions

## Action

Read `episodes/<ep-id>/patterns/<pattern-id>/plot.md`. Apply the modification to either the plot.md or just the prompt (decide based on the instruction — content changes touch plot.md, visual-only changes touch only prompt assembly).

If you modify plot.md, save the previous version as `plot_v1.md` (and the new one as `plot.md`).

Then re-run the image generation script:

```bash
WORKSPACE="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
SKILL_DIR="$WORKSPACE/.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts"
EP_DIR="$WORKSPACE/episodes/<ep-id>"
PATTERN_DIR="$EP_DIR/patterns/<pattern-id>"

STYLE=$(awk '/^## Style preset suggestion$/{getline; print; exit}' "$PATTERN_DIR/plot.md")
CAST=$(bash "$SKILL_DIR/compose-prompt.sh" "$WORKSPACE" "$PATTERN_DIR" "$STYLE")

# Determine next version number (count existing generated_v*.png to avoid clobbering)
EXISTING_MAX=$(ls "$PATTERN_DIR"/generated_v*.png 2>/dev/null | sed -E 's/.*generated_v([0-9]+)\.png/\1/' | sort -n | tail -1)
NEXT=$(( ${EXISTING_MAX:-1} + 1 ))

bash "$SKILL_DIR/invoke-codex.sh" "$WORKSPACE" "$PATTERN_DIR" "$STYLE" "$CAST"
mv "$PATTERN_DIR/generated.png" "$PATTERN_DIR/generated_v${NEXT}.png"
```

Report back the path of the new image and prompt the user to review.
