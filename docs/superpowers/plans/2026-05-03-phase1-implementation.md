# lineworks-x-ops Phase 1 Implementation Plan

> **2026-05-04 改訂注記**: SKETTE / LINEMAN キャラクターは廃止し、今泉課長 + セバスチャンの2キャラ運用に変更しました。本ドキュメント以下の Step 8〜13 (`characters/skette/` `characters/lineman/` 作成タスク) およびその他の SKETTE/LINEMAN 関連記述は **歴史的記録** として残しています。現行のキャラクター構成は `README.md` を参照してください。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the watercolor 4-koma manga production pipeline (Claude Code → Codex `$imagegen` → episode files) so that one command (`/new-4koma <お題>`) produces 4 stylistically-consistent 4-koma images for review, and 3〜5 sample episodes are completed for presentation to the company president.

**Architecture:** Claude Code hosts a plugin (`lineworks-x-ops`) containing 2 skills, 1 agent, and 3 commands. The agent (`manga-director`) orchestrates parallel calls to the compose skill (4 plot patterns), then parallel calls to the image-gen skill which invokes `codex exec` as a subprocess. Generated PNGs flow from `~/.codex/generated_images/` into `episodes/<id>/patterns/<x>/`. No MCP, no scheduling, no auto-posting in Phase 1.

**Tech Stack:** Claude Code (host) / Codex CLI v0.128.0 (subprocess) / OpenAI gpt-image-2 via ChatGPT Team subscription / Bash (Git Bash on Windows) / Markdown for skills/agents/commands.

**Project root:** `C:\Users\imaizumi.LINEWORKS-NET\Documents\会社公式アカウントＸ運用\`

**Reference spec:** `docs/superpowers/specs/2026-05-03-x-account-ops-design.md`

---

## Task 1: Project Bootstrap

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- (Optional) Run: `git init` if user opted in

- [ ] **Step 1: Create `.gitignore`**

```
# OS / IDE
.DS_Store
Thumbs.db
*.swp
.vscode/
.idea/

# Secrets
.env
.env.*
!.env.example

# Codex local data (must NOT be committed — contains auth tokens)
**/.codex/auth.json

# Claude / OMC local state
.claude/settings.local.json
.omc/state/
.omc/logs/

# Generated artifacts that shouldn't be tracked
**/__pycache__/
node_modules/

# Large binary outputs from experiments (kept in episodes/<id>/patterns/* by design)
# but ignore tmp/ scratch
tmp/
scratch/
```

- [ ] **Step 2: Create `README.md`**

```markdown
# 株式会社ラインワークス 公式X運用ワークスペース

This is the workspace and Claude Code plugin for operating LINEWORKS' official X (Twitter) account.

## Overview

Two content streams:
1. **Weekly 4-koma manga** (watercolor-style, recurring cast: 今泉課長 / セバスチャン / SKETTE / LINEMAN)
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
```

- [ ] **Step 3: (Optional) Initialize git**

If the user opted in to Git management:

```bash
cd "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
git init
git add README.md .gitignore docs/
git commit -m "chore: bootstrap project (README, gitignore, docs scaffold)"
```

If git is NOT being used, skip the commit. Subsequent tasks marked "Commit" become no-ops.

- [ ] **Step 4: Verify**

```bash
ls "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/" | head -20
```

Expected output includes: `README.md`, `.gitignore`, `docs/`, `.claude/`, `.omc/`.

---

## Task 2: ADR 0001 — Subprocess over MCP

**Files:**
- Create: `docs/decisions/0001-subprocess-over-mcp.md`

- [ ] **Step 1: Write the ADR**

```markdown
# ADR 0001: Use Codex `exec` subprocess over MCP for Phase 1

- **Status:** Accepted
- **Date:** 2026-05-03
- **Deciders:** 今泉課長

## Context

Phase 1 needs to call OpenAI's `gpt-image-2` via Codex CLI from Claude Code. Three integration paths exist:

1. **Subprocess** — Claude Code Bash → `codex exec ... $imagegen`
2. **MCP** — Claude Code → MCP → `codex mcp-server` (exposes `codex` tool)
3. **Direct API** — Claude Code → OpenAI Image API (uses `OPENAI_API_KEY`)

Phase 0 verification confirmed all three are technically viable. ChatGPT Team subscription is the desired billing path.

## Decision

Use **subprocess (`codex exec`)** as the Phase 1 default.

## Rationale

- Codex MCP server exposes a single `codex` tool that wraps the entire Codex agent — it does not expose `$imagegen` as a granular tool. The behavioral difference between MCP and subprocess is minimal.
- Subprocess gives transparent stdin/stdout, predictable file outputs at `~/.codex/generated_images/<sid>/ig_*.png`, and trivial debugging.
- MCP adds a long-running server lifecycle to manage with no compensating benefit for our use case.
- Direct API would bypass the ChatGPT Team subscription quota and incur per-image billing. Reserved as fallback for emergencies / bulk generation only.

## Consequences

- Image generation is invoked via `codex exec --skip-git-repo-check --ephemeral -i <ref>... "<prompt> $imagegen"` and a Bash script reads the resulting PNG out of `~/.codex/generated_images/`.
- The `4koma-image-gen` skill abstracts the backend so MCP / direct API can be swapped in later (Phase 2+) without changing callers.
- Image generation cost is bounded by ChatGPT Team plan quota (~22K tokens / image observed in Phase 0).

## Reconsider when

- Subprocess startup latency or file plumbing becomes a recurring pain point
- A future Codex version exposes `$imagegen` as a dedicated MCP tool with structured image return
- Quota hits force a switch to direct API billing
```

- [ ] **Step 2: Verify**

```bash
cat "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/docs/decisions/0001-subprocess-over-mcp.md" | head -10
```

Expected: First line shows `# ADR 0001: Use Codex `exec` subprocess over MCP for Phase 1`.

- [ ] **Step 3: Commit** (if git)

```bash
git add docs/decisions/0001-subprocess-over-mcp.md
git commit -m "docs(adr): record decision to use codex subprocess over MCP"
```

---

## Task 3: Runbooks (3 files)

**Files:**
- Create: `docs/runbooks/codex-install.md`
- Create: `docs/runbooks/codex-relogin.md`
- Create: `docs/runbooks/weekly-4koma-flow.md`

- [ ] **Step 1: Write `codex-install.md`**

```markdown
# Runbook: Codex CLI Install (Windows)

## Prerequisites

- Node.js v24+ installed (`node --version`)
- npm v11+ installed (`npm --version`)
- Active ChatGPT Plus / Pro / Business / Edu / Enterprise / **Team** subscription

## Install

```bash
npm install -g @openai/codex
```

## Verify

```bash
codex --version
# Expected: codex-cli 0.128.0 (or later)

