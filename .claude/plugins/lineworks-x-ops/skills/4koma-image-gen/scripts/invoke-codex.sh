#!/usr/bin/env bash
# invoke-codex.sh — call codex exec with a composed prompt and reference images,
# then move the generated PNG into the pattern dir.
#
# Usage: invoke-codex.sh <workspace_root> <pattern_dir> <style_preset> <cast_ids_space_separated>
#
# Reads:
#   <pattern_dir>/prompt.md
#   <workspace_root>/characters/<cid>/reference/*.png (for each cast member)
#   <workspace_root>/style-guide/<preset>/samples/*.png
#
# Writes:
#   <pattern_dir>/codex.stdout.log
#   <pattern_dir>/generated.png
#   <pattern_dir>/error.log (only on failure)

set -euo pipefail

WORKSPACE_ROOT="$1"
PATTERN_DIR="$2"
STYLE_PRESET="${3:-shinkai_default}"
CAST_IDS="${4:-}"

PROMPT_FILE="$PATTERN_DIR/prompt.md"
STDOUT_LOG="$PATTERN_DIR/codex.stdout.log"
ERROR_LOG="$PATTERN_DIR/error.log"
GENERATED="$PATTERN_DIR/generated.png"

[[ -f "$PROMPT_FILE" ]] || { echo "ERROR: prompt.md not found at $PROMPT_FILE" >&2; exit 1; }

# --- Pre-flight: codex auth check ---
PRECHECK=$(codex exec --skip-git-repo-check --ephemeral "Reply: OK" </dev/null 2>&1 || true)
if echo "$PRECHECK" | grep -qE "401|token_expired|refresh token was already used"; then
  {
    echo "ERROR: Codex authentication failed pre-flight."
    echo ""
    echo "$PRECHECK" | tail -10
    echo ""
    echo "Please run 'codex logout && codex login' (see docs/runbooks/codex-relogin.md)."
  } > "$ERROR_LOG"
  exit 2
fi

# --- Build -i flags for reference images ---
REF_ARGS=()
for cid in $CAST_IDS; do
  shopt -s nullglob
  for img in "$WORKSPACE_ROOT/characters/$cid/reference/"*.png; do
    REF_ARGS+=(-i "$img")
  done
  shopt -u nullglob
done
shopt -s nullglob
for img in "$WORKSPACE_ROOT/style-guide/$STYLE_PRESET/samples/"*.png; do
  REF_ARGS+=(-i "$img")
done
shopt -u nullglob

# --- Invoke Codex ---
cat "$PROMPT_FILE" | codex exec \
  --skip-git-repo-check \
  --ephemeral \
  "${REF_ARGS[@]}" \
  - \
  > "$STDOUT_LOG" 2>&1 || {
    cp "$STDOUT_LOG" "$ERROR_LOG"
    echo "ERROR: codex exec failed (see $ERROR_LOG)" >&2
    exit 3
  }

# --- Find session id and locate generated image ---
SID=$(grep -oE 'session id: [a-f0-9-]+' "$STDOUT_LOG" | head -1 | awk '{print $3}')
if [[ -z "$SID" ]]; then
  echo "ERROR: could not extract session id from codex stdout" > "$ERROR_LOG"
  cat "$STDOUT_LOG" >> "$ERROR_LOG"
  exit 4
fi

shopt -s nullglob
SRC_FILES=( "$HOME/.codex/generated_images/$SID/"ig_*.png )
shopt -u nullglob
SRC="${SRC_FILES[0]:-}"
if [[ -z "$SRC" || ! -f "$SRC" ]]; then
  echo "ERROR: no generated image found at ~/.codex/generated_images/$SID/" > "$ERROR_LOG"
  exit 5
fi

cp "$SRC" "$GENERATED"

# --- Validate ---
SIZE=$(wc -c < "$GENERATED" | tr -d ' ')
if [[ "$SIZE" -lt 100000 ]]; then
  echo "WARNING: generated image is suspiciously small (${SIZE} bytes)" >> "$ERROR_LOG"
fi

if ! file "$GENERATED" | grep -q "PNG image data"; then
  echo "ERROR: generated file is not a valid PNG" > "$ERROR_LOG"
  exit 6
fi

echo "SUCCESS: $GENERATED ($SIZE bytes)"
