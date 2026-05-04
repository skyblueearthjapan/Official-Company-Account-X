# 株式会社ラインワークス 公式X運用ワークスペース

This is the workspace and Claude Code plugin for operating LINEWORKS' official X (Twitter) account.

## Overview

Two content streams:
1. **Weekly 4-koma manga** (watercolor-style, recurring cast: 今泉課長 / セバスチャン)
2. **Ad-hoc news posts** (recruitment, awards, patents, etc.) — Phase 3

Currently in **Phase 1**: building the 4-koma production pipeline.

## Quick Start

1. Read [`docs/superpowers/specs/2026-05-03-x-account-ops-design.md`](docs/superpowers/specs/2026-05-03-x-account-ops-design.md)
2. Read [`docs/runbooks/weekly-4koma-flow.md`](docs/runbooks/weekly-4koma-flow.md)
3. Open Claude Code in this folder
4. Type: `/new-4koma "今週は新工場の食堂でセバスチャンが配膳ロボとぶつかる話"`

## Folder Layout

| Folder | Purpose |
|--------|---------|
| `characters/` | Character sheets (profile, anchor prompt, reference images) |
| `style-guide/` | Watercolor style presets (shinkai_default / picturebook / ghibli_bg) |
| `episodes/` | Per-episode artifacts (4 patterns + final) |
| `news/` | News posts (Phase 3) |
| `analytics/` | X analytics output (Phase 3) |
| `docs/` | Specs, plans, runbooks, ADRs |
| `.claude/plugins/lineworks-x-ops/` | The Claude Code plugin |

## Phase Status

- ✅ Phase 0: Design spec complete
- 🚧 Phase 1: Production pipeline (in progress)
- ⏳ Phase 2: Sample episodes + president approval
- ⏳ Phase 3: X API integration & launch

## Contact

今泉課長 (設計部) — 株式会社ラインワークス