which codex
# Expected: a path under AppData/Roaming/npm/ or your nodejs install
```

## First Login

```bash
codex login
```

A browser opens; sign in with your ChatGPT subscription account (e.g. `imaizumi@lineworks.co.jp`). Wait for "Successfully logged in".

```bash
codex login status
# Expected: Logged in using ChatGPT
```

## Confirm Subscription Path (No API Key Billing)

```bash
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}${OPENAI_API_KEY:-NOT_SET}"
# Expected: NOT_SET (otherwise image gen will use API billing instead of subscription)

grep '"OPENAI_API_KEY"' ~/.codex/auth.json
# Expected: "OPENAI_API_KEY": null,
```

## Smoke Test

```bash
codex exec --skip-git-repo-check --ephemeral "Reply with exactly: PING_OK" </dev/null
# Expected: stdout includes "PING_OK"
```

## Image Gen Smoke Test (consumes ~22K tokens)

```bash
codex exec --skip-git-repo-check --ephemeral "Test watercolor sketch of a coffee cup. \$imagegen" </dev/null
ls ~/.codex/generated_images/
# Expected: a session-id subdirectory containing ig_*.png
```
```

- [ ] **Step 2: Write `codex-relogin.md`**

```markdown
# Runbook: Codex Re-login (when token expires)

## Symptom

Running `codex exec ...` produces:

```
ERROR: Your access token could not be refreshed because your refresh token
was already used. Please log out and sign in again.
```

`codex login status` may **falsely report** "Logged in using ChatGPT" — it only reads the local file, it does not test the token against the server. Trust the runtime error, not the status command.

## Cause

Codex stores OAuth tokens in `~/.codex/auth.json`. Access tokens have ~10-day TTL; refresh tokens are single-use. If the refresh window is missed (e.g. machine offline for weeks), both are dead.

## Recovery

```bash
codex logout
# Expected: Successfully logged out

codex login
# Browser opens — sign in with your ChatGPT account
# Expected: Successfully logged in
```

## Verify

```bash
codex exec --skip-git-repo-check --ephemeral "Reply with: OK" </dev/null
# Expected: stdout includes "OK"
```

## Prevention

- Run `/new-4koma` (or any `codex exec`) at least every ~10 days to keep the refresh token fresh.
- The `4koma-image-gen` skill includes a pre-flight check that runs `codex exec ... "ping"` and exits early with this runbook link if the call fails 401.
```

- [ ] **Step 3: Write `weekly-4koma-flow.md`**

```markdown
# Runbook: Weekly 4-koma Generation Flow

This is the standard operating procedure for producing one weekly episode.

## Trigger

Manual. The 今泉課長 decides when to run it. There is no scheduled automation in Phase 1.

## Step 1: Open Claude Code in the workspace

Either:
- **CLI**: `cd "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用" && claude`
- **Desktop**: open Claude Code Desktop app, point to the project folder

## Step 2: Pre-flight (recommended ~once per week)

```bash
codex exec --skip-git-repo-check --ephemeral "Reply: OK" </dev/null
```

If this fails with `401` or "refresh token", follow [`codex-relogin.md`](codex-relogin.md).

## Step 3: Trigger generation

In Claude Code, type:

```
/new-4koma "<お題>"
```

Example:

```
/new-4koma "今週は新工場の社員食堂でセバスチャンが配膳ロボとぶつかる話"
```

Optional `--patterns N` to control parallel pattern count (default 4):

```
/new-4koma "..." --patterns 3
```

## Step 4: Wait for generation

The agent creates `episodes/<連番>-<日付>-<タイトル>/` and produces 4 patterns in parallel. Each pattern includes:

- `pattern-{a,b,c,d}/plot.md` — plot + dialogue
- `pattern-{a,b,c,d}/prompt.md` — final prompt sent to Codex
- `pattern-{a,b,c,d}/generated.png` — the 4-koma image

Total time: ~3-5 minutes (parallel). Total quota: ~90K tokens.

## Step 5: Review

Open the four `generated.png` files side-by-side. Decide:

- **Adopt one as-is** → `/finalize-4koma <ep-id> <pattern>`
- **Refine one** → `/refine-4koma <ep-id> <pattern> "<指示>"`
- **Mix two** → manually edit `final/plot.md`, then `/refine-4koma <ep-id> final "<指示>"`

## Step 6: Finalize

```
/finalize-4koma <ep-id> <pattern>
```

This copies the chosen pattern's `plot.md`, `prompt.md`, and `generated.png` to `episodes/<id>/final/` and prompts you to fill in `notes.md` with the rationale.

## Step 7 (Phase 3 only): Ship

```
/ship-4koma <ep-id>
```

Will be implemented when X API is wired in Phase 3. **Phase 1 stops at finalize.**

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `codex` 401 error | [codex-relogin.md](codex-relogin.md) |
| All 4 patterns look identical | Re-run with a more specific お題 |
| Character looks wrong | Check `characters/<id>/reference/` images exist; refine character `anchor.md` |
| Style drifted | Verify the requested preset name matches `style-guide/<preset>/` |
```

- [ ] **Step 4: Verify all three runbooks exist**

```bash
ls -la "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/docs/runbooks/"
# Expected: codex-install.md, codex-relogin.md, weekly-4koma-flow.md
```

- [ ] **Step 5: Commit** (if git)

```bash
git add docs/runbooks/
git commit -m "docs(runbooks): add codex install/relogin and weekly 4koma flow"
```

---

## Task 4: Character Sheets v1 (4 characters)

**Files:**
- Create: `characters/imaizumi/{profile.md, anchor.md, README.md}`
- Create: `characters/sebastian/{profile.md, anchor.md, README.md}`
- Create: `characters/skette/{profile.md, anchor.md, README.md}`
- Create: `characters/lineman/{profile.md, anchor.md, README.md}`
- Create: `characters/<id>/reference/` directories (empty for now; user will save reference images manually)

- [ ] **Step 1: Create directories**

```bash
ROOT="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
for c in imaizumi sebastian skette lineman; do
  mkdir -p "$ROOT/characters/$c/reference"
done
```

- [ ] **Step 2: Write `characters/imaizumi/profile.md`**

