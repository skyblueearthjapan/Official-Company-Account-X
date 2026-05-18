#!/usr/bin/env python3
"""
Discord Bot for LINEWORKS X-Ops
携帯Discordから VPS Claude Code へ指示を送り、生成画像を返す。

実行: cd /opt/lineworks-x-ops && .venv/bin/python scripts/discord_bot.py
"""
import asyncio
import datetime as _dt
import logging
import os
import re
import time
from pathlib import Path

import discord
from discord.ext import tasks
from dotenv import load_dotenv

# ============================================================
# 自然文・スラッシュ経由の投稿依頼検出
# ============================================================
# Claude の応答末尾に `!publish <episode_id>` が単独行で現れたら自動で承認フロー起動
# - re.MULTILINE: 各行頭で ^ がマッチ
# - episode_id は \S+ で 非空白文字列を吸う（日本語含む）
PUBLISH_MARKER_RE = re.compile(r"^!publish[ \t]+(\S+)[ \t]*$", re.MULTILINE)

# ============================================================
# Config
# ============================================================
PROJECT_ROOT = Path("/opt/lineworks-x-ops")
EPISODES_DIR = PROJECT_ROOT / "episodes"
LOG_FILE = PROJECT_ROOT / "logs" / "discord_bot.log"
LOG_FILE.parent.mkdir(exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("DISCORD_BOT_TOKEN not found in .env")

# ALLOWED_USER_IDS: 空 (= 全員許可) or カンマ区切りで Discord ユーザーIDを指定
_allowed = os.environ.get("DISCORD_ALLOWED_USER_IDS", "").strip()
ALLOWED_USER_IDS = {int(x) for x in _allowed.split(",") if x.strip().isdigit()}

# Claude CLI command timeout (seconds). 4コマ生成は5-8分かかる
CLAUDE_TIMEOUT = 600

# X 投稿関連
X_TWEET_LIMIT = 280
PUBLISH_APPROVAL_TIMEOUT = 600  # ボタン待機 10 分

# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("xops-bot")


# ============================================================
# Helpers
# ============================================================
def snapshot_pngs() -> set[Path]:
    return set(EPISODES_DIR.rglob("*.png"))


async def send_chunked(channel, text: str, prefix: str = ""):
    """Discord 1メッセージ2000文字制限対応。code block形式で送る。"""
    if not text.strip():
        return
    chunk_size = 1900 - len(prefix) - 10
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        await channel.send(f"{prefix}```\n{chunk}\n```")


async def upload_pngs(channel, pngs: list[Path]):
    """Discord は1メッセージあたり10ファイルまで・各25MBまで。"""
    if not pngs:
        return
    pngs = sorted(pngs)
    total = len(pngs)
    for i in range(0, total, 10):
        batch = pngs[i : i + 10]
        files = []
        captions = []
        for p in batch:
            try:
                rel = p.relative_to(PROJECT_ROOT)
            except ValueError:
                rel = p
            files.append(discord.File(str(p)))
            captions.append(f"📷 `{rel}`")
        await channel.send(content="\n".join(captions), files=files)


async def run_claude(prompt: str) -> tuple[int, str, str, float]:
    """claude -p をサブプロセスで実行。(returncode, stdout, stderr, elapsed_sec)"""
    started = time.monotonic()
    proc = await asyncio.create_subprocess_exec(
        "claude",
        "-p",
        prompt,
        "--dangerously-skip-permissions",
        cwd=str(PROJECT_ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(), timeout=CLAUDE_TIMEOUT
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", f"TIMEOUT after {CLAUDE_TIMEOUT}s", time.monotonic() - started
    return (
        proc.returncode,
        stdout_b.decode("utf-8", errors="replace"),
        stderr_b.decode("utf-8", errors="replace"),
        time.monotonic() - started,
    )


# ============================================================
# X 投稿: 承認ボタン UI
# ============================================================
class PublishApprovalView(discord.ui.View):
    """投稿前の最終承認 View。✅承認 / ❌キャンセル のボタン2つ。"""

    def __init__(self, *, episode_id: str, requester_id: int):
        super().__init__(timeout=PUBLISH_APPROVAL_TIMEOUT)
        self.episode_id = episode_id
        self.requester_id = requester_id
        self.decided = False
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.requester_id:
            await interaction.response.send_message(
                "このボタンは `!publish` を打った本人のみ操作できます。",
                ephemeral=True,
            )
            return False
        return True

    async def _disable_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(
        label="✅ 承認して X に投稿", style=discord.ButtonStyle.success
    )
    async def approve(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.decided = True
        await self._disable_buttons()
        await interaction.response.edit_message(
            content=f"⏳ X に投稿中… `{self.episode_id}`",
            view=self,
        )

        try:
            from post_to_x import post_episode

            result = await asyncio.to_thread(
                post_episode,
                self.episode_id,
                approved_by=str(interaction.user.id),
            )
        except Exception as e:
            log.exception("Publish failed for %s", self.episode_id)
            await interaction.followup.send(f"❌ 投稿失敗: `{e}`")
            self.stop()
            return

        await interaction.followup.send(
            "✅ **投稿完了**\n"
            f"- episode: `{self.episode_id}`\n"
            f"- tweet_id: `{result.tweet_id}`\n"
            f"- URL: {result.url}\n"
            f"- 投稿時刻: `{result.posted_at.isoformat()}`"
        )
        self.stop()

    @discord.ui.button(label="❌ キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.decided = True
        await self._disable_buttons()
        await interaction.response.edit_message(
            content=f"❌ キャンセルしました（`{self.episode_id}`）",
            view=self,
        )
        self.stop()

    async def on_timeout(self):
        if self.decided or self.message is None:
            return
        await self._disable_buttons()
        try:
            await self.message.edit(
                content=(
                    f"⏰ タイムアウト（{PUBLISH_APPROVAL_TIMEOUT // 60}分）— "
                    f"投稿はキャンセルされました（`{self.episode_id}`）"
                ),
                view=self,
            )
        except discord.HTTPException:
            pass


async def send_publish_preview(
    channel: discord.abc.Messageable,
    episode_id: str,
    requester_id: int,
    *,
    prefix: str = "",
) -> discord.Message | None:
    """プレビュー＋承認ボタン View を組み立てて送信。

    !publish からも、予約発火からも共通で呼ばれる。
    成功時は送信した Message を返す。エラーは channel に通知して None を返す。
    """
    try:
        from post_to_x import EpisodePost

        episode = EpisodePost.load(episode_id)
    except FileNotFoundError as e:
        await channel.send(f"❌ {e}")
        return None
    except ValueError as e:
        await channel.send(f"❌ 投稿本文の検証に失敗: `{e}`")
        return None
    except ImportError as e:
        await channel.send(
            f"❌ post_to_x モジュール読込失敗: `{e}` "
            "(VPS で `pip install -r requirements.txt` を実行してください)"
        )
        return None

    char_count = len(episode.body_text)
    preview = (
        f"{prefix}📝 **投稿プレビュー** — `{episode_id}`\n"
        f"```\n{episode.body_text}\n```\n"
        f"文字数: **{char_count}/{X_TWEET_LIMIT}** ｜ "
        f"画像: `{episode.image_path.relative_to(PROJECT_ROOT)}`\n\n"
        f"⚠️ 承認すると **本番アカウント** に即投稿します。\n"
        f"承認/キャンセルは {PUBLISH_APPROVAL_TIMEOUT // 60} 分以内にどうぞ。"
    )

    view = PublishApprovalView(
        episode_id=episode_id,
        requester_id=requester_id,
    )
    sent = await channel.send(
        content=preview,
        file=discord.File(str(episode.image_path)),
        view=view,
    )
    view.message = sent
    log.info(
        f"Publish preview sent: episode={episode_id}, requester={requester_id}"
    )
    return sent


async def handle_publish_command(message: discord.Message, episode_id: str):
    """!publish <ep-id> 実行時のハンドラ。プレビュー + 承認ボタンを表示する。"""
    await send_publish_preview(
        message.channel, episode_id, message.author.id
    )


# ============================================================
# X 投稿: 予約スケジュール (!schedule / !schedule-list / !schedule-cancel)
# ============================================================
SCHEDULE_HELP = (
    "**予約コマンド使い方**\n"
    "```\n"
    "!schedule <episode_id> <YYYY-MM-DD HH:MM>   # JST で予約登録\n"
    "!schedule-list                              # 予約一覧\n"
    "!schedule-cancel <sched-id>                 # 予約取消\n"
    "```\n"
    "例: `!schedule 002-2026-05-18-創立45周年記念式典PR2 2026-05-20 06:55`\n"
    "予約時刻になると、このチャンネルへ承認ボタン付きプレビューが自動表示されます。"
)


async def handle_schedule_add(message: discord.Message, rest: str):
    if not rest:
        await message.channel.send(SCHEDULE_HELP)
        return
    tokens = rest.split()
    if len(tokens) < 3:
        await message.channel.send(
            f"❌ 引数不足: `{rest}`\n\n{SCHEDULE_HELP}"
        )
        return
    episode_id, date_str, time_str = tokens[0], tokens[1], tokens[2]

    try:
        from scheduler import add_schedule, parse_jst_datetime, JST
        from post_to_x import EpisodePost

        EpisodePost.load(episode_id)  # 存在チェック
    except FileNotFoundError as e:
        await message.channel.send(f"❌ {e}")
        return
    except ValueError as e:
        await message.channel.send(f"❌ {e}")
        return
    except ImportError as e:
        await message.channel.send(f"❌ モジュール読込失敗: `{e}`")
        return

    try:
        preview_at = parse_jst_datetime(date_str, time_str)
    except ValueError:
        await message.channel.send(
            f"❌ 日時形式が不正: `{date_str} {time_str}` — `YYYY-MM-DD HH:MM` (JST) で指定してください"
        )
        return

    now = _dt.datetime.now(JST)
    if preview_at <= now:
        await message.channel.send(
            f"❌ 指定時刻が過去です: `{preview_at.strftime('%Y-%m-%d %H:%M JST')}`"
        )
        return

    entry = add_schedule(
        episode_id=episode_id,
        preview_at=preview_at,
        channel_id=message.channel.id,
        approver_id=message.author.id,
    )
    delta = preview_at - now
    total_min = int(delta.total_seconds() // 60)
    hours, mins = divmod(total_min, 60)
    days, hours = divmod(hours, 24)
    delta_label_parts = []
    if days:
        delta_label_parts.append(f"{days}日")
    if hours or days:
        delta_label_parts.append(f"{hours}時間")
    delta_label_parts.append(f"{mins}分")
    delta_label = "".join(delta_label_parts)

    await message.channel.send(
        f"📅 **予約登録完了** — `{entry['id']}`\n"
        f"- episode: `{episode_id}`\n"
        f"- preview_at: `{preview_at.strftime('%Y-%m-%d %H:%M JST')}` ({delta_label}後)\n"
        f"- channel: <#{message.channel.id}>\n"
        f"- approver: <@{message.author.id}>\n\n"
        f"その時刻になったら、このチャンネルに承認ボタン付きプレビューを自動表示します。"
    )
    log.info(
        f"Schedule added: id={entry['id']} episode={episode_id} at={preview_at.isoformat()}"
    )


async def handle_schedule_list(message: discord.Message):
    try:
        from scheduler import load_schedules, JST
    except ImportError as e:
        await message.channel.send(f"❌ scheduler モジュール読込失敗: `{e}`")
        return
    entries = load_schedules()
    if not entries:
        await message.channel.send("📅 予約はまだ登録されていません。")
        return
    pending = [e for e in entries if e.get("status") == "pending"]
    other = [e for e in entries if e.get("status") != "pending"]

    lines = ["📅 **予約一覧**"]
    if pending:
        lines.append("\n**pending:**")
        for e in pending:
            lines.append(
                f"- `{e['id']}` ｜ {e['preview_at'][:16].replace('T', ' ')} JST ｜ `{e['episode_id']}`"
            )
    if other:
        lines.append("\n**履歴 (直近5件):**")
        for e in other[-5:]:
            lines.append(
                f"- `{e['id']}` ｜ {e.get('status')} ｜ `{e['episode_id']}`"
            )
    await message.channel.send("\n".join(lines))


async def handle_schedule_cancel(message: discord.Message, rest: str):
    sched_id = rest.strip()
    if not sched_id:
        await message.channel.send(
            "使い方: `!schedule-cancel <sched-id>` — ID は `!schedule-list` で確認"
        )
        return
    try:
        from scheduler import cancel_schedule
    except ImportError as e:
        await message.channel.send(f"❌ scheduler モジュール読込失敗: `{e}`")
        return
    result = cancel_schedule(sched_id)
    if result is None:
        await message.channel.send(
            f"❌ 取消できませんでした: `{sched_id}` (存在しない or 既に発火/取消済み)"
        )
        return
    await message.channel.send(
        f"🗑️ 予約を取消しました: `{sched_id}` (episode `{result['episode_id']}`)"
    )
    log.info(f"Schedule cancelled: {sched_id}")


# ============================================================
# 予約発火ループ
# ============================================================
@tasks.loop(seconds=30)
async def schedule_runner_loop():
    try:
        from scheduler import due_schedules, stale_schedules, mark_status
    except ImportError:
        log.exception("scheduler module import failed in loop")
        return

    # 24h 以上前のすり抜けエントリを missed 化
    for s in stale_schedules():
        log.warning(
            f"Marking stale schedule as missed: {s['id']} ({s['episode_id']})"
        )
        mark_status(s["id"], "missed")
        channel = client.get_channel(int(s["channel_id"]))
        if channel is not None:
            try:
                await channel.send(
                    f"⏰ 予約 `{s['id']}` (episode `{s['episode_id']}`) は "
                    f"24時間以上前の時刻だったため、自動で `missed` にしました。"
                )
            except discord.HTTPException:
                pass

    # 発火時刻に到達した pending を順次発火
    for s in due_schedules():
        sched_id = s["id"]
        log.info(
            f"Firing scheduled preview: {sched_id} -> {s['episode_id']}"
        )
        channel = client.get_channel(int(s["channel_id"]))
        if channel is None:
            log.error(
                f"Channel {s['channel_id']} not found for schedule {sched_id}"
            )
            mark_status(sched_id, "failed")
            continue
        try:
            preview_at = _dt.datetime.fromisoformat(s["preview_at"])
            prefix = (
                f"⏰ **予約発火** — `{sched_id}` "
                f"(予約時刻 {preview_at.strftime('%Y-%m-%d %H:%M JST')})\n"
            )
            sent = await send_publish_preview(
                channel,
                s["episode_id"],
                int(s["approver_id"]),
                prefix=prefix,
            )
            mark_status(sched_id, "sent" if sent is not None else "failed")
        except Exception:
            log.exception(f"Failed to fire schedule {sched_id}")
            mark_status(sched_id, "failed")


@schedule_runner_loop.before_loop
async def _before_schedule_loop():
    await client.wait_until_ready()


# ============================================================
# Discord client
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    log.info(f"Bot logged in as {client.user} (id={client.user.id})")
    log.info(f"Joined guilds: {[g.name for g in client.guilds]}")
    log.info(f"Allowed user IDs: {ALLOWED_USER_IDS or '(all users)'}")
    if not schedule_runner_loop.is_running():
        schedule_runner_loop.start()
        log.info("schedule_runner_loop started (interval=30s)")


@client.event
async def on_message(message: discord.Message):
    # Ignore self & other bots
    if message.author == client.user or message.author.bot:
        return

    content = message.content.strip()
    if not content:
        return

    # Access control
    if ALLOWED_USER_IDS and message.author.id not in ALLOWED_USER_IDS:
        log.warning(
            f"Denied: user={message.author} ({message.author.id}) content={content[:60]!r}"
        )
        return

    # Mention prefix removal (if bot was mentioned)
    if client.user in message.mentions:
        content = content.replace(f"<@{client.user.id}>", "").strip()
        if not content:
            return

    log.info(f"Received from {message.author} in #{message.channel}: {content[:120]!r}")

    # ----- Special command: !publish <episode-id> -----
    # Claude には流さず、X 投稿の承認フローを開始する
    if content.startswith("!publish"):
        parts = content.split(maxsplit=2)
        if len(parts) < 2 or not parts[1].strip():
            await message.channel.send(
                "使い方: `!publish <episode_id>`\n"
                "例: `!publish 001-2026-05-11-新拠点完成PR1`"
            )
            return
        await handle_publish_command(message, parts[1].strip())
        return

    # ----- Special commands: !schedule-* / !schedule -----
    # 順序重要: より具体的なサブコマンドを先に判定する
    if content.startswith("!schedule-list"):
        await handle_schedule_list(message)
        return
    if content.startswith("!schedule-cancel"):
        await handle_schedule_cancel(
            message, content[len("!schedule-cancel"):].strip()
        )
        return
    if content.startswith("!schedule"):
        await handle_schedule_add(
            message, content[len("!schedule"):].strip()
        )
        return

    # Acknowledge immediately
    await message.add_reaction("⏳")
    ack = await message.channel.send(f"⏳ 処理中...\n```\n{content[:200]}\n```")

    # Snapshot PNGs before
    before_pngs = snapshot_pngs()

    # Run claude
    rc, stdout, stderr, elapsed = await run_claude(content)

    # Find new PNGs
    after_pngs = snapshot_pngs()
    new_pngs = sorted(after_pngs - before_pngs)

    # Update reaction
    await message.remove_reaction("⏳", client.user)
    await message.add_reaction("✅" if rc == 0 else "❌")

    # Edit ack with summary
    summary = (
        f"{'✅' if rc == 0 else '❌'} "
        f"完了 (rc={rc}, {elapsed:.1f}s, 新規画像{len(new_pngs)}枚)"
    )
    try:
        await ack.edit(content=summary)
    except discord.HTTPException:
        await message.channel.send(summary)

    # Send Claude output
    if stdout:
        await send_chunked(message.channel, stdout)
    if stderr and rc != 0:
        await send_chunked(message.channel, stderr, prefix="⚠️ stderr ")

    # Upload new PNGs
    await upload_pngs(message.channel, new_pngs)

    # Claude の応答末尾に !publish マーカーがあれば承認フローを自動起動
    # （CLAUDE.md §D / skills/x-publish の仕様）
    if rc == 0 and stdout:
        match = PUBLISH_MARKER_RE.search(stdout)
        if match:
            ep_id = match.group(1).strip()
            log.info(
                f"Auto-detected publish marker from Claude output: episode_id={ep_id}"
            )
            await message.channel.send(
                f"🤖 Claude が投稿マーカーを検出しました → "
                f"`{ep_id}` の承認フローを起動します"
            )
            await handle_publish_command(message, ep_id)

    log.info(
        f"Done in {elapsed:.1f}s: rc={rc}, stdout={len(stdout)}b, "
        f"stderr={len(stderr)}b, new_pngs={len(new_pngs)}"
    )


def main():
    log.info("Starting Discord bot...")
    client.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
