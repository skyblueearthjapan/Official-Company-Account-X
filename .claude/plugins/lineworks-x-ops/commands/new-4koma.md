---
description: Start a new 4-koma episode. Generates 4 plot/image patterns in parallel from a theme.
argument-hint: "<お題テキスト> [--patterns N]"
---

# /new-4koma

Start a new 4-koma episode for the LINEWORKS official X account.

## Usage

```
/new-4koma "<お題テキスト>"
/new-4koma "<お題テキスト>" --patterns 3
```

## What this does

Invokes the `manga-director` agent which:
1. Creates a new episode folder under `episodes/<NNN>-<YYYY-MM-DD>-<title>/`
2. Generates 4 (or N) distinct plot variants in parallel via `4koma-compose`
3. Generates 4 watercolor 4-koma images in parallel via `4koma-image-gen` (calling Codex `$imagegen`)
4. Reports back with paths to all generated PNGs for review

## Cost

~90K tokens (default 4 patterns) consumed from your ChatGPT Team subscription. Takes 3-5 minutes.

## Pre-conditions

- Codex CLI is installed and authenticated (`codex login status` returns "Logged in using ChatGPT")
- Character sheets exist under `characters/<id>/`
- Style guide presets exist under `style-guide/<preset>/`

## Action

Invoke the `manga-director` agent with the user's theme as input. Pass through any `--patterns` flag.