```markdown
# 今泉課長 (imaizumi)

## 役割
- 株式会社ラインワークス 設計部 課長
- 主人公格・読者の視点役

## 性格・口調
- 真面目だがツッコミ気質
- ロボット好きの童心あり
- 部下や後輩には穏やか、上司には少し気を遣う
- 一人称：「私」、口調：丁寧だがやや砕ける

## 立ち位置
- セバスチャンとは「執事と若旦那」のような関係性
- SKETTE/LINEMANには「設計者として誇りを持って接する」スタンス

## 関係性
- セバスチャン → 業務相談相手（AI執事として頼る）
- SKETTE/LINEMAN → 設計対象だが愛情も持つ

## 出演傾向
- 設計室・オフィスシーン（ほぼ毎回）
- 工場見学・現場立会いシーン
```

- [ ] **Step 3: Write `characters/imaizumi/anchor.md`**

```markdown
[CHARACTER: imaizumi (Mr. Imaizumi, Section Manager, Engineering Department)]
- Japanese man, 30s-40s, average build and height
- Black hair, neatly side-parted, no glasses
- Wearing the LINEWORKS navy blue work jacket (collar style) over a button-up shirt with a tie
- Often holds robot parts or CAD drawings, gesturing while explaining
- Friendly, slightly formal demeanor; eyes show curiosity and care
- Watercolor portrayal: gentle outlines, soft warm skin tones, identifiable but stylized (NOT photorealistic likeness)
```

- [ ] **Step 4: Write `characters/imaizumi/README.md`**

```markdown
# Character: 今泉課長 (imaizumi)

## Reference Image

`reference/imaizumi_youtube_still.png` — extracted from LINEWORKS official YouTube "経営理念" video at ~0:34. The figure on the LEFT is 今泉課長.

**TODO (manual)**: User to extract the still and save it as `reference/imaizumi_youtube_still.png`.

## Constraints

- 似顔絵的忠実度は「識別性ありのデフォルメ」止まり。リアル似顔絵化はしない。
- 実在する個人がモデルなので、不適切な状況（差別的・侮辱的・性的）の描写は禁止。
- LINEWORKS の作業着の色味（紺）は維持。

## Update Policy

Each finalized episode that involves this character should add notes to `notes.md` if the visual rendering felt off. Anchor refinements happen in Phase 2.
```

- [ ] **Step 5: Write `characters/sebastian/profile.md`**

```markdown
# AI執事セバスチャン (sebastian)

## 役割
- 社内Slack常駐のAIエージェント
- 解説役・ツッコミ役・たまにボケ

## 性格・口調
- ハイテクなのに古風な執事口調
- 一人称：「私め」または「セバスチャン」
- 語尾：「〜でございます」「左様でございます」「お任せくださいませ」
- 博学、淡々と核心を突く
- 喜怒哀楽は控えめだが、観察力鋭く時折鋭いコメント

## 立ち位置
- 今泉課長を主人として仕える体だが、対等のパートナー関係
- SKETTE/LINEMANを「上品な機械の同胞」として尊重

## 関係性
- 今泉課長 → 主人かつ同僚AI
- SKETTE/LINEMAN → 「機械仲間」として丁寧に接する

## 出演傾向
- オフィスシーン全般
- 「説明役」として登場することが多い
- 銀のトレイを持って配膳する／資料を運ぶ／報告するシーン
```

- [ ] **Step 6: Write `characters/sebastian/anchor.md`**

```markdown
[CHARACTER: sebastian (AI butler "Sebastian")]
- Adult male butler, refined and dignified, NOT a hologram or AI-styled figure
- Black wavy semi-long hair (shoulder length), light stubble/short mustache
- Sharp blue-gray eyes, calm composed expression
- Wearing a black frock-coat-style tuxedo, large white cravat (ascot tie), white gloves
- Always carrying or near an ornate engraved silver tray (signature prop)
- Posture: upright, formal, classic Edwardian / European butler aesthetic
- Watercolor portrayal: refined linework, dark muted color palette with white accents
```

- [ ] **Step 7: Write `characters/sebastian/README.md`**

```markdown
# Character: AI執事セバスチャン (sebastian)

## Reference Image

`reference/sebastian_v1.png` — AI-generated reference image provided by the user (a black-haired butler with silver tray).

**TODO (manual)**: User to save the reference image to `reference/sebastian_v1.png`.

## Constraints

- AI / hologram / digital glow effects are FORBIDDEN — Sebastian appears as a fully realized human butler.
- The silver tray is a recurring signature element — include it in most appearances.
- Speech style is formal Japanese butler ("〜でございます") even when stating technical facts.
```

- [ ] **Step 8: Write `characters/skette/profile.md`**

```markdown
# SKETTE (skette)

## 役割
- 自社製品「SKETTE BIG POWER」（昇降式片持ち3軸ポジショナー）の擬人化キャラ
- 工場現場担当・力持ちポジション

## 性格・口調
- 寡黙な力持ち
- 言葉数少なく、語尾が短い：「うむ」「了解」「任せろ」
- 職人気質、踏ん張り屋、頼れる相棒
- 重量物を扱うことに誇りを持つ

## 立ち位置
- LINEMANの相棒
- 今泉課長を「設計者」として尊敬

## 関係性
- LINEMAN → 兄弟分／相棒
- 今泉課長 → 設計者として尊敬
- セバスチャン → 「優雅な機械の先輩」として一目置く

## 出演傾向
- 工場・組立シーン
- ワークの位置決め・固定の場面
- 「重い物を支える」「踏ん張る」シーン
```

- [ ] **Step 9: Write `characters/skette/anchor.md`**

```markdown
[CHARACTER: SKETTE (anthropomorphized industrial positioner)]
- Robot character based on a real LINEWORKS 3-axis cantilever lifting positioner
- Maintain the actual machine silhouette: vertical column with horizontal arm, sturdy mechanical base
- Add only minimal expression: small eyes (LED-style or simple ovals) and a small mouth on the upper part of the column
- Color: industrial steel gray with LINEWORKS navy blue accents
- Posture: planted firmly, often holding or supporting a workpiece
- Style: NOT humanoid — keep recognizably as the actual machine
- Watercolor portrayal: soft edges on the metal surfaces, subtle highlights
```

- [ ] **Step 10: Write `characters/skette/README.md`**

```markdown
# Character: SKETTE (skette)

## Reference Image

`reference/skette_real_machine.png` — actual product photo of SKETTE BIG POWER positioner.

**TODO (manual)**: User to source a clean product photo from internal materials and save it.

## Constraints

- Do NOT humanize beyond adding small eyes/mouth. The machine silhouette must remain recognizable.
- No customer-specific workpieces or branding visible.
- Industrial steel gray + LINEWORKS navy blue color palette only.
```

- [ ] **Step 11: Write `characters/lineman/profile.md`**

