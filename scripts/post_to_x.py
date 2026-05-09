#!/usr/bin/env python3
"""
post_to_x.py — 株式会社ラインワークス公式 X アカウントへ 4コマ漫画を投稿

使い方:
  CLI:
    python scripts/post_to_x.py <episode_id>
    python scripts/post_to_x.py <episode_id> --dry-run

  ライブラリ:
    from scripts.post_to_x import post_episode
    result = post_episode("001-2026-05-11-新拠点完成PR1")
    # -> {"tweet_id": "...", "url": "...", "posted_at": "..."}

エピソード規約:
  episodes/<id>/final/final.png       … 投稿画像（必須）
  episodes/<id>/final/post-body.txt   … 投稿本文（UTF-8、≤280字、必須）

ログ:
  analytics/<YYYY-MM>/post-log.md に追記
"""
from __future__ import annotations

import argparse
import datetime as _dt
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# tweepy is imported lazily inside post_episode() so --dry-run / --help
# work in environments where the package is not yet installed.

PROJECT_ROOT = Path(os.environ.get("LINEWORKS_X_OPS_ROOT", "/opt/lineworks-x-ops"))
EPISODES_DIR = PROJECT_ROOT / "episodes"
ANALYTICS_DIR = PROJECT_ROOT / "analytics"

X_TWEET_LIMIT = 280

log = logging.getLogger("post_to_x")


@dataclass
class EpisodePost:
    episode_id: str
    image_path: Path
    body_text: str

    @classmethod
    def load(cls, episode_id: str) -> "EpisodePost":
        ep_dir = EPISODES_DIR / episode_id
        if not ep_dir.is_dir():
            raise FileNotFoundError(f"Episode directory not found: {ep_dir}")

        image = ep_dir / "final" / "final.png"
        if not image.is_file():
            raise FileNotFoundError(
                f"final.png not found: {image} — run finalize step first"
            )

        body_file = ep_dir / "final" / "post-body.txt"
        if not body_file.is_file():
            raise FileNotFoundError(
                f"post-body.txt not found: {body_file} — create it with the X post text"
            )

        text = body_file.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"post-body.txt is empty: {body_file}")
        if len(text) > X_TWEET_LIMIT:
            raise ValueError(
                f"post-body.txt is {len(text)} chars, exceeds X limit of {X_TWEET_LIMIT}"
            )

        return cls(episode_id=episode_id, image_path=image, body_text=text)


@dataclass
class PostResult:
    tweet_id: str
    url: str
    posted_at: _dt.datetime
    body_text: str
    image_path: Path

    def to_dict(self) -> dict:
        return {
            "tweet_id": self.tweet_id,
            "url": self.url,
            "posted_at": self.posted_at.isoformat(),
            "body_text": self.body_text,
            "image_path": str(self.image_path),
        }


def _read_credentials() -> dict:
    keys = [
        "X_API_KEY",
        "X_API_SECRET",
        "X_ACCESS_TOKEN",
        "X_ACCESS_TOKEN_SECRET",
    ]
    creds = {k: os.environ.get(k, "").strip() for k in keys}
    missing = [k for k, v in creds.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing X API credentials in env: {', '.join(missing)}. "
            "See .env.example and docs/X_API_SETUP.md"
        )
    return creds


def _build_url(tweet_id: str) -> str:
    handle = os.environ.get("X_SCREEN_NAME", "").strip().lstrip("@")
    if handle:
        return f"https://x.com/{handle}/status/{tweet_id}"
    return f"https://x.com/i/status/{tweet_id}"


def _append_analytics(
    result: PostResult,
    episode_id: str,
    approved_by: str | None,
) -> Path:
    posted = result.posted_at
    month_dir = ANALYTICS_DIR / posted.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)
    log_file = month_dir / "post-log.md"
    if not log_file.exists():
        log_file.write_text(
            f"# X 投稿ログ — {posted.strftime('%Y-%m')}\n\n", encoding="utf-8"
        )
    entry = (
        f"## {posted.strftime('%Y-%m-%d %H:%M:%S %Z').strip()} — `{episode_id}`\n"
        f"- tweet_id: `{result.tweet_id}`\n"
        f"- url: {result.url}\n"
        f"- image: `{result.image_path.relative_to(PROJECT_ROOT)}`\n"
        f"- approved_by: `{approved_by or 'cli'}`\n"
        f"- body:\n"
        f"  ```\n"
        f"  {result.body_text}\n"
        f"  ```\n\n"
    )
    with log_file.open("a", encoding="utf-8") as f:
        f.write(entry)
    return log_file


def post_episode(
    episode_id: str,
    *,
    dry_run: bool = False,
    approved_by: str | None = None,
) -> PostResult:
    """指定エピソードの final.png + post-body.txt を X に投稿する。

    Raises:
        FileNotFoundError / ValueError: episode 構成が不正
        RuntimeError: 認証情報が未設定
        tweepy.TweepyException: API エラー
    """
    episode = EpisodePost.load(episode_id)
    log.info(
        "Loaded episode %s: image=%s, %d chars",
        episode_id,
        episode.image_path,
        len(episode.body_text),
    )

    if dry_run:
        log.info("[dry-run] would post: %r", episode.body_text)
        return PostResult(
            tweet_id="DRYRUN",
            url="(dry-run, no URL)",
            posted_at=_dt.datetime.now().astimezone(),
            body_text=episode.body_text,
            image_path=episode.image_path,
        )

    creds = _read_credentials()
    import tweepy  # type: ignore[import-not-found]

    auth = tweepy.OAuth1UserHandler(
        consumer_key=creds["X_API_KEY"],
        consumer_secret=creds["X_API_SECRET"],
        access_token=creds["X_ACCESS_TOKEN"],
        access_token_secret=creds["X_ACCESS_TOKEN_SECRET"],
    )
    api_v1 = tweepy.API(auth)

    log.info("Uploading media via v1.1 …")
    media = api_v1.media_upload(filename=str(episode.image_path))
    log.info("media_id=%s", media.media_id)

    client_v2 = tweepy.Client(
        consumer_key=creds["X_API_KEY"],
        consumer_secret=creds["X_API_SECRET"],
        access_token=creds["X_ACCESS_TOKEN"],
        access_token_secret=creds["X_ACCESS_TOKEN_SECRET"],
    )
    log.info("Creating tweet via v2 …")
    response = client_v2.create_tweet(
        text=episode.body_text,
        media_ids=[media.media_id],
    )
    tweet_id = str(response.data["id"])
    posted_at = _dt.datetime.now().astimezone()
    log.info("Posted: tweet_id=%s", tweet_id)

    result = PostResult(
        tweet_id=tweet_id,
        url=_build_url(tweet_id),
        posted_at=posted_at,
        body_text=episode.body_text,
        image_path=episode.image_path,
    )
    log_file = _append_analytics(result, episode_id, approved_by)
    log.info("Analytics appended: %s", log_file)
    return result


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Post a finalized episode to X")
    parser.add_argument("episode_id", help="e.g. 001-2026-05-11-新拠点完成PR1")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="読み込み・検証のみ。X API は呼ばない",
    )
    parser.add_argument(
        "--approved-by",
        default=None,
        help="承認者の識別子（discord user id など）",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    try:
        result = post_episode(
            args.episode_id,
            dry_run=args.dry_run,
            approved_by=args.approved_by,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # tweepy errors etc.
        print(f"ERROR: X API call failed: {e}", file=sys.stderr)
        return 3

    print(f"OK tweet_id={result.tweet_id}")
    print(f"   url={result.url}")
    print(f"   posted_at={result.posted_at.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
