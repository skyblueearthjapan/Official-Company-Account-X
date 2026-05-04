# 株式会社ラインワークス 公式X運用 設計仕様書

> **2026-05-04 改訂注記**: SKETTE / LINEMAN キャラクターは廃止し、**今泉課長 + セバスチャンの2キャラ運用** に変更しました。本ドキュメント以下の §3.2 ロボット主役シリーズ、§3.3 工場系軸、§4.1 §4.2 の SKETTE/LINEMAN 行、§6 フォルダ構造の `skette/` `lineman/` 等の記述は **歴史的記録** として残しています。現行のキャラクター構成は `README.md` および `.claude/plugins/lineworks-x-ops/skills/4koma-compose/SKILL.md` を参照してください。

| 項目 | 内容 |
|------|------|
| プロジェクト名（仮） | `lineworks-x-ops` |
| 作成日 | 2026-05-03 |
| 起案者 | 今泉課長（株式会社ラインワークス 設計部） |
| 文書ステータス | Phase 0 設計仕様 — レビュー待ち |
| 対象範囲 | Phase 0〜3 全体の設計（実装対象は Phase 1 のみ） |

---

## 第1章 プロジェクト概要

### 1.1 目的

株式会社ラインワークス（千葉市の産業用ロボットメーカー）の **公式X（旧Twitter）アカウント運用** を支援する Claude Code ベースのワークスペース／プラグイン群を構築する。

### 1.2 コアバリュー

- ホームページに載せられない「**一品一用品の現場感**」を、水彩画チックな4コマ漫画で**ぼかして見せる**
- 製品PR文脈と採用文脈を **「中の人の日常」発信** で橋渡しする
- 顧客機密に配慮しつつ、若手エンジニア層にリーチできる発信プラットフォームを構築

### 1.3 成功基準

Phase 4 終了後に、社長の承認を経て公式X運用を継続的に回せる体制が整っており、週1の4コマ漫画＋不定期ニュース、両系統の発信が「人手最小・品質安定」で運用できる状態。

---

## 第2章 フェーズ計画とスコープ

| Phase | 名称 | ゴール | 含むもの | 含まないもの |
|-------|------|--------|----------|--------------|
| **0** | 設計仕様確定 | 本ドキュメントの完成 | spec doc、要件合意 | 実装 |
| **1** | 4コマ生産ライン実装 | Claude Code から `$imagegen` まで一貫して動く | スキル、エージェント、コマンド、character sheets v1、style presets | X API、ニュース投稿、分析 |
| **2** | 試作＆社内承認 | サンプル4コマ 3〜5本を社長に提示 | 複数パターンの試作、レビューループ、character sheet 改良 | 公開投稿 |
| **3** | X API連携＋本番運用開始 | 公式アカウント開設、定期投稿、分析 | X開発者申請、ニュース投稿系、分析エージェント | （Phase 3 以降の運用改善） |

本仕様書がカバーするのは Phase 0〜3 全体の設計だが、**実装の即時着手対象は Phase 1 のみ**。Phase 2・3 は「設計は書くが実装は後」という扱い。

---

## 第3章 コンテンツ戦略

### 3.1 二系統の発信

| 系統 | 頻度 | 内容 | 表現 | Phase 1の主対象 |
|------|------|------|------|----------------|
| **① 4コマ漫画**（メイン） | 週1回 | 設計者の1日／組み立て員の出張／新工場／AI活用／社員食堂・社内カフェ等、社内の日常 | 水彩画チック4コマ | ✅ |
| **② ニュース告知**（サブ） | 不定期 | 求人募集／受賞／特許取得／節目の広報 | 写真＋テキストもあり得る | ❌（Phase 3） |

### 3.2 4コマ漫画のテーマ領域（初期想定プール）

- **設計室シリーズ**：機械設計の試行錯誤、CAD作業、3D図面、客先への提案資料作り
- **工場・組立シリーズ**：現場での組み立て、調整、出張、客先据付
- **AI/DXシリーズ**：社内でのAI活用例、セバスチャン登場回、新ツール導入
- **オフィス文化シリーズ**：社員食堂、社内カフェ、新工場、節目イベント
- **ロボット主役シリーズ**：SKETTE / LINEMAN が前面に出る回（製品PR要素強め）

### 3.3 キャスト構成原則

- 毎回 **2〜3キャラ** を組み合わせて出演（4人全員が出る回はレア演出）
- 軸は **今泉課長＋セバスチャン**（オフィス系）と **SKETTE＋LINEMAN±誰か**（工場系）

---

## 第4章 キャラクター設定 & スタイルプリセット

### 4.1 キャスト

