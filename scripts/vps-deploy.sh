#!/usr/bin/env bash
# =====================================================================
# vps-deploy.sh — VPS 側のデプロイ手順を 1 コマンドにまとめたスクリプト
#
# 前提:
#   - root として実行する（sudo bash scripts/vps-deploy.sh）
#   - /opt/lineworks-x-ops/ にリポジトリが clone 済み
#   - .venv/ が作成済み (python -m venv .venv)
#   - tmux session 'xops' に 'discord-bot' window が存在
#   - .env が 4 つの X API キー + DISCORD_BOT_TOKEN を含む
#
# このスクリプトがやること:
#   1. git pull origin main
#   2. pip install -r requirements.txt --upgrade
#   3. .env の存在 + 権限 (chmod 600) を確認
#   4. tmux 内の Discord Bot を Ctrl-C → 再起動
#   5. post_to_x.py を --dry-run で起動して構成検証
# =====================================================================
set -euo pipefail

PROJECT_DIR=/opt/lineworks-x-ops
APP_USER=lineworks
TMUX_SESSION=xops
TMUX_WINDOW=discord-bot

cd "$PROJECT_DIR"

echo "==> [1/5] git pull"
sudo -u "$APP_USER" git pull origin main

echo "==> [2/5] pip install (upgrade)"
sudo -u "$APP_USER" .venv/bin/pip install -r requirements.txt --upgrade --quiet
echo "    installed: $(sudo -u "$APP_USER" .venv/bin/python -c 'import tweepy, discord; print(f"tweepy={tweepy.__version__} discord.py={discord.__version__}")')"

echo "==> [3/5] .env チェック"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "ERROR: $PROJECT_DIR/.env が見つかりません"
    echo "       sudo -u $APP_USER cp .env.example .env"
    echo "       sudo -u $APP_USER nano .env   # 4 つの X_API_* キーと DISCORD_BOT_TOKEN を埋める"
    echo "       sudo chmod 600 .env"
    exit 1
fi
chmod 600 "$PROJECT_DIR/.env"
chown "$APP_USER:$APP_USER" "$PROJECT_DIR/.env"

# 必須 env が埋まっているか軽く確認（値は表示しない）
missing=()
for v in DISCORD_BOT_TOKEN X_API_KEY X_API_SECRET X_ACCESS_TOKEN X_ACCESS_TOKEN_SECRET; do
    if ! grep -qE "^${v}=.+" "$PROJECT_DIR/.env"; then
        missing+=("$v")
    fi
done
if [ ${#missing[@]} -gt 0 ]; then
    echo "WARN: .env に値が入っていない変数があります: ${missing[*]}"
    echo "      X 投稿が失敗します。Bot 再起動は続行しますが .env を編集してください"
fi

echo "==> [4/5] tmux 内の Discord Bot を再起動"
if sudo -u "$APP_USER" tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    # 既存プロセスを Ctrl-C で停止
    sudo -u "$APP_USER" tmux send-keys -t "$TMUX_SESSION:$TMUX_WINDOW" C-c
    sleep 2
    # 起動コマンド送信
    sudo -u "$APP_USER" tmux send-keys -t "$TMUX_SESSION:$TMUX_WINDOW" \
        "cd $PROJECT_DIR && .venv/bin/python scripts/discord_bot.py" Enter
    echo "    Bot を $TMUX_SESSION:$TMUX_WINDOW で再起動しました"
    echo "    確認: sudo -u $APP_USER tmux attach -t $TMUX_SESSION  (デタッチは Ctrl-b d)"
    echo "    ログ: tail -f $PROJECT_DIR/logs/discord_bot.log"
else
    echo "WARN: tmux session '$TMUX_SESSION' が存在しません"
    echo "      手動起動: sudo -u $APP_USER tmux new -s $TMUX_SESSION -d"
    echo "      その後: sudo -u $APP_USER tmux send-keys -t $TMUX_SESSION \\"
    echo "              'cd $PROJECT_DIR && .venv/bin/python scripts/discord_bot.py' Enter"
fi

echo "==> [5/5] post_to_x.py --dry-run で構成検証 (実際の投稿はしない)"
if sudo -u "$APP_USER" .venv/bin/python scripts/post_to_x.py \
    "001-2026-05-11-新拠点完成PR1" --dry-run; then
    echo "    ✅ dry-run OK — episode 001 は読み込み・検証通過"
else
    echo "    ⚠️  dry-run NG — final.png または post-body.txt の配置を確認"
fi

echo ""
echo "==> done."
echo ""
echo "次は Discord で:"
echo "    !publish 001-2026-05-11-新拠点完成PR1"
echo "→ プレビュー + 承認ボタンが表示されます。"
echo "  ✅承認 を押すと実際の投稿が走ります。"
echo "  ❌キャンセル / 10 分放置でキャンセル。"
