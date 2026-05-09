# X API 取得・設定ガイド

株式会社ラインワークス公式 X アカウントから自動投稿するための X (旧 Twitter) API 取得手順。

> 関連設計: `docs/superpowers/specs/2026-05-03-x-account-ops-design.md` §5.5
> 残作業表: `docs/REMAINING_WORK.md` §C
> .env テンプレ: `.env.example`

---

## 0. 前提

- 会社の公式 X アカウント（投稿先）が作成済みで、ログインできる状態であること
- 開発者申請は **会社（法人）の用途として** 行う
- 申請者は本人確認済みのアカウント所有者（社長 or 設計部担当）

---

## 1. プラン選定

| プラン | 月額 | 投稿数/月 | 備考 |
|---|---|---|---|
| **Free** | $0 | 500投稿/月（書込可） | ✅ **当社用途はこれで十分**（週1〜数本） |
| Basic | $200 | 3,000投稿/月 | 不要 |
| Pro | $5,000 | 300,000投稿/月 | 不要 |

> ⚠️ ゴールド認証（Premium Business Basic、年$2,000）は API とは別物。バッジ表示用途のみで、API利用には不要。

---

## 2. 取得すべきキー（4種類）

| 名称 | 用途 |
|---|---|
| **API Key** + **API Key Secret** | アプリ自体の認証（Consumer Key/Secret） |
| **Access Token** + **Access Token Secret** | 投稿アカウントの認証（OAuth 1.0a User Context） |
| Bearer Token | 読み取り専用 API（v2 Read）。投稿には不要だが念のため取得 |

→ 投稿には **API Key/Secret + Access Token/Secret の 4 つ** を `.env` に保存。

---

## 3. ステップ詳細

### Step 1. 公式 X アカウントにログイン

ブラウザで投稿先アカウントにログイン状態にしておく。

### Step 2. Developer Portal にアクセス

https://developer.x.com/en/portal/dashboard

「Sign up for Free Account」をクリック。

### Step 3. 利用目的を英語で記述（250字以上必須）

下記をコピペして、社名や用途を必要に応じて調整：

```text
We operate the official X account for LINEWORKS Inc., a Japanese
industrial robotics manufacturer based in Chiba. We use the API
exclusively to publish AI-assisted 4-panel watercolor manga content
about our company culture, design department activities, and
corporate news. All posts go through a mandatory human approval
flow on Discord before publishing. Posting frequency is
approximately 4-8 posts per month. We do not collect, store, or
analyze data from other users' tweets. We do not redistribute
Twitter content outside of X. The official account is operated
by the design department in coordination with general affairs
and the company president.
```

**和訳（社内承認用）:**

> 当社（株式会社ラインワークス、千葉、産業用ロボットメーカー）の公式 X アカウント運用専用。AI 補助で生成した水彩4コマ漫画コンテンツの投稿が主目的。Discord 上での人間の最終承認フローを必須とする。投稿頻度は月4〜8件程度。他ユーザーのツイートの収集・保存・分析・再配布は一切行わない。

### Step 4. 規約同意

- Developer Agreement に同意
- Restricted Use Cases（政府監視・選挙操作・医療データ等）→ **すべて No**

### Step 5. メール確認 → アプリ作成

承認メール（即時〜数時間）→ Portal で **Create App**
- App name: `lineworks-x-ops`（一意の名前であれば何でも可）

### Step 6. 各種キー発行 ⚠️ 最重要

「Keys and tokens」タブ：

1. **API Key & Secret** → Generate → **その場でコピー**（再表示不可）
2. **Bearer Token** → Generate → コピー
3. **Access Token & Secret** → Generate → コピー

→ 4 種類すべてを安全な場所（パスワードマネージャ等）に一時保存。
**画面を閉じると Secret は二度と表示できない**ので注意。

### Step 7. ⚠️ 権限設定（忘れがち）

「User authentication settings」 → Edit：

| 項目 | 設定値 |
|---|---|
| App permissions | ✅ **Read and write**（デフォルトは Read のみで投稿不可） |
| Type of App | Web App, Automated App or Bot |
| Callback URI | `http://localhost/`（投稿APIだけなら未使用、形式上必要） |
| Website URL | `https://lineworks.co.jp` |

→ Save 後、**Access Token を再生成**（権限変更後は古いトークンが効かない）

### Step 8. VPS への反映

VPS に SSH で入り、`/opt/lineworks-x-ops/.env` を編集：

```bash
ssh root@31.97.109.137
cd /opt/lineworks-x-ops
sudo -u lineworks cp .env.example .env   # 初回のみ
sudo -u lineworks nano .env              # 4つのキーと SCREEN_NAME を埋める
sudo -u lineworks chmod 600 .env
sudo systemctl restart xops-discord-bot  # サービス名は環境に合わせる
```

`.env` 該当項目:

```
X_API_KEY=...
X_API_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
X_SCREEN_NAME=lineworks_chiba
```

---

## 4. 動作確認

```bash
cd /opt/lineworks-x-ops
sudo -u lineworks .venv/bin/python scripts/post_to_x.py \
    001-2026-05-11-新拠点完成PR1 --dry-run
```

→ `OK tweet_id=DRYRUN` が出れば、エピソード読込と認証読込までは正常。
本番投稿は Discord から `!publish 001-2026-05-11-新拠点完成PR1` で承認ボタン経由。

---

## 5. 社内承認 (A6) 用 Q&A

| 質問 | 回答 |
|---|---|
| 費用は？ | 無料（Free Tier）。週1投稿なら制限内 |
| データ漏洩リスクは？ | キーは VPS の `.env`（`chmod 600`）にのみ保存、Git にコミットしない仕組み済み |
| 誤投稿リスクは？ | Discord 上で人間が承認ボタン押すまで投稿しない。タイムアウト10分で自動キャンセル |
| 取り消しは？ | API で削除可能。誤投稿時は即削除、`analytics/<YYYY-MM>/post-log.md` で追跡 |
| 中の人は？ | 自動投稿だが必ず人間が approve したものだけ。「中の人=設計部 + AI執事セバスチャン（コンテンツ作成）+ 人間（承認）」 |

---

## 6. トラブルシュート

| 症状 | 原因 | 対処 |
|---|---|---|
| 401 Unauthorized | キーが間違っている / 権限が Read のみ | Step 7 で Read and write に変更し、Token を再生成 |
| 403 Forbidden + "duplicate" | 同じ本文を直前に投稿 | 本文に絵文字や日付等を含めて差別化 |
| 429 Too Many Requests | レート制限 | 月 500 投稿（Free）。15分待って再試行 |
| `tweepy.errors.Forbidden: 453` | Free Tier でアクセスできないエンドポイント | v2 `create_tweet` + v1.1 `media_upload` のみを使用すること（本実装はそうしている） |
| 画像が添付されない | media_upload 失敗 / ファイルサイズ超過 | 画像 ≤ 5MB / PNG, JPG のみ。final.png のサイズを確認 |

---

## 7. 関連ファイル

| パス | 役割 |
|---|---|
| `.env.example` | 環境変数テンプレート |
| `scripts/post_to_x.py` | 投稿スクリプト本体（CLI + ライブラリ） |
| `scripts/discord_bot.py` | `!publish <ep-id>` コマンド + 承認ボタン |
| `requirements.txt` | tweepy 等の依存定義 |
| `analytics/<YYYY-MM>/post-log.md` | 投稿履歴の自動記録 |
| `episodes/<id>/final/final.png` | 投稿画像（必須） |
| `episodes/<id>/final/post-body.txt` | 投稿本文（≤280字, 必須） |