擬人化方針：**「ロボット形態維持＋表情のみ追加」（『ウォーリー』方式）** を全キャラ共通の基本方針とする。SKETTE/LINEMAN は実機形態を残してデフォルメ。今泉課長・セバスチャンは人間／執事の標準的人型だが画風は同じ水彩タッチで統一。

| ID | 名前 | 所属／役回り | 性格・口調 | ビジュアル方針 |
|----|------|--------------|----------|----------------|
| `imaizumi` | **今泉課長** | 設計部・課長／主人公 | 真面目だがツッコミ気質、ロボット好きの童心あり | LINEWORKS紺色作業着（襟付きジャケット）、内側に襟付シャツ＋ネクタイ、メガネなし、黒髪を横分けの清潔感ある髪型、中肉中背の30〜40代男性。手にロボット部品やCAD図面を持って説明するシーンが似合う。実在ご本人がモデルだが、似顔絵的忠実度は「識別性ありのデフォルメ」に留める |
| `sebastian` | **AI執事セバスチャン** | 社内Slack常駐AIエージェント | ハイテクだが古風な執事口調（「左様でございます」等）、博学、淡々 | 黒髪のセミロング（軽くウェーブ）、薄い口髭・無精髭、鋭い眼差し（青〜灰色系の瞳）、黒のフロックコート風タキシード＋白の大きめのクラヴァット、白手袋。AI／ホログラム表現は使わず、正統派の格式高い執事として描く。シグネチャー・プロップは装飾彫刻入りの**銀のトレイ** |
| `skette` | **SKETTE** | ポジショナー擬人化／工場現場担当 | 寡黙な力持ち、職人気質、踏ん張り屋 | 実機（昇降式片持ち3軸ポジショナー）の形を残し、表情（目・口）を追加 |
| `lineman` | **LINEMAN** | 6軸ロボット擬人化／溶接職人キャラ | 器用万能、フットワーク軽い、明るい | 実機（6軸複合型ロボット）の形を残し、アーム先端付近に表情を配置 |

### 4.2 リファレンス画像

| キャラ | 正準リファレンス | 保存場所 |
|--------|------------------|----------|
| `sebastian` | ユーザー提示の AI 生成画像（黒髪・銀トレイ持ちの執事） | `characters/sebastian/reference/sebastian_v1.png` |
| `imaizumi` | LINEWORKS 公式 YouTube「経営理念」動画（0:34付近）の左側に映る今泉課長の静止画 | `characters/imaizumi/reference/imaizumi_youtube_still.png` |
| `skette` | 実機写真（社内素材から選定） | `characters/skette/reference/skette_real_machine.png` |
| `lineman` | 実機写真（社内素材から選定） | `characters/lineman/reference/lineman_real_machine.png` |

リファレンス画像は **`codex exec -i, --image` フラグで毎回画像生成プロンプトに添付** することで、キャラクター一貫性を担保する。

### 4.3 スタイルプリセット

| プリセットID | 用途・トリガー | スタイル要素 | 参照作品 |
|--------------|--------------|-------------|----------|
| `shinkai_default` | デフォルト、現代的シーン、若手向け | 淡い水彩＋デジタルの透明感、空・光の表現、繊細なディテール | 新海誠映画の背景美術系 |
| `picturebook` | ほっこり系（社内カフェ、社員食堂、社内行事） | やわらかい水彩、ぬくもり、丸みのある描線 | ピーターラビット、ぐりとぐら系 |
| `ghibli_bg` | 工場・重厚な機械・現場感 | 質感の高い水彩背景、重厚さ、職人の手仕事の空気 | 男鹿和雄のジブリ背景画 |

### 4.4 Character Sheet & Style Preset の格納フォーマット

```
characters/<id>/
├── profile.md          ← 役回り、性格、口調、関係性（日本語）
├── anchor.md           ← 画像生成プロンプトに差し込む英語テキスト断片
├── reference/          ← 参照画像
│   └── *.png
└── README.md           ← キャラの取扱注意・制約

style-guide/<preset_id>/
├── style.md            ← スタイルの説明、参照作品、色調（日本語）
├── prompt-fragment.md  ← プロンプトに差し込む英語テキスト断片
└── samples/            ← 過去生成の代表画像
    └── *.png
```

### 4.5 画像生成プロンプトの組み立てルール

`$imagegen` に渡されるプロンプトは以下の構造を持つ：

```
[基本指示] 4-panel manga, watercolor style, no speech bubbles initially.
[スタイル断片] {style-guide/<preset>/prompt-fragment.md の内容}
[キャラ断片] {出演キャラそれぞれの characters/<id>/anchor.md の内容}
[シーン記述] {本回固有のネタ・構図記述（Claude Code が生成）}
[制約] No real customer products. No real company logos other than LINEWORKS approved.
```