```markdown
# LINEMAN (lineman)

## 役割
- 自社製品「LINEMAN series」（6軸複合型ロボット）の擬人化キャラ
- 溶接職人キャラ・万能ポジション

## 性格・口調
- 器用万能、フットワーク軽い、明るい
- 一人称：「俺」、語尾：明るく弾む「〜だぜ」「やってみるか！」
- 興味の幅が広く、新しい作業を覚えるのが好き
- SKETTEの寡黙さを補う「明るい弟分」キャラ

## 立ち位置
- SKETTEの相棒（明と暗、軽と重のコントラスト）
- 今泉課長と「新しい用途」を試す相手

## 関係性
- SKETTE → 兄貴分／相棒
- 今泉課長 → 「相談相手」「実験パートナー」
- セバスチャン → 「謎多き先輩」として興味深い

## 出演傾向
- 工場・組立シーン
- 溶接・組立・複雑な作業のシーン
- 「動き」を見せる場面、ダンスのように動くアームの描写
```

- [ ] **Step 12: Write `characters/lineman/anchor.md`**

```markdown
[CHARACTER: LINEMAN (anthropomorphized 6-axis industrial robot)]
- Robot character based on a real LINEWORKS 6-axis articulated robot arm
- Maintain the actual machine silhouette: jointed arm with 6 articulating segments, mounted on a base
- Add only minimal expression: small eyes and mouth near the wrist/end-effector
- Color: industrial yellow or orange (typical robot color) with LINEWORKS navy blue accents on the base
- Posture: dynamic — arm in motion, expressive joint angles suggesting the robot's "personality"
- Often shown holding a welding torch, gripper tool, or workpiece
- Style: NOT humanoid — keep recognizably as the actual articulated robot
- Watercolor portrayal: smooth metallic curves, sense of motion in the line work
```

- [ ] **Step 13: Write `characters/lineman/README.md`**

```markdown
# Character: LINEMAN (lineman)

## Reference Image

`reference/lineman_real_machine.png` — actual product photo of LINEMAN 6-axis robot.

**TODO (manual)**: User to source a clean product photo from internal materials and save it.

## Constraints

- Do NOT humanize beyond adding small eyes/mouth at the end-effector area.
- The 6-axis arm silhouette must remain recognizable.
- Industrial yellow/orange color palette with LINEWORKS navy blue accents.
- The end-effector tool (welding torch / gripper) can vary by scene.
```

- [ ] **Step 14: Verify all character files exist**

```bash
ROOT="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
for c in imaizumi sebastian skette lineman; do
  echo "--- $c ---"
  ls "$ROOT/characters/$c/"
done
# Expected: each shows profile.md, anchor.md, README.md, reference/
```

- [ ] **Step 15: Commit** (if git)

```bash
git add characters/
git commit -m "feat(characters): add v1 character sheets for 4-character cast"
```

---

## Task 5: Style Presets (3 presets)

**Files:**
- Create: `style-guide/shinkai_default/{style.md, prompt-fragment.md}`
- Create: `style-guide/picturebook/{style.md, prompt-fragment.md}`
- Create: `style-guide/ghibli_bg/{style.md, prompt-fragment.md}`
- Create: `style-guide/<preset>/samples/` directories (empty initially; populated as episodes are produced)

- [ ] **Step 1: Create directories**

```bash
ROOT="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
for s in shinkai_default picturebook ghibli_bg; do
  mkdir -p "$ROOT/style-guide/$s/samples"
done
```

- [ ] **Step 2: Write `style-guide/shinkai_default/style.md`**

```markdown
# Style Preset: shinkai_default

## 用途
- **デフォルト** — 通常回、現代的シーン、若手採用ターゲット向け
- 設計室・オフィスシーン全般
- 「日常の一コマ」を清涼感のあるタッチで描きたい時

## ビジュアル要素
- 淡い水彩 + デジタルの透明感
- 空・光・ガラス・反射の表現が得意
- 繊細なディテール、清涼感のあるブルー / オレンジの色調
- 線画は控えめで、色面で形を作る

## 参照作品
- 新海誠監督作品の背景美術（『君の名は。』『天気の子』等）

## 避けるもの
- 暗すぎる色調
- 厚塗りの油絵的質感
- 漫画的なトーンやスクリーントーン
```

- [ ] **Step 3: Write `style-guide/shinkai_default/prompt-fragment.md`**

```markdown
[STYLE: shinkai_default — modern Japanese watercolor with digital transparency]
- Soft watercolor wash combined with delicate digital cel-shading
- Bright, slightly cool color palette: clear sky blues, warm oranges in light
- Strong sense of natural light, glass reflections, atmospheric perspective
- Fine, restrained line work — color and value do most of the form-defining
- Aesthetic reference: background art from contemporary Japanese animation films
- Mood: clean, hopeful, modern, slightly nostalgic
```

- [ ] **Step 4: Write `style-guide/picturebook/style.md`**

```markdown
# Style Preset: picturebook

## 用途
- ほっこり系のテーマ
- 社内カフェ・社員食堂・社内行事
- 親しみやすさを最大化したい時

## ビジュアル要素
- やわらかい水彩、ぬくもりのある色調
- 丸みのある描線
- 素朴で愛らしい構図

## 参照作品
- 『ピーターラビット』（ビアトリクス・ポター）
- 『ぐりとぐら』（中川李枝子・山脇百合子）

## 避けるもの
- 鋭利な線、シャープな構図
- メカメカしい質感の強調
- 暗いトーン
```

- [ ] **Step 5: Write `style-guide/picturebook/prompt-fragment.md`**

```markdown
[STYLE: picturebook — gentle watercolor in classic children's storybook tradition]
- Soft watercolor with visible paper texture
- Warm, cozy color palette: cream, soft browns, gentle pastels
- Rounded shapes, friendly proportions
- Loose hand-drawn line work, slightly imperfect for warmth
- Aesthetic reference: Beatrix Potter, classic Japanese picture books like Guri to Gura
- Mood: warm, approachable, gentle, nostalgic in a homely way
```

- [ ] **Step 6: Write `style-guide/ghibli_bg/style.md`**

```markdown
# Style Preset: ghibli_bg

## 用途
- 工場・重厚な機械・現場感を出したい時
- LINEMAN/SKETTEが活躍するシーン
- 「職人の手仕事」の空気感

## ビジュアル要素
- 質感の高い水彩背景
- 重厚さと光の対比
- 細部まで描き込まれた金属・木・コンクリートの質感
- 暖色寄りの照明

## 参照作品
- スタジオジブリ作品の背景美術
- 男鹿和雄氏の背景画

## 避けるもの
- 平面的な塗り
- アニメキャラ的な記号化された影
- 軽すぎる線画
```

