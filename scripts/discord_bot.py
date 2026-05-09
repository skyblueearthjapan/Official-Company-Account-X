#!/usr/bin/env python3
"""
Discord Bot for LINEWORKS X-Ops
携帯Discordから VPS Claude Code へ指示を送り、生成画像を返す。

実行: cd /opt/lineworks-x-ops && .venv/bin/python scripts/discord_bot.py
"""
import asyncio
import logging
import os
import re
import time
from pathlib import Path

import discord
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


async def handle_publish_command(message: discord.Message, episode_id: str):
    """!publish <ep-id> 実行時のハンドラ。プレビュー + 承認ボタンを表示する。"""
    try:
        from post_to_x import EpisodePost

        episode = EpisodePost.load(episode_id)
    except FileNotFoundError as e:
        await message.channel.send(f"❌ {e}")
        return
    except ValueError as e:
        await message.channel.send(f"❌ 投稿本文の検証に失敗: `{e}`")
        return
    except ImportError as e:
        await message.channel.send(
            f"❌ post_to_x モジュール読込失敗: `{e}` "
            "(VPS で `pip install -r requirements.txt` を実行してください)"
        )
        return

    char_count = len(episode.body_text)
    preview = (
        f"📝 **投稿プレビュー** — `{episode_id}`\n"
        f"```\n{episode.body_text}\n```\n"
        f"文字数: **{char_count}/{X_TWEET_LIMIT}** ｜ "
        f"画像: `{episode.image_path.relative_to(PROJECT_ROOT)}`\n\n"
        f"⚠️ 承認すると **本番アカウント** に即投稿します。\n"
        f"承認/キャンセルは {PUBLISH_APPROVAL_TIMEOUT // 60} 分以内にどうぞ。"
    )

    view = PublishApprovalView(
        episode_id=episode_id,
        requester_id=message.author.id,
    )
    sent = await message.channel.send(
        content=preview,
        file=discord.File(str(episode.image_path)),
        view=view,
    )
    view.message = sent
    log.info(
        f"Publish preview sent: episode={episode_id}, requester={message.author}"
    )


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