これをテンプレート化したのが Phase 1 のスキル `4koma-image-gen` の中心責務。

---

## 第5章 技術アーキテクチャ

### 5.1 全体システム俯瞰

```
┌────────────────────────────────────────────────────────────────┐
│                   会社公式アカウントＸ運用 (workspace)            │
│                                                                 │
│  ┌────────────────────────────────────────────┐               │
│  │ Claude Code (司令塔・対話・編集・オーケストレーション)         │
│  │  ├─ skill: 4koma-compose                   │               │
│  │  ├─ skill: 4koma-image-gen                 │               │
│  │  ├─ skill: x-news-draft   (Phase 3)        │               │
│  │  ├─ skill: x-analytics    (Phase 3)        │               │
│  │  ├─ agent: manga-director                  │               │
│  │  └─ command: /new-4koma 等                 │               │
│  └────────┬───────────────────────────────────┘               │
│           │ Bash subprocess (Phase 1 main)                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────────┐               │
│  │ codex exec --skip-git-repo-check ...       │               │
│  │   ├─ -i (reference images: characters/*)   │               │
│  │   └─ prompt: "...$imagegen"                │               │
│  └────────┬───────────────────────────────────┘               │
│           │ ChatGPT Team subscription quota                    │
│           ▼                                                     │
│  ┌────────────────────────────────────────────┐               │
│  │ OpenAI gpt-image-2 (Codex 内蔵)            │               │
│  └────────┬───────────────────────────────────┘               │
│           │ → ~/.codex/generated_images/<sid>/ig_*.png         │
│           ▼                                                     │
│  ┌────────────────────────────────────────────┐               │
│  │ Claude Code (Read PNG → 検収 → episodes/に移送) │             │
│  └────────────────────────────────────────────┘               │
└────────────────────────────────────────────────────────────────┘

  Phase 3 で追加:
  Claude Code → X API (投稿/分析) ← X 開発者申請＋OAuth
```

### 5.2 画像生成バックエンド：3層フォールバック設計

| 優先 | バックエンド | 起動方法 | 認証 | 用途 |
|------|------------|---------|------|------|
| **1次** | **Codex subprocess** | `codex exec ... $imagegen` | ChatGPT Teamサブスク | **Phase 1 デフォルト** |
| 2次 | Codex MCP | `claude mcp add codex` で登録、`codex` ツール経由 | 同上 | 将来オプション、Phase 2 検証対象 |
| 3次 | OpenAI Image API直叩き | 自前ラッパスクリプト | `OPENAI_API_KEY` | 緊急時／大量生成時のみ |

設計上、画像生成バックエンドを **`4koma-image-gen` スキル内で抽象化** し、設定で切替可能にする。

### 5.3 リファレンス画像注入戦略

- **キャラ一貫性**：出演する各キャラの `characters/<id>/reference/*.png` を `-i` で添付
- **スタイル一貫性**：採用プリセットの `style-guide/<preset>/samples/` から代表サンプルを `-i` で添付
- **シリーズ連続性**：直前回の最終コマを `-i` で添付し、回を跨いだ世界観連続性を保つ（Phase 1 後半で導入検討）

### 5.4 Codex セッション戦略

- **Phase 1 デフォルト**：`--ephemeral` で各 codex 呼出は独立。再現性・冪等性確保
- **将来オプション**：`resume` で過去セッションを継続。長期キャラ性格の蓄積（Phase 2 以降検討）

### 5.5 X API 連携（Phase 3、設計のみ）

- **認証**：X 開発者ポータルで法人アカウント申請 → OAuth 2.0 Bearer Token 取得
- **最小権限**：投稿（Write）＋分析（Read：自社tweetメトリクス、業界他社観察）
- **エンドポイント**：v2 API 前提（Tweet作成、Media upload、User lookup、Tweet metrics）
- **実装方針**：薄い HTTP クライアント（Python or Node）を Claude Code から呼ぶ
- **責任分離**：投稿前に必ず Claude Code 上でプレビュー＆ユーザー承認を経るフロー（自動投稿しない）

### 5.6 認証情報の管理

| 種類 | 保存場所 | 取扱方針 |
|------|---------|---------|
| Codex (ChatGPT) | `~/.codex/auth.json` | Codex CLI 標準。この PC の物理アクセス管理に依存。バックアップ対象から除外 |
| OpenAI APIキー（フォールバック用） | 環境変数 `OPENAI_API_KEY` | リポジトリにコミットしない、設定書類にも書かない |
| X API トークン（Phase 3） | OS 標準のキーリングまたは `.env`（`.gitignore`） | リポジトリ非コミット必須 |

