# Phase 1 完了 引き継ぎ資料 — 2026-05-03

> **2026-05-04 改訂注記**: SKETTE / LINEMAN キャラクターは廃止し、今泉課長 + セバスチャンの2キャラ運用に変更しました。本ドキュメント以下の SKETTE/LINEMAN 関連記述は **歴史的記録** として残しています。

| 項目 | 内容 |
|------|------|
| セッション日 | 2026-05-03（土） |
| セッション時間 | 約2時間半（22:00 - 23:30） |
| 担当 | 今泉課長 ＋ Claude (ディレクター) |
| 結果 | **Phase 1 全納品物完了**、Phase 2 社長レビュー素材4本完成 |
| 次回 | 社長レビュー → Phase 2 改善 → Phase 3（X API連携） |

> 次回セッション冒頭で**まずこのファイルを読む**ことで、前回の全体像を即座に把握できます。
> 詳細な仕様は `docs/superpowers/specs/2026-05-03-x-account-ops-design.md` を参照。

---

## 1. 本日の達成事項

### 1.1 Phase 1 全納品物（仕様§10.1）完了

| 区分 | 件数 | パス |
|------|------|------|
| ADR | 1 | `docs/decisions/0001-subprocess-over-mcp.md` |
| Runbook | 3 | `docs/runbooks/{codex-install, codex-relogin, weekly-4koma-flow}.md` |
| キャラクター v1 | 4キャラ | `characters/{imaizumi, sebastian, skette, lineman}/` |
| スタイル | 3preset | `style-guide/{shinkai_default, picturebook, ghibli_bg}/` |
| プラグイン | 一式 | `.claude/plugins/lineworks-x-ops/` |
| サンプル | 4本 | `episodes/{001-, 002-, 003-}/` |
| 提示用 | 1 | `episodes/PRESENTATION_INDEX.md` |
| 業務フロー資料 (Bonus) | 1 | `docs/business-flows/design-daily-workflow.md` |

### 1.2 Phase 2 社長レビュー素材ラインナップ（4本）

| # | エピソード | 採用パターン | スタイル | 評価 | final.png パス |
|---|-----------|------------|---------|------|---------------|
| 1 | 001 設計室の朝 | pattern-b（セバ視点） | shinkai_default | ★★★★★ | `episodes/001-2026-05-10-設計室の朝/final/final.png` |
| 2 | 002 廃盤部品の襲来 | pattern-d（緊迫系） | ghibli_bg | ★★★★ | `episodes/002-2026-05-17-廃盤部品の襲来/final/final.png` |
| 3 | 003 3DCAD vs 2D職人 | pattern-a v2 | shinkai_default | ★★★★ | `episodes/003-2026-05-24-3DCAD vs 2D職人/final/final.png` |
| 4 | 003 同サブ案 | pattern-c v2 | picturebook | ★★★★ | `episodes/003-2026-05-24-3DCAD vs 2D職人/patterns/pattern-c/generated.png` |

### 1.3 ディレクター方式での進行

ユーザー指示：「ディレクターとして動き、品質管理と進捗管理に専念」「3名チーム（実装1+レビュー2）でクロスレビュー」
- 6案件並行実装 → クロスレビュー10名 → 修正5名 → 統合受入1名 → スモークテスト → 改善多数
- 私（Claude）は終始ディレクターとして、ファイル直接編集を最小限に抑制（memory更新と引き継ぎ資料のみ自身で対応）

---

## 2. 本セッション中に発見・解決した課題

### 解決済み

| # | 課題 | 解決内容 |
|---|------|---------|
| 1 | `invoke-codex.sh` の codex 引数が位置渡しで動かない | `cat prompt.md \| codex exec ... -` に修正 |
| 2 | `compose-prompt.sh` の `[BASE]` が「吹き出しなし」固定で実用に合わず | 「吹き出し付き必須＋台詞verbatim」に修正 |
| 3 | `compose-prompt.sh` の awk が plot.md のフォーマット揺らぎ（`**Scene:**` vs `- Scene:`、`Panel` vs `コマ`）に追従できない | Panel/コマ両対応＋全非空行抽出に緩和 |
| 4 | キャラ整合制約が一部README欠落（lineman の顧客機密制約等） | 全キャラREADMEに横断的に追加 |
| 5 | `refine-4koma` のversion suffixカウントが衝突する | `generated_v*.png` のみ対象、最大番号+1に修正 |
| 6 | `invoke-codex.sh` の `ls\|head` が日本語パスで破損／`stat` がWindows非互換 | nullglob+配列展開／`wc -c` に置換 |

### 残課題（Phase 2 で対応）

| # | 課題 | 影響度 | 対応方針 |
|---|------|--------|---------|
| A | SKETTE/LINEMAN の実機形態忠実度が低い（標準的ロボット形状にしかならない） | 中 | reference 画像を **単一実機写真** に絞り込み、anchor.md の形状記述を強化 |
| B | sebastian の女性化キャラ崩壊（テクノロジー操作役で発生、003-b/d で実発生） | 中 | plot.md 設計時、sebastian は「執事として横で見守る」役柄に固定し、テクノロジー操作描写は imaizumi に寄せる |
| C | plot.md フォーマットが executor 毎にブレる | 低 | `4koma-compose/SKILL.md` テンプレ厳格化＋compose-prompt.sh awk 更に頑健化 |
| D | `invoke-codex.sh` の SID 抽出が稀に Windows パスを誤認 | 低 | `\bsession id: \K[a-f0-9-]{30,}` のような厳密化 |
| E | 並行codex 4本以上で稀に認証競合 | 低 | `&` 並列の間に `sleep 2` 挟むか並列度を最大4に制限 |
| F | 標準スケット／スケットビッグの別キャラ分離（ユーザー方針） | 中 | `characters/skette/` を `skette_standard/` `skette_big/` に分離、各 anchor.md/profile.md 整備 |
| G | imaizumi reference画像が YouTube プレビュー画面のまま（UI要素含む） | 低 | 人物部分のみクロップした画像に差し替え |
| H | imaizumi/skette の参照画像差し替え予定（ユーザー方針） | 低 | ユーザーが後日素材ピックアップ |
| I | runbook の codex-relogin.md / weekly-4koma-flow.md にも PowerShell 等価コマンド併記 | 低 | codex-install.md と同パターンで対応 |

