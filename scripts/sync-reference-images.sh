#!/bin/bash
# reference-images を Google Drive 共有フォルダから同期する
# Usage: bash scripts/sync-reference-images.sh
#
# 共有フォルダ:
#   会社公式X_サンプルデータ
#   https://drive.google.com/drive/folders/1HSA4aeVhaQPh9x6NMGPmbXWYYbE2iY9q
#
# 「anyone with link」共有のため OAuth 不要。gdown が --continue でリジューム対応。
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$PROJECT_ROOT/.venv"
DRIVE_FOLDER_ID="1HSA4aeVhaQPh9x6NMGPmbXWYYbE2iY9q"
TARGET_DIR="$PROJECT_ROOT/reference-images"

if [ ! -x "$VENV/bin/gdown" ]; then
  echo "ERROR: gdown not installed. Run: $VENV/bin/pip install gdown"
  exit 1
fi

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

echo "Syncing from Google Drive folder $DRIVE_FOLDER_ID..."
"$VENV/bin/gdown" --folder --continue "https://drive.google.com/drive/folders/$DRIVE_FOLDER_ID"

echo
echo "Synced. Current state:"
echo "  Total files: $(find "$TARGET_DIR" -type f | wc -l)"
echo "  Total size:  $(du -sh "$TARGET_DIR" | cut -f1)"