### 5.7 依存ソフトウェア

| ソフト | 必須バージョン | 確認状況 |
|--------|--------------|----------|
| Node.js | v24+ | ✅ v24.12.0 |
| npm | v11+ | ✅ v11.6.2 |
| Codex CLI | v0.128+ | ✅ v0.128.0、ChatGPT Team 認証済 |
| Claude Code | 最新 | ✅ 本セッション環境 |
| Git | 任意 | バージョン管理する場合のみ |

### 5.8 Phase 0 で実施した検証結果（参考）

| 項目 | 結果 |
|------|------|
| Codex CLI インストール | ✅ v0.128.0 |
| ChatGPT Team サブスク認証 | ✅（〜2026-08-12 有効） |
| API課金リスク | ✅ なし（環境変数 `OPENAI_API_KEY` 未設定、auth.json も null） |
| `codex exec` テキスト疎通 | ✅（PING_OK、1,669 tokens） |
| `codex mcp-server` 起動 | ✅ `codex` / `codex-reply` の2ツール公開 |
| `$imagegen` 動作 | ✅ 水彩タッチで生成成功（22,671 tokens／枚） |
| 画像出力先 | ✅ `~/.codex/generated_images/<session_id>/ig_*.png` |

---

## 第6章 フォルダ構造（プロジェクトルート）

```
会社公式アカウントＸ運用/                      ← プロジェクトルート
├── .claude/
│   ├── plugins/
│   │   └── lineworks-x-ops/                  ← プラグイン本体（第7章）
│   └── settings.local.json                   ← 既存
├── .omc/                                     ← 既存（OMC状態）
│
├── characters/                               ← キャラクター設定書
│   ├── imaizumi/
│   │   ├── profile.md                        ← 役回り・性格・口調
│   │   ├── anchor.md                         ← 画像生成プロンプト断片（英語）
│   │   ├── reference/
│   │   │   └── imaizumi_youtube_still.png
│   │   └── README.md
│   ├── sebastian/
│   │   ├── profile.md
│   │   ├── anchor.md
│   │   ├── reference/
│   │   │   └── sebastian_v1.png
│   │   └── README.md
│   ├── skette/
│   │   ├── profile.md
│   │   ├── anchor.md
│   │   ├── reference/
│   │   │   └── skette_real_machine.png
│   │   └── README.md
│   └── lineman/
│       ├── profile.md
│       ├── anchor.md
│       ├── reference/
│       │   └── lineman_real_machine.png
│       └── README.md
│
├── style-guide/                              ← スタイルプリセット
│   ├── shinkai_default/
│   │   ├── style.md
│   │   ├── prompt-fragment.md
│   │   └── samples/
│   ├── picturebook/
│   │   ├── style.md
│   │   ├── prompt-fragment.md
│   │   └── samples/
│   └── ghibli_bg/
│       ├── style.md
│       ├── prompt-fragment.md
│       └── samples/
│
├── episodes/                                 ← 各回の成果物（4コマ）
│   └── 001-2026-05-12-設計室の朝/            ← <連番>-<投稿予定日>-<タイトル>
│       ├── README.md                         ← この回のメタ情報、お題、最終採用パターン
│       ├── theme.md                          ← ユーザー提示のお題（原文）
│       ├── patterns/
│       │   ├── pattern-a/
│       │   │   ├── plot.md                   ← 起承転結＋台詞案
│       │   │   ├── prompt.md                 ← 最終 codex プロンプト
│       │   │   └── generated.png
│       │   ├── pattern-b/
│       │   ├── pattern-c/
│       │   └── pattern-d/
│       ├── final/                            ← 採用版（パターン選択後）
│       │   ├── plot.md
│       │   ├── prompt.md
│       │   └── final.png
│       ├── post.md                           ← X 投稿用テキスト案（Phase 3）
│       └── notes.md                          ← レビューコメント、採用理由、改善点メモ
│
├── news/                                     ← ニュース投稿（Phase 3）
│   └── YYYY-MM-DD-<title>/
│       ├── draft.md
│       ├── media/
│       └── post.md
│
├── analytics/                                ← X API 分析結果（Phase 3）
│   └── YYYY-MM/
│       ├── self_summary.json
│       ├── industry_benchmark.json
│       └── report.md
│
├── docs/
│   ├── superpowers/
│   │   ├── specs/                            ← 設計仕様書
│   │   │   └── 2026-05-03-x-account-ops-design.md  ← 本書
│   │   └── plans/                            ← 実装計画書
│   ├── runbooks/                             ← 運用手順
│   │   ├── codex-install.md
│   │   ├── codex-relogin.md
│   │   └── weekly-4koma-flow.md
│   └── decisions/                            ← ADR
│       └── 0001-subprocess-over-mcp.md
│
└── README.md                                 ← プロジェクト概要・新規参画者向け
```

