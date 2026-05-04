# CLAUDE.md — lineworks-x-ops プロジェクト指針

このファイルは Claude Code が本プロジェクトで作業する際の **必読指針** です。
特にヘッドレスモード（`claude -p`）で Discord Bot から起動された場合、これがあなたが受け取る最重要コンテキストです。

---

## このプロジェクトの目的

株式会社ラインワークス（千葉、産業用ロボットメーカー）の **公式 X (旧Twitter) アカウント運用** を支援。
週1回の **水彩4コマ漫画** + 不定期ニュース投稿を運用するためのワークスペース＆Claude Code プラグイン群。

---

## システム稼働環境

- **VPS**: Hostinger (Ubuntu 24.04, /opt/lineworks-x-ops/)
- **ユーザー**: `lineworks` (uid=1001)
- **Discord Bot**: Xagent（あなたを呼び出す入口、scripts/discord_bot.py）
- **常時稼働**: tmux session "xops" with claude/codex/discord-bot windows
- **GitHub**: https://github.com/skyblueearthjapan/Official-Company-Account-X.git

---

## キャスト（恒久・たった2キャラ）

| ID | 名前 | 役割 |
|---|---|---|
| `i_kacho` | **I課長** | 株式会社ラインワークス 設計部 課長。氏名はイニシャル「I」のみで表記（プライバシー配慮） |
| `sebastian` | **セバスチャン** | 社内Slack上に常駐するAI執事 (AI Agent 執事 セバスチャン)。物理キャラとして solid に描く（v3 のホログラム表現は撤回済み）。建設現場でもヘルメット非着用 |
| `tamura` | **田村修二 社長** | 株式会社ラインワークス 代表取締役社長。2025年秋の旭日単光章受章。式典・公式行事に登場。実写写真リファレンスあり |

詳細: `characters/<id>/profile.md` `characters/<id>/anchor.md` を必ず読むこと。

---

## 🚨 重要：A/B/C/D パターンとは？（誤解しがち）

`pattern-a` `pattern-b` `pattern-c` `pattern-d` は **創作上のバリエーション** です。

**以下は ❌ 誤解です：**
- ❌ ChatGPT アカウントが複数ある
- ❌ Codex の認証ファイルが pattern 別に分かれている
- ❌ `CODEX_HOME` を切り替える必要がある
- ❌ レート制限回避のための仕組みがある

**以下が ✅ 正解です：**
- ✅ ChatGPT アカウント / Codex 認証は **1つだけ**：`/home/lineworks/.codex/auth.json`
- ✅ `pattern-a/b/c/d` は単に **「同じテーマで4種類の creative な構成バリエーション」を並列生成する仕組み**
- ✅ 並列度はせいぜい4までで、`for ... &` で同時起動するだけ
- ✅ pattern 間の差は **plot.md の内容（構成・スタイル・POV）** だけ

---

## 主要な作業の流れ

### A. ユーザーがテーマだけ渡してきた場合（お任せモード）

ユーザーは以下のいずれかでリクエストしてくる：
- 明示的: `/new-4koma "<テーマ>"`
- **自然文**: 「設計の1日を4コマ漫画にまとめて」「カフェスペースで朝のコーヒーの話を作って」など

**自然文の場合も同じ扱い**：4コマ漫画作成依頼として認識し、フルパイプラインを起動する。

→ 次の手順:
  1. 次のエピソード番号を判定: `ls episodes/ | grep -oE '^[0-9]{3}' | sort -n | tail -1` + 1
  2. エピソード ID 命名: `<NNN>-<YYYY-MM-DD>-<短い日本語タイトル>`（YYYY-MM-DD は投稿予定日 = 通常今日から1週間後）
  3. `episodes/<id>/{theme.md, README.md}` 作成 + `patterns/pattern-{a,b,c,d}/` 作成
  4. 4 patterns の plot.md を並列生成（または各々で異なる方向性を持つように構成）
  5. `compose-prompt.sh` + `invoke-codex.sh` を 4 並列で実行（各 pattern 個別）
  6. 結果 4 枚を Discord に scripts/upload_to_discord.py 経由で投稿
  7. ユーザー選定待ちの状態で完了報告

これ全体の所要時間: 5〜8分（並列生成）

### B. ユーザーが具体的な構成イメージを持っている場合

ユーザーが「こういう構成で」と詳細を伝えてきたら：
1. **plot.md を私（あなた = Claude）が起草**
2. ユーザーに提示して承認を得る
3. 承認後、`scripts/` 内の bash スクリプト経由で生成
4. Discord に上げて確認

### C. ユーザーが「リファレンス確認 + 構成検討」を依頼してきた場合

これは今あなたがやっている作業です。手順：
1. **`reference-images/` 配下の写真を Read で見る**（特にユーザーが指定したフォルダ）
2. 写真の内容を踏まえた構成案（4 panels の起承転結）を Discord 用のテキストでまとめる
3. ユーザーに提示 → 承認後に生成へ進む

**注意**: 構成検討の段階では画像生成しない。plot 案だけ提案。

---

## 重要なファイルパス

- 設計仕様: `docs/superpowers/specs/2026-05-03-x-account-ops-design.md`
- リファレンスカタログ: `reference-images-CATALOG.md`
- VPS 環境メモ: メモリ参照（外部）
- バナーテンプレート: `.claude/plugins/lineworks-x-ops/skills/4koma-image-gen/scripts/compose-prompt.sh`

---

## バナー（全エピソード共通）

すべての生成画像の最上部に以下のバナーを自動挿入（`compose-prompt.sh` で実装済み）：
```
(株)ラインワークス★ 公式アカウント X 4コマコンテンツ No.NNN
```
NNN は episode dir 名から自動抽出（`001`, `002`, ...）

## 全エピソード共通の画像内ルール（恒久・compose-prompt.sh で実装）

### 必須要素

- **スピーカー名ラベル**: すべての吹き出しの直上に **濃紺/インディゴ色の小さな角丸ボックス** を配置し、白文字で発話者名（「I課長」「セバスチャン」「司会者」など）を表示する。シリーズ共通の視覚的記号

### 禁止要素

- **「起」「承」「転」「結」マーカー** をパネルの角に描かない（プロット構造の人間向け注釈であり、画像内には不要）
- **「Panel 1」「Panel 2」などの位置インジケーター** も描かない

---

## 既存エピソード

- `episodes/001-2026-05-11-新拠点完成PR1/` — 第1弾、Pattern-A v5 を採用予定（finalize 保留中）
- `episodes/_archive/` — Phase 1 試作（無視してよい）

---

## デバッグ

- Bot ログ: `/opt/lineworks-x-ops/logs/discord_bot.log`
- Codex 実行ログ: 各 `episodes/<id>/patterns/<x>/run.log` `codex.stdout.log`
- tmux 接続: `tmux attach -t xops`
