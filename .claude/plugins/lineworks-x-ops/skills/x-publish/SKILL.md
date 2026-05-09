---
name: x-publish
description: Use when the user asks (in any natural-language phrasing) to publish, post, tweet, or share a finalized 4-koma episode to the company's official X account. Resolves the episode reference, validates final.png + post-body.txt are in place, and emits the !publish marker line that triggers the Discord bot's human-approval flow. NEVER calls the X API directly — approval gate is mandatory.
---

# x-publish

「X に投稿して」「ポストして」「ツイートして」「公開して」など、自然文での
**X (旧 Twitter) 投稿依頼を受けたとき** に使うスキル。

このスキル本体は X API を直接叩かない。Discord Bot (`scripts/discord_bot.py`) が
ボタン承認 UI を出すための **トリガーマーカー (`!publish <ep-id>`) を応答に埋める** ことだけ責任を持つ。

## When to invoke

ユーザーの発話が次のいずれかに該当する：

- 「X に投稿して」「ツイートして」「アップして」「公開して」「ポストして」
- `/publish <ep-id>` スラッシュコマンドが直接呼ばれた場合
- 4コマ生成後に「これでいきましょう」「これで投稿」など承認系の発話で締められた場合

ただし **本文の起草** や **構成の議論** だけを求められている場合は invoke しない。

## Inputs

- `user_request` (required) — ユーザーの自然文発話そのまま
- `episode_id_hint` (optional) — ユーザーが番号やテーマで言及している部分

## Pipeline

### Step 1: episode_id を解決する

```bash
ls episodes/ | grep -E '^[0-9]{3}-'
```

ヒューリスティクス：

| ユーザー言及 | 一致方法 |
|---|---|
| 「001」「第1弾」「001番」「ep001」 | `^001-` で前方一致 |
| 「新拠点」「式典」「45周年」など | dir 名に部分一致 |
| 「最新」「直近」「次の」 | `sort -V \| tail -1` |
| 曖昧 / 候補複数 | **候補を列挙してユーザーに聞き返す**。決め打ちしない |

### Step 2: 投稿準備を検証する

```bash
ep=<resolved_episode_id>
ls -la "episodes/$ep/final/final.png" "episodes/$ep/final/post-body.txt"
wc -m "episodes/$ep/final/post-body.txt"
```

- `final.png` 不在 → 「先に finalize が必要です」と返す
- `post-body.txt` 不在 → 本文を起草してユーザーに提示し、承認後に書き込む（投稿はその後）
- `wc -m` が 281 以上 → 短縮案を提示

### Step 3: 応答に !publish マーカーを埋める

応答文末尾に **単独行・コードブロック外** で次のフォーマットを必ず出力：

```
!publish <episode_id>
```

良い例：

```
episodes/001-2026-05-11-新拠点完成PR1 を X に投稿します。
本文 170 字（280 字以内）、画像 final.png 存在確認済みです。
Discord で承認ボタン付きプレビューが出ますので、内容確認の上ボタンを押してください。

!publish 001-2026-05-11-新拠点完成PR1
```

悪い例（マーカーが Bot に検出されない）：

````
✅ 投稿準備完了：
```
!publish 001-2026-05-11-新拠点完成PR1   ← コードブロック内、❌
```
````

```
ご確認後、 `!publish 001-2026-05-11-新拠点完成PR1` を実行してください。   ← 行内、❌
```

## Constraints

### ❌ 絶対禁止

- `scripts/post_to_x.py` の直接実行（CLI も Python import も禁止）
- `tweepy` を import して直接 `client.create_tweet(...)` 呼び出し
- `curl` で X API へ POST
- `.env` から `X_API_*` を読み出して使用すること
- ユーザー承認なしの投稿（マーカー方式以外の投稿経路を作ってはいけない）

### ✅ 許可される行為

- `post_to_x.py` を **読む**（実装確認のため）
- `episodes/*/final/post-body.txt` の起草・編集
- `analytics/<YYYY-MM>/post-log.md` の参照（投稿履歴の振り返り用）
- 投稿予定日や予定本数の確認

## Outputs

- ユーザーへの自然文応答（経緯・本文プレビュー・確認事項）
- 末尾に `!publish <ep-id>` 単独行（**Bot がここをトリガーに使う**）

## Why this design

- Claude が直接投稿すると人間レビューを skip でき、誤投稿リスクが大きい
- マーカー方式なら Discord ボタン承認が常に必須となり、安全側に倒れる
- 自然文・スラッシュコマンド・直接 `!publish` のすべてが同じパイプラインに合流するので
  運用が単純化される

## Related

- `scripts/post_to_x.py` — 実投稿スクリプト（Bot 側からのみ呼ばれる）
- `scripts/discord_bot.py` — `!publish` 検出 + 承認ボタン UI
- `docs/X_API_SETUP.md` — API キー取得・設定手順
- `commands/publish.md` — 明示的なスラッシュコマンド版