### 6.1 命名規則

- **エピソード**：`<3桁連番>-<投稿予定日YYYY-MM-DD>-<日本語タイトル(短)>` 例：`001-2026-05-12-設計室の朝`
- **キャラID**：英小文字、ハイフンなし。`imaizumi`, `sebastian`, `skette`, `lineman`
- **スタイルID**：英小文字＋アンダースコア。`shinkai_default`, `picturebook`, `ghibli_bg`
- **ファイル**：Markdown は `kebab-case.md`、画像は `<id>_<説明>.png`
- **言語**：仕様書・README・profile は **日本語**、`anchor.md` / `prompt-fragment.md` は **英語**（画像生成モデル向け）

---

## 第7章 プラグイン内部構造（`.claude/plugins/lineworks-x-ops/`）

```
.claude/plugins/lineworks-x-ops/
├── plugin.json                               ← プラグインマニフェスト
├── README.md
│
├── skills/
│   ├── 4koma-compose/                        ← 4コマ構成案を作る
│   │   └── SKILL.md
│   ├── 4koma-image-gen/                      ← 画像生成プロンプト組立＋codex呼出
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── compose-prompt.sh             ← anchor + style + scene 結合
│   │       └── invoke-codex.sh               ← codex exec ラッパ
│   ├── x-news-draft/                         ← Phase 3
│   │   └── SKILL.md
│   └── x-analytics/                          ← Phase 3
│       └── SKILL.md
│
├── agents/
│   └── manga-director/                       ← 4コマ全体を仕切るエージェント
│       └── AGENT.md
│
├── commands/
│   ├── new-4koma.md                          ← /new-4koma <お題>
│   ├── refine-4koma.md                       ← /refine-4koma <ep-id> <pat> <指示>
│   ├── finalize-4koma.md                     ← /finalize-4koma <ep-id> <pat>
│   └── ship-4koma.md                         ← /ship-4koma（Phase 3）
│
└── hooks/                                    ← Phase 1 では空
```

### 7.1 各コンポーネントの責務

| コンポーネント | 責務 | 入力 | 出力 |
|---------------|------|------|------|
| `manga-director` (agent) | エピソード生成全体を統括、各スキルを順番に呼ぶ | お題（自由テキスト） | `episodes/<新規>/` 配下一式 |
| `4koma-compose` (skill) | 起承転結とキャラ配役、台詞案を作る | お題＋キャスト情報 | `plot.md` |
| `4koma-image-gen` (skill) | character/style 断片を組合せて codex に渡す | `plot.md` ＋ `style preset` 指定 | `prompt.md` ＋ `generated.png` |
| `/new-4koma` (command) | エントリポイント。manga-director を起動、N=4 パターン並行生成 | `<お題>` `[--patterns N]` | 新エピソードフォルダ生成開始 |
| `/refine-4koma` (command) | 既存パターンを再生成・微調整 | `<ep-id>` `<pattern-id>` `<修正指示>` | `generated_v2.png` 等 |
| `/finalize-4koma` (command) | 採用パターンを `final/` に確定 | `<ep-id>` `<pattern-id>` | `final/final.png`、`notes.md` |
| `/ship-4koma` (command) | （Phase 3）`final.png` ＋ `post.md` を X に投稿 | `<ep-id>` | 投稿結果ログ |

---

## 第8章 ワークフロー（4コマ生産パイプライン）

### 8.1 全体タイムライン（1エピソード分）