---

## 3. 重要な判断ログ

### 003 で 002 と異なりキャラ崩壊が発生した理由（仮説）

- 002 plot.md の sebastian は「内線メモを持って報告」「夜通し付き合う」など**執事役柄に忠実な行動**
- 003 plot.md の sebastian は「3D CADを操作してプレゼン」「タブレット表示」など**テクノロジー操作役**を担う描写
- gpt-image-2 が行動コンテキストから役柄を再解釈し、「未来的女性アシスタント」イメージを誘発した可能性

**結論**: reference 画像の効力よりも plot.md 内の行動描写が画像生成に強く影響することが判明。Phase 2 で plot.md 設計ガイドラインを強化する。

### 003 で a/c は崩壊せず b/d だけ崩壊した理由

- a/c は executor がリカバリ作業中に compose-prompt.sh を迂回、または別経路で生成
- b/d は同じ崩壊リスクある plot.md でも結果が違う → 確率的揺らぎの寄与もある
- refine 後の v2 では a/c とも崩壊なし → 改善されたプロンプトで安定

### Pattern B 採用理由（001）

ディレクター推奨：「① の俯瞰背中越し構図 +『本日も7時52分。課長は8時ちょうどに……』モノローグが映画の冒頭ナレーション風で、ブランド観を最も体現」→ 社長レビュー素材として最強と判断

---

## 4. コスト試算（Codex経由・本セッション実消費推定）

| 工程 | 推定トークン |
|------|-------------|
| 001 スモークテスト初回 | 約86K |
| 001 台詞付き化 A/B/D refine | 約66K |
| 002 生成（リカバリ含む） | 約100-130K |
| 003 生成（リカバリ含む） | 約100-130K |
| 緊急修正 refine 3本 | 約66K |
| **合計** | **約400-500K** |

ChatGPT Team プランの月間目安600K（仕様§8.8）以内に収束。

---

## 5. 次回セッション開始手順

### 5.1 Phase 2 開始時（社長承認後）

1. 本ファイル `docs/sessions/2026-05-03-phase1-completion-handover.md` を最初に読む
2. memory `project_lineworks_x_ops_phase1.md` で Phase 2 優先事項を確認
3. `episodes/PRESENTATION_INDEX.md` で社長フィードバックを当てはめる場所を確認
4. 残課題リスト（本ファイル §2 後半）から優先度の高い項目に着手

### 5.2 新エピソードを単に追加したい場合

1. `/new-4koma "<お題>"` を Claude Code で実行
2. 4パターン生成（約86Kトークン、5-8分）
3. 視覚確認 → `/finalize-4koma <ep-id> <pattern>` で確定
4. `episodes/PRESENTATION_INDEX.md` に1行追加

### 5.3 本日の方式を踏襲する場合（並行ディレクター方式）

- 6案件以下の独立タスクなら executor 並行起動が効率的
- ただし codex 並列は **4本まで**に抑える（仕様§5.6 認証競合リスク）
- レビュー2名のクロスレビューは critic + code-reviewer の組み合わせが有効
- 修正担当には「BLOCKER のみ対応、MINOR は Phase 次フェーズで」と指示すると無駄が出にくい

---

## 6. 関連ドキュメント

- 設計仕様書: `docs/superpowers/specs/2026-05-03-x-account-ops-design.md`（597行、全章）
- 実装計画書: `docs/superpowers/plans/2026-05-03-phase1-implementation.md`（2020行、Task 1-13）
- 業務フロー資料: `docs/business-flows/design-daily-workflow.md`（255行、4コマ題材プール）
- ADR: `docs/decisions/0001-subprocess-over-mcp.md`
- 関連 memory:
  - `project_lineworks_x_ops_phase1.md` — Phase 1 完了状態 + Phase 2 優先事項
  - `feedback_lineworks_x_ops_pitfalls.md` — 実機運用での落とし穴
  - `reference_lineworks_x_ops_paths.md` — 重要パスリファレンス
  - `project_skette_naming_origin.md` — SKETTE 命名由来 + 標準/ビッグ分離方針

---

## 7. 締めの所感（ディレクター視点）

- Phase 1 は計画通り「ファイル成果物 → スモークテスト → サンプル蓄積」の流れで完走
- 計画書の不備（プロンプト「吹き出しなし」固定、awk 厳格すぎ）が実機で初めて判明し、本セッションで根本対応済み
- ユーザー（今泉課長）の「ディレクターとして動く」指示により、私は終始エージェント采配と判断ログ整備に集中、ファイル編集は最小限に抑制できた
- Phase 2 の最優先は **SKETTE/LINEMAN の視覚忠実度** と **plot.md 設計ガイドライン強化**（特に sebastian キャラ崩壊予防）
- Phase 3（X API）は社長承認＋開発者ポータル法人申請の進捗待ち、Phase 1/2 とは独立して進められる

**社長承認をいただければ Phase 2 → Phase 3 と進めます。お疲れさまでした。**
