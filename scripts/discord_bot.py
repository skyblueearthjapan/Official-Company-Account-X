#!/usr/bin/env python3
"""
Discord Bot for LINEWORKS X-Ops
携帯Discordから VPS Claude Code へ指示を送り、生成画像を返す。

実行: cd /opt/lineworks-x-ops && .venv/bin/python scripts/discord_bot.py
"""
import asyncio
import logging
import os
import time
from pathlib import Path

import discord
from dotenv import load_dotenv

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

    log.info(
        f"Done in {elapsed:.1f}s: rc={rc}, stdout={len(stdout)}b, "
        f"stderr={len(stderr)}b, new_pngs={len(new_pngs)}"
    )


def main():
    log.info("Starting Discord bot...")
    client.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
