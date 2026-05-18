"""
scripts/scheduler.py — X 投稿の予約キュー管理

scheduled-posts.json (project root) を読み書きする小さなモジュール。
discord_bot.py から import される前提で、Discord SDK には依存しない。

Schedule entry shape:
    {
      "id": "sched-xxxxxxxx",                       # ユニーク ID
      "episode_id": "002-...",
      "preview_at": "2026-05-20T06:55:00+09:00",    # ISO 8601 with TZ
      "channel_id": 123,                            # 発火時に Bot がプレビューを送るチャンネル
      "approver_id": 456,                           # 承認ボタンを押せる Discord ユーザー
      "status": "pending" | "sent" | "missed" | "cancelled" | "failed",
      "created_at": "...",
      "<status>_at": "..."                          # 各遷移時刻
    }
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import uuid
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("LINEWORKS_X_OPS_ROOT", "/opt/lineworks-x-ops"))
SCHEDULE_FILE = PROJECT_ROOT / "scheduled-posts.json"
JST = _dt.timezone(_dt.timedelta(hours=9), name="JST")
MAX_STALE_HOURS = 24


def _now() -> _dt.datetime:
    return _dt.datetime.now(JST)


def load_schedules() -> list[dict]:
    if not SCHEDULE_FILE.exists():
        return []
    try:
        data = json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return list(data.get("schedules", []))


def save_schedules(schedules: list[dict]) -> None:
    SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schedules": schedules,
        "updated_at": _now().isoformat(),
    }
    tmp = SCHEDULE_FILE.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(SCHEDULE_FILE)


def add_schedule(
    *,
    episode_id: str,
    preview_at: _dt.datetime,
    channel_id: int,
    approver_id: int,
) -> dict:
    if preview_at.tzinfo is None:
        preview_at = preview_at.replace(tzinfo=JST)
    entry = {
        "id": f"sched-{uuid.uuid4().hex[:8]}",
        "episode_id": episode_id,
        "preview_at": preview_at.isoformat(),
        "channel_id": int(channel_id),
        "approver_id": int(approver_id),
        "status": "pending",
        "created_at": _now().isoformat(),
    }
    schedules = load_schedules()
    schedules.append(entry)
    save_schedules(schedules)
    return entry


def cancel_schedule(sched_id: str) -> dict | None:
    schedules = load_schedules()
    for s in schedules:
        if s["id"] == sched_id and s["status"] == "pending":
            s["status"] = "cancelled"
            s["cancelled_at"] = _now().isoformat()
            save_schedules(schedules)
            return s
    return None


def mark_status(sched_id: str, new_status: str) -> dict | None:
    schedules = load_schedules()
    for s in schedules:
        if s["id"] == sched_id:
            s["status"] = new_status
            s[f"{new_status}_at"] = _now().isoformat()
            save_schedules(schedules)
            return s
    return None


def pending_schedules() -> list[dict]:
    return [s for s in load_schedules() if s.get("status") == "pending"]


def due_schedules() -> list[dict]:
    """preview_at <= now の pending エントリ。古すぎる (>24h) ものは除外。"""
    now = _now()
    stale_cutoff = now - _dt.timedelta(hours=MAX_STALE_HOURS)
    result = []
    for s in pending_schedules():
        try:
            preview_at = _dt.datetime.fromisoformat(s["preview_at"])
        except (KeyError, ValueError):
            continue
        if preview_at > now:
            continue
        if preview_at < stale_cutoff:
            continue
        result.append(s)
    return result


def stale_schedules() -> list[dict]:
    """preview_at が 24時間以上前の pending エントリ（自動 missed 化対象）。"""
    now = _now()
    stale_cutoff = now - _dt.timedelta(hours=MAX_STALE_HOURS)
    result = []
    for s in pending_schedules():
        try:
            preview_at = _dt.datetime.fromisoformat(s["preview_at"])
        except (KeyError, ValueError):
            continue
        if preview_at < stale_cutoff:
            result.append(s)
    return result


def parse_jst_datetime(date_str: str, time_str: str) -> _dt.datetime:
    """`2026-05-20` + `06:55` (or `06:55:00`) を JST datetime に。"""
    if len(time_str) == 5:
        time_str = time_str + ":00"
    iso = f"{date_str}T{time_str}"
    return _dt.datetime.fromisoformat(iso).replace(tzinfo=JST)