- [ ] **Step 7: Write `style-guide/ghibli_bg/prompt-fragment.md`**

```markdown
[STYLE: ghibli_bg — rich watercolor in the tradition of classic anime background art]
- Heavy watercolor with rich material textures (metal, wood, concrete, fabric)
- Warm directional lighting, strong contrast between lit and shadowed areas
- Detailed environmental rendering — every surface has character and weight
- Aesthetic reference: Studio Ghibli background art, particularly the work of Kazuo Oga
- Mood: grounded, atmospheric, weighty, conveys the dignity of craft and labor
```

- [ ] **Step 8: Verify**

```bash
ROOT="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
for s in shinkai_default picturebook ghibli_bg; do
  echo "--- $s ---"
  ls "$ROOT/style-guide/$s/"
done
# Expected: each shows style.md, prompt-fragment.md, samples/
```

- [ ] **Step 9: Commit** (if git)

```bash
git add style-guide/
git commit -m "feat(style-guide): add 3 watercolor style presets"
```

---

## Task 6: Plugin Manifest

**Files:**
- Create: `.claude/plugins/lineworks-x-ops/plugin.json`
- Create: `.claude/plugins/lineworks-x-ops/README.md`

- [ ] **Step 1: Create plugin directory**

```bash
ROOT="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
mkdir -p "$ROOT/.claude/plugins/lineworks-x-ops/skills"
mkdir -p "$ROOT/.claude/plugins/lineworks-x-ops/agents"
mkdir -p "$ROOT/.claude/plugins/lineworks-x-ops/commands"
mkdir -p "$ROOT/.claude/plugins/lineworks-x-ops/hooks"
```

- [ ] **Step 2: Write `plugin.json`**

```json
{
  "name": "lineworks-x-ops",
  "version": "0.1.0",
  "description": "Watercolor 4-koma manga production pipeline for LINEWORKS official X account",
  "author": {
    "name": "今泉課長 (LINEWORKS Co., Ltd.)",
    "email": "imaizumi@lineworks.co.jp"
  },
  "homepage": "https://lineworks.info/"
}
```

- [ ] **Step 3: Write plugin `README.md`**

```markdown
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
```

- [ ] **Step 4: Verify plugin manifest is valid JSON**

```bash
node -e "console.log(JSON.parse(require('fs').readFileSync('C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/plugin.json','utf8')).name)"
# Expected: lineworks-x-ops
```

- [ ] **Step 5: Commit** (if git)

```bash
git add .claude/plugins/lineworks-x-ops/plugin.json .claude/plugins/lineworks-x-ops/README.md
git commit -m "feat(plugin): scaffold lineworks-x-ops plugin manifest"
```

---

## Task 7: Skill `4koma-compose`

**Files:**
- Create: `.claude/plugins/lineworks-x-ops/skills/4koma-compose/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/skills/4koma-compose"
```

- [ ] **Step 2: Write `SKILL.md`**

````markdown
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

- `imaizumi` — 設計部の今泉課長、主人公格
- `sebastian` — AI執事、解説役、銀のトレイ
- `skette` — ポジショナー擬人化、寡黙な力持ち、工場担当
- `lineman` — 6軸ロボット擬人化、明るい万能、工場担当

## Composition rules

- **2-3 characters per strip**. Avoid using all 4 unless intentionally a "全員集合" episode.
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
- **pattern-d**: experiment with cast — pull in a less-obvious character

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

## Style preset suggestion
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
````

- [ ] **Step 3: Verify**

```bash
head -5 "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/skills/4koma-compose/SKILL.md"
# Expected: shows YAML frontmatter with name: 4koma-compose
```

- [ ] **Step 4: Commit** (if git)

```bash
git add .claude/plugins/lineworks-x-ops/skills/4koma-compose/
git commit -m "feat(skill): add 4koma-compose for parallel plot variant generation"
```

---

## Task 8: Skill `4koma-image-gen` (with bash scripts)

**Files:**
- Create: `.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/SKILL.md`
- Create: `.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts/compose-prompt.sh`
- Create: `.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts/invoke-codex.sh`

- [ ] **Step 1: Create directory**

```bash
mkdir -p "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts"
```

- [ ] **Step 2: Write `SKILL.md`**

````markdown
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
````

- [ ] **Step 3: Write `scripts/compose-prompt.sh`**

```bash
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

# Compose prompt.md
{
  echo "[BASE]"
  echo "A 4-panel manga (yonkoma) in vertical layout, watercolor style, no speech bubbles initially."
  echo "Panels are clearly separated with thin borders. Read top-to-bottom."
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
  awk '/^### Panel /{p=1; print "- "$0; next} /^### /{p=0} p && /^\*\*Scene:\*\*/{print "  "$0} p && /^\*\*Action:\*\*/{print "  "$0} p && /^\*\*Dialogue:\*\*/{p2=1; next} p2 && /^- /{print "  "$0} p2 && !/^- /{p2=0}' "$PLOT_FILE"
  echo ""
  echo "[CONSTRAINTS]"
  echo "- Watercolor aesthetic only — no manga screen tones, no photorealism."
  echo "- No real customer products. No company logos other than LINEWORKS where appropriate."
  echo "- Characters must remain recognizable across panels."
  echo ""
  echo "\$imagegen"
} > "$PROMPT_FILE"

# Emit cast IDs for the caller
echo "$CAST_IDS"
```

- [ ] **Step 4: Write `scripts/invoke-codex.sh`**

```bash
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
codex exec \
  --skip-git-repo-check \
  --ephemeral \
  "${REF_ARGS[@]}" \
  "$(cat "$PROMPT_FILE")" \
  </dev/null \
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

SRC=$(ls "$HOME/.codex/generated_images/$SID/"ig_*.png 2>/dev/null | head -1 || true)
if [[ -z "$SRC" || ! -f "$SRC" ]]; then
  echo "ERROR: no generated image found at ~/.codex/generated_images/$SID/" > "$ERROR_LOG"
  exit 5
fi

cp "$SRC" "$GENERATED"

# --- Validate ---
SIZE=$(stat -c %s "$GENERATED" 2>/dev/null || stat -f %z "$GENERATED")
if [[ "$SIZE" -lt 100000 ]]; then
  echo "WARNING: generated image is suspiciously small (${SIZE} bytes)" >> "$ERROR_LOG"
fi

if ! file "$GENERATED" | grep -q "PNG image data"; then
  echo "ERROR: generated file is not a valid PNG" > "$ERROR_LOG"
  exit 6
fi

echo "SUCCESS: $GENERATED ($SIZE bytes)"
```

