---
name: 4koma-compose
description: Use when generating one 4-panel manga plot variant from a theme. Produces structured plot.md with panel-by-panel breakdown, dialogue, and cast assignment. Called 4 times in parallel by manga-director with different style/cast variations.
---

# 4koma-compose

Generate one 4-panel manga plot from a theme prompt.

## Inputs

- `theme` (required) — the user's お題 (free text in Japanese)
- `pattern_id` (required) — one of `pattern-a`, `pattern-b`, `pattern-c`, `pattern-d`
- `cast_hint` (optional) — comma-separated character IDs to prefer (e.g. `imaizumi,sebastian`)
- `episode_dir` (required) — the absolute path to `episodes/<id>/`

## Cast catalog

Available characters (read from `characters/<id>/profile.md`):

- `i_kacho` — 株式会社ラインワークス 設計部 I課長、主人公格（氏名は意図的にイニシャル表記）
- `sebastian` — 社内専用AI執事 AI Agent 執事 セバスチャン、解説役、銀のトレイ

## Composition rules

- **1-2 characters per strip** (full cast: imaizumi + sebastian). Solo strips are also valid (e.g., sebastian-only POV episodes).
- **4 panels with 起承転結**:
  - Panel 1 (起): set up the situation
  - Panel 2 (承): develop / introduce a small twist
  - Panel 3 (転): unexpected turn / problem
  - Panel 4 (結): punchline / resolution / character moment
- Each panel needs: scene description, character actions, dialogue (if any).
- Dialogue should reflect each character's speech style (see profile.md).

## Variation strategy

Each of the 4 parallel calls (a/b/c/d) should produce a **meaningfully different** treatment:
- **pattern-a**: most literal interpretation of the theme
- **pattern-b**: shift the central character (different POV)
- **pattern-c**: change the gag structure (visual gag vs. wordplay vs. situational)
- **pattern-d**: experiment with tone or setting (e.g., shift to a dramatic, absurd, or quiet tone different from a/b/c)

## Output format

Write a single file: `<episode_dir>/patterns/<pattern_id>/plot.md`

```markdown
# <Episode title> — <pattern_id>

## Theme
<original theme text>

## Cast
- <character_id>
- <character_id>
- ...

**重要: 各行は `- <character_id>` の形式のみ（半角ハイフン+半角スペース+英小文字IDのみ）。日本語注釈・括弧・追加テキスト一切禁止。**

## Style preset suggestion
**重要: 直後の行はプリセットIDのみ（`shinkai_default` / `picturebook` / `ghibli_bg` のいずれか1つ）、他のテキスト混在禁止。**
<one of: shinkai_default | picturebook | ghibli_bg>
Reason: <one sentence>

## Panels

### Panel 1 (起)
**Scene:** <description in Japanese>
**Characters in shot:** <list>
**Action:** <description>
**Dialogue:**
- <character_name>: 「<line>」

### Panel 2 (承)
...same structure...

### Panel 3 (転)
...

### Panel 4 (結)
...
```

## How to invoke

This skill is invoked by the `manga-director` agent. Direct user invocation is not expected in Phase 1.

## Constraints

- No real customer products or company logos other than LINEWORKS-approved.
- Avoid sensitive workplace topics (overtime complaints, internal politics, etc.) unless the theme explicitly calls for them.
- Keep humor warm and inclusive, suitable for a corporate official account.
- LINEWORKSロゴ・社名言及時は「株式会社ラインワークス（千葉）の産業用ロボットメーカー」文脈を明示し、同名グループウェア「LINE WORKS」との混同を回避すること。
