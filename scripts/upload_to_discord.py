#!/usr/bin/env python3
"""
4枚の生成画像を Discord にアップロードする単発スクリプト。
Usage: .venv/bin/python scripts/upload_to_discord.py <ep_id> [channel_id]

channel_id 省略時は環境変数 DISCORD_DEFAULT_CHANNEL_ID、なければサーバー第一の text channel に送信。
"""
import asyncio
import os
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv

PROJECT_ROOT = Path("/opt/lineworks-x-ops")
load_dotenv(PROJECT_ROOT / ".env")
TOKEN = os.environ["DISCORD_BOT_TOKEN"]

if len(sys.argv) < 2:
    print("Usage: upload_to_discord.py <ep_id> [channel_id]")
    sys.exit(1)

EP_ID = sys.argv[1]
CHANNEL_ID = int(sys.argv[2]) if len(sys.argv) >= 3 else None

EP_DIR = PROJECT_ROOT / "episodes" / EP_ID
PATTERNS = ["pattern-a", "pattern-b", "pattern-c", "pattern-d"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    target = None
    if CHANNEL_ID:
        target = client.get_channel(CHANNEL_ID)
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    target = ch
                    break
            if target:
                break
    if target is None:
        print("No usable channel found")
        await client.close()
        return

    print(f"Sending to: #{target.name} ({target.id}) in {target.guild.name}")

    await target.send(
        f"🎬 **エピソード `{EP_ID}` 生成完了 (4パターン比較)**\n"
        f"上部バナー: `(株)ラインワークス★ 公式アカウント X 4コマコンテンツ No.001`\n"
        f"4枚を見比べてベストを選んでください。"
    )

    files = []
    for p in PATTERNS:
        png = EP_DIR / "patterns" / p / "generated.png"
        if png.exists():
            files.append((p, png))

    # 4ファイル一括送信（Discord は10ファイル/メッセージまで OK）
    discord_files = []
    captions = []
    for p, png in files:
        plot = (EP_DIR / "patterns" / p / "plot.md").read_text(encoding="utf-8")
        # plot.md から style preset を抽出
        style = "?"
        for i, line in enumerate(plot.splitlines()):
            if line.startswith("## Style preset suggestion"):
                for j in range(i + 1, min(i + 5, len(plot.splitlines()))):
                    cand = plot.splitlines()[j].strip()
                    if cand and not cand.startswith("**"):
                        style = cand
                        break
                break
        discord_files.append(discord.File(str(png), filename=f"{p}.png"))
        captions.append(f"📷 **{p}** (style: {style})")

    await target.send(content="\n".join(captions), files=discord_files)

    print(f"Uploaded {len(discord_files)} files")
    await client.close()


client.run(TOKEN, log_handler=None)
