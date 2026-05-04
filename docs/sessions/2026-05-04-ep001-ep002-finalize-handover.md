# 2026-05-04 セッション引き継ぎ — 第1弾・第2弾 完成 + 運用基盤確立

## 本日の達成事項

### コンテンツ
- ✅ **公式X 4コマ第1弾 (No.001)** 確定 — 「新工場建設・新事務所完成 PR」、Pattern-A v5
- ✅ **公式X 4コマ第2弾 (No.002)** 確定 — 「創立45周年記念式典 + 旭日単光章受章祝賀会 PR」、Pattern-C v11

### 運用基盤
- ✅ **VPS（Hostinger srv1508169）** に常時稼働環境構築
  - 専用ユーザー `lineworks` (uid=1001)
  - プロジェクト `/opt/lineworks-x-ops/`
  - tmux session `xops` 3 windows（claude / codex / discord-bot）
- ✅ **Discord Bot Xagent** 稼働、携帯から指示出し可能
- ✅ **Google Workspace MCP** 統合（claudeagent01 から service-account.json 流用）
- ✅ **GitHub** 連携（https://github.com/skyblueearthjapan/Official-Company-Account-X）
- ✅ **リファレンス写真同期**：会社公式X_サンプルデータ + 260403式典 = 130+ 枚

### 恒久ルール（compose-prompt.sh / CLAUDE.md / character anchors に組み込み済）
1. **バナー自動挿入**: `(株)ラインワークス★ 公式アカウント X 4コマコンテンツ No.NNN`（NNN は episode dir 名から自動抽出）
2. **紺色話者ラベル必須**: 各吹き出し上に紺色角丸ラベルで発話者名表示
3. **起承転結マーカー禁止**: パネルの角に「起」「承」「転」「結」を描かない
4. **Sebastian トレイにデバイス禁止**: タブレット・スマホは絶対トレイに乗せない、シーンに合った接客アイテム（ワイングラス / お猪口 / ウェルカムカード等）のみ
5. **キャスト確定**: i_kacho, sebastian, tamura（田村社長は控えめ方針）

---

## キャラクター仕様（確定）

### I課長 (i_kacho)
- 株式会社ラインワークス 設計部 課長
- 氏名は意図的に「I課長」とイニシャル表記（プライバシー配慮）
- 紺色作業着、黒髪横分け、メガネなし
- 建設現場では**必ずヘルメット着用**
- 屋内シーンでは脇に抱える

### セバスチャン (sebastian)
- **社内Slack上に常駐するAI執事**（自己紹介の決まり文句）
- 物理的に solid に描く（ホログラム表現は撤回済）
- 黒フロックコート + 銀のトレイ、胸元にチップ柄ラペルピン（AI記号）
- 安全配慮ルールから免除（ヘルメット非着用、Slack在住で説明）
- トレイにはシーンに合った接客アイテム（デバイス禁止）

### 田村修二 社長 (tamura)
- 代表取締役、2025年秋 旭日単光章受章
- 公式ホームページ写真をリファレンス使用
- **明示的に登場させるのは控えめ方針**（ご本人が嫌がる可能性配慮）
- 公式式典系での登場時のみ使用、似顔絵的忠実度は「識別性ありのデフォルメ」

---

## バージョン履歴の要点（Episode 002 Pattern-C）

11バージョン経過。主な学び：

| 版 | 学び |
|---|---|
| v1 | 初版、童顔・幟修正のV1テイスト |
| v2-v3 | 田村社長 登場 → 撤回（社長配慮） |
| v4 | 画像合成（Pillow）でハイブリッド制作可能と判明 |
| v5 | 「起承転結」マーカーが意図せず描画される問題発覚 |
| v6 | 写真忠実度と大人キャスト指定が必要と判明 |
| v7 | Sebastian トレイにタブレット問題、4コマ目台詞の宛先問題 |
| v8 | **恒久ルール（紺色話者ラベル + 起承転結禁止）導入** |
| v9 | Panel 1 自立幟、Panel 4 来賓正対 |
| v10 | Panel 1 で I課長 と幟の手の重なり問題 |
| **v11** | **V1テイスト復活（汗・幟修正の緊張感）→ 確定** |

---

## VPS 運用情報

### SSH接続
```
ssh lineworks-vps         # root として
ssh lineworks-vps-user    # lineworks ユーザーとして（推奨）
```

### tmux セッション
```
ssh lineworks-vps-user
xops-tmux                 # alias: tmux attach -t xops
```
ウィンドウ構成：
- **0 (claude)**: 対話的 Claude Code（Bypass Permissions モード）
- **1 (codex)**: Codex CLI（ChatGPT 認証済）
- **2 (discord-bot)**: Discord Bot 常駐 Python プロセス

### Discord Bot 操作
- 状態確認: `tail -f /opt/lineworks-x-ops/logs/discord_bot.log`
- 停止: tmux 内 window 2 で `Ctrl+C`
- 再起動: `cd /opt/lineworks-x-ops && .venv/bin/python scripts/discord_bot.py`

### 画像生成方式
- **Discord 経由**: `#一般` チャンネルにメッセージ送信 → bot が claude -p で実行
- **VPS 直接**: SSH 後、エピソード単位の `run-all.sh` 実行 or 個別 codex 起動

---

## 次回セッション開始時の手順

1. このファイル読了
2. `episodes/PRESENTATION_INDEX.md` で確定済み素材を確認
3. `CLAUDE.md` の恒久ルール再確認
4. メモリ（`reference_lineworks_x_ops_*` 系）参照
5. Discord Bot 健康確認（必要に応じ tmux で再起動）

---

## 既知の課題 / 改善余地

1. **gpt-image-2 の人数指定の限界**: plot で「4人」指定しても 2-3人で生成されるケースあり
2. **Deploy Key (VPS→GitHub push)**: HTTPS read のみ動作、push は未解決（影響軽微）
3. **建物の実写完全再現**: 雰囲気は寄せられるが形状の完全一致は AI モデルの限界

---

## 連絡先
- プロジェクトオーナー: I課長 (株式会社ラインワークス 設計部)
- Claude Code セッション: admin-01@lineworks-local.info（Opus 4.7 1M context）