```
[ユーザー]                               [Claude Code / プラグイン]                        [Codex CLI]                  [gpt-image-2]
   │                                              │                                            │                              │
   │ /new-4koma "<お題>"                          │                                            │                              │
   ├─────────────────────────────────────────────▶│                                            │                              │
   │                                              │ ① エピソードフォルダ作成 + theme.md 保存    │                              │
   │                                              │                                            │                              │
   │                                              │ ② manga-director 起動                       │                              │
   │                                              │                                            │                              │
   │                                              │ ③ 4koma-compose ×4 並列                     │                              │
   │                                              │   pattern-{a,b,c,d}/plot.md                │                              │
   │                                              │                                            │                              │
   │                                              │ ④ 4koma-image-gen ×4 並列                   │                              │
   │                                              │   ┌─ codex exec --ephemeral ─────────────▶│ codex CLI 起動               │
   │                                              │   │   -i characters/<出演>/reference/*    │  ├─ $imagegen 内部呼出 ─────▶│
   │                                              │   │   -i style-guide/<preset>/samples/*   │  │                            │ gpt-image-2 で生成
   │                                              │   │   "<組立済プロンプト> $imagegen"      │  │                            │
   │                                              │   │                                          │  ◀─ ig_*.png ───────────────┤
   │                                              │   │ ←── stdout ──────────────────────────────│                              │
   │                                              │   ⑤ 画像移送                                  │                              │
   │                                              │     → episodes/<id>/patterns/<x>/generated.png                              │
   │                                              │                                            │                              │
   │ ⑥ 4枚プレビュー表示                            │                                            │                              │
   │◀─────────────────────────────────────────────│                                            │                              │
   │                                              │                                            │                              │
   │ ⑦ レビュー＆指示                               │                                            │                              │
   │   "Cベース、3コマ目だけBの構図"                 │                                            │                              │
   ├─────────────────────────────────────────────▶│                                            │                              │
   │                                              │ ⑧ /refine-4koma 内部呼出 → v2.png            │                              │
   │ (必要なら反復)                                 │                                            │                              │
   │                                              │                                            │                              │
   │ ⑨ /finalize-4koma <id> pattern-c              │                                            │                              │
   ├─────────────────────────────────────────────▶│                                            │                              │
   │                                              │ ⑩ pattern-c → final/ に確定保存              │                              │
   │                                              │                                            │                              │
   │ (Phase 3) /ship-4koma <id>                    │                                            │                              │
   ├─────────────────────────────────────────────▶│ X API 投稿 (Phase 3)                        │                              │
```

### 8.2 各ステップの詳細責務

| Step | 責務 | 担当 | 入力 | 出力 |
|------|------|------|------|------|
| ① | エピソードフォルダ生成、`theme.md` 保存 | `manga-director` | お題テキスト | `episodes/<id>/theme.md` |
| ② | エージェント全体オーケストレーション | `manga-director` | お題＋キャスト一覧 | 後続呼び分け |
| ③ | お題→プロット4案を並列生成 | `4koma-compose` ×4 | お題、キャスト anchor | `pattern-*/plot.md` |
| ④ | プロット→画像生成プロンプト組立、Codex呼出 | `4koma-image-gen` ×4 | `plot.md`、style preset、character anchor | `pattern-*/prompt.md`、生成画像 |
| ⑤ | Codex出力画像をエピソードフォルダに移送 | `4koma-image-gen` | `~/.codex/generated_images/...` | `pattern-*/generated.png` |
| ⑥ | 4パターンを並べて表示 | Claude Code | 4枚PNG | 視覚プレビュー |
| ⑦ | レビュー＆指示 | **ユーザー** | 4パターン | 修正指示 |
| ⑧ | 修正・再生成ループ | `/refine-4koma` | エピID＋パターンID＋修正指示 | `generated_v2.png` 等 |
| ⑨ | 採用パターン確定 | **ユーザー** | エピID＋採用パターンID | `/finalize-4koma` 起動 |
| ⑩ | `final/` 配下に複製、notes記録 | `manga-director` | 採用指示 | `final/final.png`、`notes.md` |
| (P3) | X 投稿 | `/ship-4koma` | エピID | 投稿結果ログ |

### 8.3 並列実行とエラー処理

- **③④の並列度**：4パターンを **同時に** 生成（Claude Code の並列ツール呼出 or `xargs -P 4` 系）
- **失敗時**：4本中 1〜2本がエラー（クォータ超過・ネットワーク等）した場合、残りで先に進める＋エラーパターンは `pattern-*/error.log` 残してスキップ
- **冪等性**：同じ `episode-id` に対して `/new-4koma` を再実行しても、既存パターンは上書きせず `pattern-a-v2/` のように接尾辞付きで追加（or 明示的に `--overwrite` フラグで上書き）

### 8.4 マルチターン対話との関係

- **Phase 1 デフォルト**：`--ephemeral` で各 codex 呼出は独立。連続性は**ファイル経由のみ**
- **将来オプション**：`/refine-4koma` で同じ session id を resume（Phase 1 後半で検証）

### 8.5 Phase 1 受入条件

1. ✅ 任意のお題テキストから **`/new-4koma` 1コマンドで4パターンの4コマ漫画画像が生成される**
2. ✅ 生成画像が **水彩画チック** に統一されている（style preset の効果が確認できる）
3. ✅ 出演キャラの **ビジュアルが回を跨いで安定** している（character reference の効果）
4. ✅ 4パターンが **互いに有意に異なる** 構図/オチを持つ（コピーではない）
5. ✅ `/refine-4koma` で **部分修正→再生成** ができる
6. ✅ `/finalize-4koma` で **採用版が `final/` に確定** される
7. ✅ Warp(CLI) と Claude Code デスクトップ **両方で同一動作** する
8. ✅ サンプルエピソード **3〜5本** を完成させ、Phase 2 の社長承認に供せる状態