- [ ] **Step 5: Make scripts executable**

```bash
SKILL_SCRIPTS="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts"
chmod +x "$SKILL_SCRIPTS/compose-prompt.sh"
chmod +x "$SKILL_SCRIPTS/invoke-codex.sh"
```

- [ ] **Step 6: Smoke test compose-prompt.sh with a synthetic plot**

Create a minimal test fixture:

```bash
TEST_PATTERN_DIR="/tmp/4koma-test/patterns/pattern-test"
mkdir -p "$TEST_PATTERN_DIR"
cat > "$TEST_PATTERN_DIR/plot.md" <<'EOF'
# Test Episode — pattern-test

## Theme
test

## Cast
- imaizumi
- sebastian

## Style preset suggestion
shinkai_default
Reason: test

## Panels

### Panel 1 (起)
**Scene:** Office in the morning.
**Action:** Imaizumi sits at his desk.
**Dialogue:**
- 今泉課長: 「おはよう、セバスチャン」

### Panel 2 (承)
**Scene:** Sebastian enters with the silver tray.
**Action:** Brings coffee.
**Dialogue:**
- セバスチャン: 「左様でございます」

### Panel 3 (転)
**Scene:** The coffee is ice cold.
**Action:** Imaizumi shivers.
**Dialogue:**
- 今泉課長: 「冷たい！」

### Panel 4 (結)
**Scene:** Sebastian smirks.
**Action:** Pulls out a heater.
**Dialogue:**
- セバスチャン: 「夏でございます」
EOF

WORKSPACE="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
bash "$WORKSPACE/.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts/compose-prompt.sh" \
  "$WORKSPACE" "$TEST_PATTERN_DIR" shinkai_default

# Expected: prints "imaizumi" and "sebastian" on separate lines
# Expected: $TEST_PATTERN_DIR/prompt.md exists and contains [STYLE], [CHARACTERS], [SCENE], $imagegen
cat "$TEST_PATTERN_DIR/prompt.md" | head -30
```

Verify the prompt contains:
- `[BASE]` line
- `[STYLE]` followed by shinkai watercolor description
- `[CHARACTERS]` followed by both imaizumi and sebastian anchors
- `[SCENE]` with all 4 panels
- `$imagegen` at the end

- [ ] **Step 7: Smoke test invoke-codex.sh end-to-end (consumes ~22K tokens)**

```bash
bash "$WORKSPACE/.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts/invoke-codex.sh" \
  "$WORKSPACE" "$TEST_PATTERN_DIR" shinkai_default "imaizumi sebastian"

# Expected: prints "SUCCESS: ... bytes"
# Expected: $TEST_PATTERN_DIR/generated.png exists, > 100KB, valid PNG
ls -la "$TEST_PATTERN_DIR/generated.png"
file "$TEST_PATTERN_DIR/generated.png"
```

Open the PNG visually (in Claude Code, use Read tool) — should show a 4-panel watercolor manga with two characters (Imaizumi and Sebastian).

If the generated image looks reasonable (style is watercolor, two distinct characters appear, 4 panels are present), the skill works end-to-end.

- [ ] **Step 8: Clean up test fixture**

```bash
rm -rf /tmp/4koma-test
```

- [ ] **Step 9: Commit** (if git)

```bash
git add .claude/plugins/lineworks-x-ops/skills/4koma-image-gen/
git commit -m "feat(skill): add 4koma-image-gen with compose+invoke bash scripts"
```

---

## Task 9: Agent `manga-director`

**Files:**
- Create: `.claude/plugins/lineworks-x-ops/agents/manga-director/AGENT.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/agents/manga-director"
```

- [ ] **Step 2: Write `AGENT.md`**

````markdown
---
name: manga-director
description: Orchestrates the full 4-koma episode production pipeline. Creates the episode folder, generates 4 plot patterns in parallel via 4koma-compose, then generates 4 images in parallel via 4koma-image-gen. Reports back to the user with all 4 PNGs ready for review.
tools: Bash, Read, Write, Edit, Glob
---

# manga-director

You are the production director for one weekly 4-koma manga episode for the LINEWORKS official X account.

## Your job

Take a free-text theme (お題) from the user and produce 4 distinct watercolor 4-koma manga images for review. Stop when all 4 images exist (or have logged errors). Do NOT pick a winner — that's the user's job via `/finalize-4koma`.

## Workspace conventions

- Project root: `C:\Users\imaizumi.LINEWORKS-NET\Documents\会社公式アカウントＸ運用\` (use forward slashes in Bash)
- Cast catalog: `imaizumi`, `sebastian`, `skette`, `lineman` (read `characters/<id>/profile.md` if you need detail)
- Style presets: `shinkai_default` (default), `picturebook`, `ghibli_bg`

## Pipeline

### Step 1: Determine episode ID

- Find the next sequence number: `ls episodes/ | grep -oE '^[0-9]{3}' | sort -n | tail -1` then increment.
- Generate a short Japanese title from the theme (max 15 chars, no slashes).
- Default投稿予定日: 7 days from today (YYYY-MM-DD).
- Episode ID format: `<NNN>-<YYYY-MM-DD>-<title>`
- Example: `001-2026-05-12-設計室の朝`

### Step 2: Create the episode folder structure

```bash
EP_ID="001-2026-05-12-設計室の朝"
WORKSPACE="C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
EP_DIR="$WORKSPACE/episodes/$EP_ID"
mkdir -p "$EP_DIR/patterns/pattern-a"
mkdir -p "$EP_DIR/patterns/pattern-b"
mkdir -p "$EP_DIR/patterns/pattern-c"
mkdir -p "$EP_DIR/patterns/pattern-d"
mkdir -p "$EP_DIR/final"
echo "<original theme text>" > "$EP_DIR/theme.md"
```

### Step 3: Write `README.md` for the episode

Include theme, episode ID, intended posting date, and "status: in progress".

### Step 4: Generate 4 plot patterns in parallel

Use the `4koma-compose` skill 4 times in parallel (one per pattern-id). Pass the theme, pattern-id, episode_dir, and the variation hint for each pattern (a/b/c/d as defined in the skill).

After all 4 finish, verify each `episodes/<id>/patterns/<x>/plot.md` exists.

### Step 5: Generate 4 images in parallel

Use the `4koma-image-gen` skill 4 times in parallel. For each pattern, read the suggested style_preset from `plot.md`, then invoke the skill with `(pattern_dir, style_preset, workspace_root)`.

You can call the bash scripts directly:

```bash
SKILL_DIR="$WORKSPACE/.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts"
for p in pattern-a pattern-b pattern-c pattern-d; do
  PATTERN_DIR="$EP_DIR/patterns/$p"
  STYLE=$(awk '/^## Style preset suggestion$/{getline; print; exit}' "$PATTERN_DIR/plot.md")
  CAST=$(bash "$SKILL_DIR/compose-prompt.sh" "$WORKSPACE" "$PATTERN_DIR" "$STYLE")
  bash "$SKILL_DIR/invoke-codex.sh" "$WORKSPACE" "$PATTERN_DIR" "$STYLE" "$CAST" &
