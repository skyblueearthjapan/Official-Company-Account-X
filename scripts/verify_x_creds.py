#!/usr/bin/env python3
"""verify_x_creds.py — X API 認証情報のチェック（投稿はしない）

OAuth1 (User Context) で認証して `users/me` を呼ぶだけ。
権限が Read-only に留まっているなど、設定ミスを早期発見する用途。

Usage:
    .venv/bin/python scripts/verify_x_creds.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("LINEWORKS_X_OPS_ROOT", "/opt/lineworks-x-ops"))


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    keys = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    creds = {k: os.environ.get(k, "").strip() for k in keys}
    missing = [k for k, v in creds.items() if not v]
    if missing:
        print(f"NG: missing {', '.join(missing)} in .env", file=sys.stderr)
        return 2

    import tweepy

    try:
        client = tweepy.Client(
            consumer_key=creds["X_API_KEY"],
            consumer_secret=creds["X_API_SECRET"],
            access_token=creds["X_ACCESS_TOKEN"],
            access_token_secret=creds["X_ACCESS_TOKEN_SECRET"],
        )
        me = client.get_me(user_fields=["username", "name", "id"])
    except tweepy.Unauthorized as e:
        print(f"NG: 401 Unauthorized — keys are wrong or expired: {e}", file=sys.stderr)
        return 3
    except tweepy.Forbidden as e:
        print(f"NG: 403 Forbidden — permission level too low: {e}", file=sys.stderr)
        return 4
    except Exception as e:
        print(f"NG: API error: {type(e).__name__}: {e}", file=sys.stderr)
        return 5

    if not me.data:
        print(f"NG: empty response: {me}", file=sys.stderr)
        return 6

    user = me.data
    print(f"OK authenticated as @{user.username}  ({user.name}, id={user.id})")
    print()
    print("App permission check (write):")
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key=creds["X_API_KEY"],
            consumer_secret=creds["X_API_SECRET"],
            access_token=creds["X_ACCESS_TOKEN"],
            access_token_secret=creds["X_ACCESS_TOKEN_SECRET"],
        )
        api_v1 = tweepy.API(auth)
        cred_data = api_v1.verify_credentials(skip_status=True, include_email=False)
        print(f"  v1.1 verify_credentials OK — screen_name=@{cred_data.screen_name}")
    except Exception as e:
        print(
            f"  ⚠️  v1.1 verify_credentials failed (may be Free-tier restriction): {e}"
        )
        print(
            "  → 投稿時の v1.1 media_upload も同様に失敗する可能性あり。"
            "    Developer Portal で App permissions を Read+Write にし、Access Token を再発行してください。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