### 8.6 自動スケジューリング方針

`/loop` `/schedule` 等の自動トリガーは **本仕様から除外**。完全に **今泉課長の発意起動モデル** に統一する。将来必要が生じれば後から追加する。

### 8.7 運用環境

| 環境 | 用途 |
|------|------|
| Warp ターミナル + Claude Code CLI | 主にバックエンド作業、デバッグ、長時間ジョブ |
| Claude Code デスクトップアプリ | 4コマレビュー、画像確認、対話的な絵柄修正 |

両環境で同じプラグイン・同じスキル・同じファイル構造が動作することを Phase 1 の受入条件に含める。

### 8.8 コスト試算

- 1お題 = 4パターン生成 ≒ **約90K tokens**（22K × 4）
- 修正1回 ≒ +22K
- 週1運用 = 月4回 × 90K + 修正10回 × 22K ≒ **月600K tokens**
- ChatGPT Team プランの Codex 利用枠内に十分収まる想定

---

## 第9章 制約・リスク・配慮事項

| カテゴリ | 制約／リスク | 緩和策 |
|---------|------------|--------|
| **顧客機密** | 一品一用品の実機・客先設備が画像に映り込む可能性 | 水彩画＋4コマで意図的にぼかす、`prompt.md` に "no real customer products / logos" を毎回必須挿入、Phase 1 受入チェックに含める |
| **社名混同** | 同名の LINE系グループウェア「LINE WORKS」と検索文脈で混同 | キャラ・投稿文・プロフィールで「**株式会社ラインワークス（千葉）**」と明示。ロゴ・色味も自社アイデンティティを強調 |
| **本人肖像権** | 今泉課長は実在ご本人がモデル | 似顔絵的忠実度は「識別性ありのデフォルメ」止まり、リアル似顔絵化はしない |
| **AI生成物の表記** | プラットフォーム規約・コンプライアンス | 投稿テキストに「水彩風AIイラスト」等の控えめ明示をデフォルト含める（Phase 3 で詳細詰め） |
| **画像生成クォータ超過** | 4パターン×週次×修正ループ | 月次クォータ消費を `analytics/` に記録、80%到達でアラート（Phase 3）。緊急時は OpenAI Image API（環境変数）にフォールバック |
| **キャラ一貫性の崩れ** | 画像生成AIは顔・形状の安定維持が苦手 | `-i` フラグで毎回 character reference を添付、生成後に視覚目視チェック、崩れたら refine ループ |
| **Codex 認証切れ** | refresh token の使用済み等で 401（Phase 0 で実発生） | `runbooks/codex-relogin.md` を整備、`/new-4koma` 開始時に `codex login status` 事前チェック |
| **Windows パス／日本語フォルダ名** | プロジェクトルートが日本語名 | スクリプト内では絶対パスを `"..."` で必ずクォート、Windows + Git Bash + PowerShell の3環境で動作確認 |
| **可逆性のない投稿** | X 投稿後の取り消しは履歴に残る | Phase 3 の `/ship-4koma` は必ず人間最終承認（自動投稿しない）、削除手順も runbook 化 |
| **属人化** | 今泉課長が運用主担当 | `docs/runbooks/` を Phase 1 から並行整備、新規参画者が `README.md` だけで概要把握できる構造 |

---

## 第10章 Phase 1 納品物（Deliverables）

Phase 1 完了時点で、以下が **存在し動作する** ことが受入条件。

### 10.1 ファイル成果物

| 区分 | 成果物 |
|------|--------|
| 仕様書 | `docs/superpowers/specs/2026-05-03-x-account-ops-design.md`（本書） |
| 実装計画 | `docs/superpowers/plans/2026-05-XX-phase1-implementation.md`（writing-plans スキルで作成） |
| ADR | `docs/decisions/0001-subprocess-over-mcp.md` |
| Runbook | `docs/runbooks/codex-install.md`、`codex-relogin.md`、`weekly-4koma-flow.md` |
| キャラ設定書（v1） | `characters/{imaizumi,sebastian,skette,lineman}/` 各 `profile.md` `anchor.md` `reference/*.png` `README.md` |
| スタイルガイド | `style-guide/{shinkai_default,picturebook,ghibli_bg}/` 各 `style.md` `prompt-fragment.md` `samples/*.png` |
| プラグイン | `.claude/plugins/lineworks-x-ops/` 配下一式（`plugin.json`、`skills/{4koma-compose,4koma-image-gen}/`、`agents/manga-director/`、`commands/{new,refine,finalize}-4koma.md`）|
| サンプル | `episodes/001-...` ～ `episodes/005-...` の 3〜5本完成エピソード（社長提示用）|
| README | プロジェクトルート `README.md`（新規参画者向け） |