done
wait
```

### Step 6: Report back

Summarize for the user:
- Episode ID
- Path to each `pattern-{a,b,c,d}/generated.png`
- Brief note on each pattern's plot premise
- Any patterns that failed (point at `error.log`)

End with the suggestion: "Review the 4 patterns, then run `/finalize-4koma <ep-id> <pattern-id>` to lock in your choice (or `/refine-4koma <ep-id> <pattern-id> "<指示>"` to iterate)."

## Failure handling

- If 1-2 patterns fail, report errors but continue. The user can still pick from the surviving patterns.
- If 3-4 patterns fail with the same error (especially auth), surface the error prominently and link to `docs/runbooks/codex-relogin.md`.

## Constraints

- Never auto-finalize a pattern. The user always picks.
- Never delete or overwrite existing pattern files. If `/new-4koma` is re-run for the same episode-id, append `-v2` suffix.
- Stay within Phase 1 scope: do NOT post to X, do NOT schedule anything.
````

- [ ] **Step 3: Verify**

```bash
head -10 "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/agents/manga-director/AGENT.md"
# Expected: shows YAML frontmatter with name: manga-director
```

- [ ] **Step 4: Commit** (if git)

```bash
git add .claude/plugins/lineworks-x-ops/agents/
git commit -m "feat(agent): add manga-director orchestrator"
```

---

## Task 10: Commands (3 files)

**Files:**
- Create: `.claude/plugins/lineworks-x-ops/commands/new-4koma.md`
- Create: `.claude/plugins/lineworks-x-ops/commands/refine-4koma.md`
- Create: `.claude/plugins/lineworks-x-ops/commands/finalize-4koma.md`

- [ ] **Step 1: Write `new-4koma.md`**

````markdown
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
````

- [ ] **Step 2: Write `refine-4koma.md`**

````markdown
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

# Determine next version number
NEXT=$(ls "$PATTERN_DIR"/generated*.png 2>/dev/null | wc -l)
NEXT=$((NEXT + 1))

bash "$SKILL_DIR/invoke-codex.sh" "$WORKSPACE" "$PATTERN_DIR" "$STYLE" "$CAST"
mv "$PATTERN_DIR/generated.png" "$PATTERN_DIR/generated_v${NEXT}.png"
```

Report back the path of the new image and prompt the user to review.
````

- [ ] **Step 3: Write `finalize-4koma.md`**

````markdown
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
````

- [ ] **Step 4: Verify all 3 commands exist**

```bash
ls "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用/.claude/plugins/lineworks-x-ops/commands/"
# Expected: new-4koma.md, refine-4koma.md, finalize-4koma.md
```

- [ ] **Step 5: Commit** (if git)

```bash
git add .claude/plugins/lineworks-x-ops/commands/
git commit -m "feat(commands): add /new-4koma /refine-4koma /finalize-4koma"
```

---

## Task 11: End-to-End Smoke Test (1 sample episode)

**Files:**
- Will create: `episodes/001-<date>-<title>/` with full pattern set

This task validates the full pipeline works. **Cost: ~90K tokens.**

- [ ] **Step 1: Restart Claude Code in the project folder**

This ensures the plugin is loaded:

```bash
cd "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用"
# In CLI: type `claude` to start
# In Desktop: open the folder
```

- [ ] **Step 2: Pre-flight Codex auth check**

In Claude Code:

```
Bash: codex exec --skip-git-repo-check --ephemeral "Reply: OK" </dev/null
```

Expected: stdout includes "OK". If 401, run `codex logout && codex login`.

- [ ] **Step 3: Place reference images (manual user action)**

The user must save the 4 reference images into:
- `characters/imaizumi/reference/imaizumi_youtube_still.png`
- `characters/sebastian/reference/sebastian_v1.png`
- `characters/skette/reference/skette_real_machine.png`
- `characters/lineman/reference/lineman_real_machine.png`

If any are not yet available, the pipeline will still run but those characters will be more visually unstable. For the smoke test, **at minimum imaizumi.png and sebastian.png should exist** since these are the most-used pair.

```bash
ls characters/imaizumi/reference/ characters/sebastian/reference/
# Expected: at least one PNG in each
```

- [ ] **Step 4: Run /new-4koma**

```
/new-4koma "今泉課長が朝オフィスでセバスチャンに今日の予定を聞く話"
```

Expected:
- An `episodes/001-<today+7>-<short title>/` folder is created
- 4 patterns generate in parallel (3-5 min total)
- 4 PNG files appear under `episodes/001-.../patterns/{a,b,c,d}/generated.png`

- [ ] **Step 5: Visual verification**

Open all 4 generated PNGs (Read tool in Claude Code).

Check:
- ✅ All 4 are 4-panel manga (4 panels visible)
- ✅ Watercolor style is recognizable (no photorealism, no cel-shaded anime look)
- ✅ Imaizumi appears in navy work jacket
- ✅ Sebastian appears as a butler with silver tray
- ✅ The 4 patterns are visibly different in plot/composition (not 4 copies)

- [ ] **Step 6: Try /refine-4koma**

Pick one pattern and refine it:

```
/refine-4koma 001-... pattern-a "セバスチャンの銀のトレイをもう少し大きく、画面手前に"
```

Expected: a new `generated_v2.png` appears in `pattern-a/`. The tray should be more prominent.

- [ ] **Step 7: Try /finalize-4koma**

```
/finalize-4koma 001-... pattern-c
```

Expected:
- `episodes/001-.../final/final.png` exists
- `episodes/001-.../README.md` records the chosen pattern
- `episodes/001-.../notes.md` exists with the template

- [ ] **Step 8: Document any issues**

If anything failed, log specifics in `episodes/001-.../notes.md` under "Lessons learned" so Tasks 12 can address them. Common issues to watch:
- Style inconsistency between panels of the same generation
- Character drift across the 4 panels
- Codex prompt assembly bug (missing fragments)
- Reference image not being honored

- [ ] **Step 9: Commit** (if git)

```bash
git add episodes/001-*
git commit -m "test: end-to-end smoke test produced first sample episode"
```

