#!/usr/bin/env bash
# compose-prompt.sh — assemble the codex $imagegen prompt for a 4-koma pattern
#
# Usage: compose-prompt.sh <workspace_root> <pattern_dir> <style_preset>
#
# Reads:
#   <pattern_dir>/plot.md
#   <workspace_root>/style-guide/<preset>/prompt-fragment.md
#   <workspace_root>/characters/<id>/anchor.md (for each cast member)
#
# Writes:
#   <pattern_dir>/prompt.md
#
# Outputs cast member IDs to stdout (one per line) for invoke-codex.sh to use.

set -euo pipefail

WORKSPACE_ROOT="$1"
PATTERN_DIR="$2"
STYLE_PRESET="${3:-shinkai_default}"

PLOT_FILE="$PATTERN_DIR/plot.md"
PROMPT_FILE="$PATTERN_DIR/prompt.md"
STYLE_FRAGMENT="$WORKSPACE_ROOT/style-guide/$STYLE_PRESET/prompt-fragment.md"

[[ -f "$PLOT_FILE" ]] || { echo "ERROR: plot.md not found at $PLOT_FILE" >&2; exit 1; }
[[ -f "$STYLE_FRAGMENT" ]] || { echo "ERROR: style fragment not found: $STYLE_FRAGMENT" >&2; exit 1; }

# Extract cast IDs from plot.md (lines under "## Cast" until next ## heading)
CAST_IDS=$(awk '/^## Cast$/{flag=1; next} /^## /{flag=0} flag && /^- /{print substr($0,3)}' "$PLOT_FILE")

# Derive episode number from pattern_dir path (.../episodes/NNN-...)
EP_NUM=$(echo "$PATTERN_DIR" | grep -oE '/episodes/[0-9]{3}' | grep -oE '[0-9]{3}' | head -1)
[[ -z "$EP_NUM" ]] && EP_NUM="???"

# Compose prompt.md
{
  echo "[BASE]"
  echo "A vertical 4-panel manga (yonkoma) image with a header banner row at the very top, watercolor style, with speech bubbles containing the Japanese dialogue text from each panel exactly as written in the [SCENE] block below."
  echo ""
  echo "Image layout TOP-DOWN:"
  echo "  1. Header banner row (full width, ~8% of total image height): clean white/cream background with a thin horizontal line below; centered Japanese text in modern sans-serif font, dark navy color. The banner text must read EXACTLY:"
  echo "     (株)ラインワークス★ 公式アカウント X 4コマコンテンツ No.${EP_NUM}"
  echo "  2. Panel 1 (起): below the banner."
  echo "  3. Panel 2 (承): below Panel 1."
  echo "  4. Panel 3 (転): below Panel 2."
  echo "  5. Panel 4 (結): at the bottom."
  echo ""
  echo "Panels are clearly separated with thin black borders. Read top-to-bottom."
  echo ""
  echo "[STYLE]"
  cat "$STYLE_FRAGMENT"
  echo ""
  echo "[CHARACTERS]"
  for cid in $CAST_IDS; do
    ANCHOR="$WORKSPACE_ROOT/characters/$cid/anchor.md"
    if [[ -f "$ANCHOR" ]]; then
      cat "$ANCHOR"
      echo ""
    else
      echo "WARNING: character anchor not found: $ANCHOR" >&2
    fi
  done
  echo "[SCENE]"
  # Extract panel descriptions from plot.md
  awk '/^### (Panel |コマ)/{p=1; print "- "$0; next} /^### /{p=0} p && /^[^[:space:]]/{print "  "$0} p && /^[[:space:]]+[^[:space:]]/{print "  "$0}' "$PLOT_FILE"
  echo ""
  echo "[CONSTRAINTS]"
  echo "- Watercolor aesthetic only — no manga screen tones, no photorealism."
  echo "- No real customer products. No company logos other than LINEWORKS where appropriate."
  echo "- Characters must remain recognizable across panels."
  echo "- Every panel MUST include a speech bubble rendering the panel's Dialogue lines verbatim in clear, readable handwritten-style Japanese text. Speech bubbles are mandatory for the manga to function."
  echo ""
  echo "\$imagegen"
} > "$PROMPT_FILE"

# Emit cast IDs for the caller
echo "$CAST_IDS"