### 10.2 動作受入条件

第 8.5 節の8項目に加えて：

9. ✅ `docs/runbooks/weekly-4koma-flow.md` の手順通りに、他の人（例：社長）が見て概要を理解できる
10. ✅ Phase 2 移行時、社長承認用のサンプル4コマ集をプレゼンテーション形式（README ＋ final.png 一覧）で出力可能

---

## 第11章 未決事項・Phase 2以降への送り

**方針**：Phase 1 で必須なのは **character sheet v1（最低限動く品質）** までとし、それ以外の未決事項は Phase 2 以降で順次対応する。Phase 1 を肥大化させない。

| # | 項目 | 対応Phase | 備考 |
|---|------|----------|------|
| 1 | セバスチャンの最終ビジュアル詳細（既存社内Slackアバター有無の確認、画風の最終化） | 2 | character sheet v1 → v2 改良の中で |
| 2 | 今泉課長の似顔絵的忠実度の最終キャリブレーション | 2 | サンプル数本作って判断 |
| 3 | SKETTE / LINEMAN の実機写真リファレンス入手・選定 | 1（v1のみ）／2（高品質化） | Phase 1 では暫定写真でも可 |
| 4 | スタイルプリセット間の相互運用（混合プリセット可否、優先度） | 2+ | 実運用で必要性判断 |
| 5 | 直前回最終コマを `-i` 添付してシリーズ連続性を出す機能 | 2 | 実装容易性次第 |
| 6 | サンプル4コマの社長レビュー方法（紙印刷／スライド／画面共有） | 2 | 社長の好みに合わせる |
| 7 | ニュース投稿系（`x-news-draft`）の文案テンプレート設計 | 3 | 求人／受賞／特許／節目それぞれのテンプレ |
| 8 | X 開発者ポータル法人申請のステータス・必要書類 | 3 | 別途進行 |
| 9 | X API バージョン・必要権限スコープ・レートリミット詳細 | 3 | 申請承認後に確定 |
| 10 | 投稿時の AI生成物表記の文言・粒度（プラットフォーム規約準拠） | 3 | 規約変動を継続ウォッチ |
| 11 | 月次分析リポート（`x-analytics`）の指標設計 | 3 | 業界他社のサンプル収集後 |
| 12 | Codex MCP 連携への移行検討（subprocess→MCP） | 2+ | サブプロセス運用で痛みが出たら |
| 13 | OpenAI APIキー従量課金へのフォールバック発動条件・コスト上限 | 2+ | 実利用クォータ消費パターンが見えた時点で |
| 14 | Codex セッション resume 機能を `/refine-4koma` で活用するか | 2 | 実装試行→効果次第 |

---

## 付録A：Phase 0 検証で得られた事実（参考データ）

### A.1 Codex CLI 環境

- バージョン：`codex-cli 0.128.0`
- インストールパス：`/c/Users/imaizumi.LINEWORKS-NET/AppData/Roaming/npm/codex`
- 認証：ChatGPT Team プラン（`imaizumi@lineworks.co.jp`）、有効期限 〜 2026-08-12
- デフォルトモデル：`gpt-5.5`
- 画像生成モデル：`gpt-image-2`（2026-04-21リリース）
- 画像出力先：`~/.codex/generated_images/<session_id>/ig_*.png`

### A.2 MCP サーバー機能

`codex mcp-server` が公開する MCP ツール：

| ツール | 役割 | 主な引数 |
|--------|------|---------|
| `codex` | 新規 Codex セッション開始 | `prompt` (必須), `model`, `cwd`, `sandbox`, etc. |
| `codex-reply` | 既存セッション継続 | `prompt`, `threadId` |

`$imagegen` は独立ツールではなく `prompt` 内のキーワードとして扱われる。

### A.3 トークン消費量実測

| 操作 | 消費トークン |
|------|------------|
| 短いテキスト応答（"PING_OK"） | 1,669 |
| 1枚の水彩画像生成 | 22,671 |

---

## 付録B：本仕様書の改訂履歴

| 版 | 日付 | 変更概要 |
|----|------|---------|
| v1.0 | 2026-05-03 | 初版作成（Phase 0 設計仕様確定） |

---

**文書終わり**