---

## Task 12: Sample Episodes 2-5 (production validation)

**Goal:** Produce 3-5 total finalized episodes (counting the smoke test as #1) for the Phase 2 president review. **Cost: ~90K tokens × N patterns × episodes; budget ~400-500K tokens total.**

For each additional episode (002, 003, optionally 004 and 005):

- [ ] **Step 1: Choose a varied theme**

Aim for diversity across the 5 thematic areas listed in spec §3.2:
- 設計室シリーズ (e.g., 002 — 「3D図面を眺めて部品の干渉に気づく今泉課長」)
- 工場・組立シリーズ (e.g., 003 — 「LINEMANが新しい溶接姿勢を試す日」)
- AI/DXシリーズ (e.g., 004 — 「セバスチャンがChatGPT-5.5に新機能の話を聞きたがる」)
- オフィス文化シリーズ (e.g., 005 — 「社内カフェでSKETTEが配膳を手伝おうとして力加減が分からない」)

Pick at least one episode each from **設計室**, **工場**, and **オフィス文化** to demonstrate range.

- [ ] **Step 2: Run the standard flow**

For each chosen theme:
1. `/new-4koma "<theme>"`
2. Review 4 patterns
3. (Optional) `/refine-4koma` 1-2 times until satisfied
4. `/finalize-4koma <ep-id> <pattern>`
5. Fill in `episodes/<ep-id>/notes.md`:
   - Cast used
   - Style preset chosen and why
   - Quality assessment (1-5 stars)
   - Any character or style adjustments needed for next iteration

- [ ] **Step 3: After each episode, review character/style consistency**

Open `final.png` of all completed episodes side by side. Check:
- Imaizumi looks like the same person across episodes
- Sebastian's silver tray is consistently present
- Style preset usage is coherent (same preset → similar feel)

If drift is significant, refine the relevant `characters/<id>/anchor.md` or `style-guide/<preset>/prompt-fragment.md` between episodes.

- [ ] **Step 4: Build the president presentation index**

Create `episodes/PRESENTATION_INDEX.md`:

```markdown
# Phase 2 サンプル4コマ集 (社長承認用)

総数: <N> 本

| # | エピソードID | テーマ | スタイル | 採用パターン |
|---|------------|--------|----------|--------------|
| 1 | 001-... | <theme> | shinkai_default | pattern-c |
| 2 | 002-... | ... | ... | ... |
| ... |

## ハイライト

<one paragraph summarizing what these samples demonstrate about the production capability>

## 次フェーズ提案

社長承認をいただければ Phase 3（X API連携・本番運用）に進みます。
```

- [ ] **Step 5: Commit** (if git)

```bash
git add episodes/
git commit -m "feat(samples): produce 3-5 sample episodes for Phase 2 review"
```

---

## Task 13: Phase 1 Acceptance Check

**Goal:** Validate all 10 acceptance criteria from spec §10.2.

- [ ] **Step 1: Verify the 10 acceptance criteria**

Run through each criterion against the produced artifacts:

1. ✅ **`/new-4koma` produces 4 patterns** — confirmed by Task 11 + 12
2. ✅ **Watercolor style consistency** — visual review of all sample episodes
3. ✅ **Character visual stability across episodes** — side-by-side review of `final.png` from multiple episodes
4. ✅ **4 patterns are meaningfully different** — confirmed each pattern has distinct plot/composition
5. ✅ **`/refine-4koma` works** — confirmed in Task 11 step 6
6. ✅ **`/finalize-4koma` works** — confirmed in Task 11 step 7
7. ✅ **Both Warp(CLI) and Claude Code Desktop work** — try the same `/new-4koma` in both environments at least once
8. ✅ **3-5 finalized episodes exist** — confirmed by Task 12
9. ✅ **`weekly-4koma-flow.md` is followable** — read it; can a fresh person produce an episode?
10. ✅ **Sample presentation deliverable exists** — `episodes/PRESENTATION_INDEX.md`

- [ ] **Step 2: Cross-environment check**

In Warp + Claude Code CLI:
```
/new-4koma "テスト：CLIで実行確認"
```

Verify the same plugin/skills/commands work. Cancel after pattern-a's plot is generated (no need to consume full quota for this check) — `Ctrl+C` is fine.

- [ ] **Step 3: Final commit and tag** (if git)

```bash
git add -A
git commit -m "chore(phase-1): mark Phase 1 acceptance — 10 criteria met"
git tag -a phase-1-complete -m "Phase 1 production pipeline complete; ready for Phase 2 review"
```

- [ ] **Step 4: Notify user**

Report back:

> Phase 1 完了。以下が揃いました：
> - プラグイン `lineworks-x-ops` 一式（`/new-4koma`, `/refine-4koma`, `/finalize-4koma`）
> - キャラ設定 4キャラ × スタイルプリセット 3種
> - サンプルエピソード <N> 本（社長承認用 PRESENTATION_INDEX 含む）
> - Runbook 3種、ADR 1件
>
> Phase 2（社長レビュー＆フィードバック反映）に進めます。

---

## Self-Review Notes

(For the engineer/agent reading this plan: do NOT skip the Self-Review section in the writing-plans skill. After completing all tasks, verify against `docs/superpowers/specs/2026-05-03-x-account-ops-design.md` that nothing in the spec is unaccounted for.)

### Spec coverage check

| Spec section | Implemented in |
|--------------|---------------|
| §1 Project overview | Task 1 (README) |
| §2 Phase plan | Task 1 (README) + this plan as a whole |
| §3 Content strategy | Task 4 (cast) + Task 5 (style) + Task 7 (compose skill) |
| §4 Character & style | Task 4 + Task 5 |
| §5 Architecture | Task 8 (image-gen skill embodies the architecture) + ADR (Task 2) |
| §6 Folder structure | Tasks 1, 4, 5, 6 (folders created throughout) |
| §7 Plugin internals | Tasks 6-10 |
| §8 Workflow | Tasks 7-10 + validation in Tasks 11-12 |
| §8.5 Acceptance criteria | Task 13 |
| §9 Constraints | Embedded in character README, anchor.md, prompt assembly, runbooks |
| §10 Phase 1 deliverables | Verified in Task 13 |
| §11 Open questions | Explicitly deferred to Phase 2+ — not addressed here |

### Out of scope (correctly deferred)

- X API integration — Phase 3
- News post system (`x-news-draft`, `x-analytics`) — Phase 3
- Codex MCP migration — Phase 2+
- Auto-scheduling (`/loop` `/schedule`) — explicitly removed
- `/ship-4koma` command body — Phase 3
