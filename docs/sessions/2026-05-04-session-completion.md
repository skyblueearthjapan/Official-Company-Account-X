# 2026-05-04 セッション完了記録

## セッション総括

**期間**: 2026-05-04（1日）
**担当**: I課長（設計部）+ Claude Code（admin-01@lineworks-local.info）
**結果**: 公式X 4コマ第1弾・第2弾の制作完了 + 公式 X アカウント開設 + 運用基盤確立

---

## 本セッションでやったこと

### 1. リファクタリング（プロジェクト整理）
- SKETTE / LINEMAN キャラクター完全削除（2キャラ運用に変更）
- Phase 1 サンプルエピソード（001/002/003）を `episodes/_archive/` に隔離
- I課長 表記をイニシャル化（プライバシー配慮）

### 2. 運用基盤の確立
- VPS（Hostinger srv1508169）に常時稼働環境構築
  - 専用ユーザー `lineworks` (uid=1001)
  - tmux session `xops`（claude / codex / discord-bot の3 windows）
  - Claude Code 2.1.114（Opus 4.7 1M context）
  - Codex CLI 0.128.0
- GitHub リポジトリ連携: https://github.com/skyblueearthjapan/Official-Company-Account-X
- Discord Bot Xagent 稼働（携帯から指示出し可能）
- Google Workspace MCP 統合（Drive 連携）
- リファレンス写真同期（130+ 枚）

### 3. キャラクター仕様の確立
- I課長（i_kacho）: 設計部課長、紺色作業着、ヘルメット必須（建設現場）
- セバスチャン（sebastian）: 社内Slack上に常駐するAI執事、物理キャラ + 控えめAI記号（チップ柄ラペルピン）
- 田村修二 社長（tamura）: 旭日単光章受章、登場は控えめ方針

### 4. 恒久ルール（compose-prompt.sh / CLAUDE.md に組み込み）
- バナー自動挿入「(株)ラインワークス★ 公式アカウント X 4コマコンテンツ No.NNN」
- 紺色話者ラベル必須
- 起承転結マーカー禁止
- Sebastian トレイにデバイス禁止
- 大人キャスト指定（特に式典系）

### 5. 第1弾コンテンツ完成
**Episode 001: 新拠点完成PR1**（Pattern-A v5、shinkai_default）
- 投稿予定: 2026-05-11
- 構成: 建設現場での緊張感 → 完成披露の王道4コマ
- セバスチャンの「社内Slack上に常駐するAI執事」自己紹介で AI 設定を自然導入

### 6. 第2弾コンテンツ完成
**Episode 002: 創立45周年記念式典PR2**（Pattern-C v11、picturebook）
- 投稿予定: 2026-05-18
- 構成: 受付準備 → 司会開会 → 鏡開き → ホテルロビーでお見送り
- 11バージョン経過。重要な学び：
  - AIが「童顔」化する問題に対処（大人キャスト明示指定）
  - Sebastian トレイにデバイス禁止ルール化
  - 来賓に正対してお辞儀する構図の指定方法
  - V1テイスト（汗・幟修正の緊張感）の表現方法

### 7. 公式 X アカウント開設
- URL: https://x.com/lineworks_chiba
- ハンドル: @lineworks_chiba（千葉本社の地場感を選択）
- プロフィール: 表示名・Bio・場所・URL・アイコン・ヘッダー設定完了
- 2要素認証 + プロフィール完成

---

## 残作業（社長・総務承認待ち）

詳細は `docs/REMAINING_WORK.md` 参照。要点：

1. **第1弾・第2弾の内容承認**
2. **ゴールド認証取得**（年額 $2,000）
3. **X API 開発者申請**（自動投稿環境構築）
4. **AI 生成コンテンツ表記の文言確定**

---

## 次回セッション開始時の手順

1. このファイル + `docs/REMAINING_WORK.md` 読了
2. 会議で決まった内容を確認
3. 承認された項目から順次実装着手
4. メモリ（`reference_lineworks_x_ops_*` 系）参照

---

## 重要なパス・URL（即時参照）

### Local（このノートPC）
- プロジェクトルート: `C:\Users\imaizumi.LINEWORKS-NET\Documents\会社公式アカウントＸ運用\`
- 確定 第1弾: `episodes/001-2026-05-11-新拠点完成PR1/final/final.png`
- 確定 第2弾: `episodes/002-2026-05-18-創立45周年記念式典PR2/final/final.png`

### VPS
- プロジェクトルート: `/opt/lineworks-x-ops/`
- SSH接続: `ssh lineworks-vps-user`
- tmux接続: `tmux attach -t xops` または `xops-tmux` alias

### GitHub
- https://github.com/skyblueearthjapan/Official-Company-Account-X

### 公式 X
- https://x.com/lineworks_chiba（@lineworks_chiba）

---

## 統計

- **本日の総コミット数**: 約30件
- **生成した4コマ画像**: 約20点（v1〜v11 含む試作）
- **使用 Codex トークン**: 推定 50万〜80万トークン（多数の reroll により）
- **VPS 稼働時間**: 8時間以上（連続稼働）
- **Discord Bot 応答数**: 約10回

---

**お疲れさまでした。会議後の進行をお待ちしています。**
