---
description: 確定済みエピソードを X (旧 Twitter) に投稿する。承認ボタン経由で必ず人間最終確認を挟む。
argument-hint: "<episode_id> | <番号> | <テーマキーワード>"
---

# /publish

完成した 4 コマエピソード（`final/final.png` + `final/post-body.txt` 配置済）を、
株式会社ラインワークス公式 X アカウント `@lineworks_chiba` に投稿します。

## Usage

```
/publish 001-2026-05-11-新拠点完成PR1     # 完全な episode_id
/publish 001                               # 番号のみ → 前方一致で解決
/publish 新拠点                            # キーワード → 部分一致で解決
/publish 最新                              # 最新エピソードを採用
/publish                                   # 候補を列挙してユーザーに聞き返す
```

## What this does

`x-publish` スキルを invoke：

1. 引数（または会話文脈）から episode_id を解決
2. `episodes/<id>/final/final.png` と `final/post-body.txt` の存在を確認
3. 本文の文字数が 280 以下であることを確認
4. 応答末尾に `!publish <episode_id>` マーカーを単独行で出力

→ Discord Bot がマーカーを検出し、**承認ボタン付きプレビュー** を表示します。

## Pre-conditions

- `final.png` と `post-body.txt` が `episodes/<id>/final/` に配置済
- `.env` に X API キー4種が設定済 (`docs/X_API_SETUP.md` 参照)
- Discord Bot が起動中

## Constraints

このコマンドは **投稿の準備とトリガーまで** を担当します。実投稿は Discord 上の
ユーザー承認ボタン押下後に Bot が `scripts/post_to_x.py` を呼んで実行する設計です。
Claude が API を直接叩くことはありません（`x-publish` スキル参照）。

## Examples

### 例 1: 番号で指定

```
ユーザー: /publish 001
Claude: episodes/001-2026-05-11-新拠点完成PR1 を X に投稿します。
        本文 170 字、画像 final.png 確認済み。Discord で承認ボタンを押してください。

        !publish 001-2026-05-11-新拠点完成PR1
```

### 例 2: キーワード曖昧で聞き返し

```
ユーザー: /publish 式典
Claude: 「式典」を含むエピソード候補が 1 件あります:
        - episodes/002-2026-05-18-創立45周年記念式典PR2
        これを投稿してよろしいですか？

        !publish 002-2026-05-18-創立45周年記念式典PR2
```

### 例 3: 引数なしで最新採用

```
ユーザー: /publish
Claude: 最新の finalized エピソードは 002-2026-05-18-創立45周年記念式典PR2 です。
        本文 213 字、画像 final.png 確認済み。

        !publish 002-2026-05-18-創立45周年記念式典PR2
```

## Related

- `commands/new-4koma.md` — 新規エピソード作成
- `commands/finalize-4koma.md` — エピソードの確定 (`final/` ディレクトリ作成)
- `skills/x-publish/SKILL.md` — このコマンドが invoke するスキル本体
- `docs/X_API_SETUP.md` — API キー取得・設定
