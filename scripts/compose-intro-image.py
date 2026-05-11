"""compose-intro-image.py — ご挨拶ツイート用の 4 写真コラージュを生成。

新工場/新事務所の写真 4 枚を 2x2 グリッドで配置し、上部に既存 4 コマ漫画
シリーズと統一感のあるバナーを乗せて 1 枚の PNG として保存する。
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHOTO_DIR = Path(
    r"C:\Users\imaizumi.LINEWORKS-NET\Desktop\東北工業高校訪問\工業高校就職訪問\新工場\iCloud写真"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "episodes"
    / "_intro-2026-05-11-アカウント開設のごあいさつ"
    / "final"
)
OUTPUT_PATH = OUTPUT_DIR / "final.png"

# 左上 → 右上 → 左下 → 右下 の順
PHOTOS = [
    ("IMG_2439.JPEG", "会社サイン"),
    ("IMG_2429.JPEG", "新事務所"),
    ("IMG_2309.JPEG", "新工場"),
    ("IMG_2432.JPEG", "Smart Factory"),
]

CANVAS_W = 1600
CANVAS_H = 1900
BANNER_H = 140
GAP = 20
PADDING = 20

BANNER_BG = (245, 245, 248)
BANNER_FG = (28, 32, 56)


def find_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\meiryob.ttc",  # メイリオ Bold
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc",  # 游ゴシック Bold
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
    ]
    for fp in candidates:
        if Path(fp).is_file():
            try:
                return ImageFont.truetype(fp, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit_into(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """中央クロップして target_w x target_h に合わせる。"""
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    tgt_ratio = target_w / target_h
    if src_ratio > tgt_ratio:
        # 横長すぎる → 左右を削る
        new_w = int(src_h * tgt_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / tgt_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # バナー
    draw.rectangle([(0, 0), (CANVAS_W, BANNER_H)], fill=BANNER_BG)

    banner_top_text = "(株)ラインワークス★ 公式アカウント X"
    banner_bottom_text = "アカウント開設のごあいさつ"

    f_top = find_font(36)
    f_bottom = find_font(48)

    top_bbox = draw.textbbox((0, 0), banner_top_text, font=f_top)
    bottom_bbox = draw.textbbox((0, 0), banner_bottom_text, font=f_bottom)
    top_w = top_bbox[2] - top_bbox[0]
    bottom_w = bottom_bbox[2] - bottom_bbox[0]

    draw.text(
        ((CANVAS_W - top_w) / 2, 18),
        banner_top_text,
        fill=BANNER_FG,
        font=f_top,
    )
    draw.text(
        ((CANVAS_W - bottom_w) / 2, 72),
        banner_bottom_text,
        fill=BANNER_FG,
        font=f_bottom,
    )

    # 写真 2x2
    grid_top = BANNER_H + PADDING
    grid_w = CANVAS_W - PADDING * 2
    grid_h = CANVAS_H - grid_top - PADDING
    cell_w = (grid_w - GAP) // 2
    cell_h = (grid_h - GAP) // 2

    positions = [
        (PADDING, grid_top),
        (PADDING + cell_w + GAP, grid_top),
        (PADDING, grid_top + cell_h + GAP),
        (PADDING + cell_w + GAP, grid_top + cell_h + GAP),
    ]

    for (filename, _label), (x, y) in zip(PHOTOS, positions):
        src_path = PHOTO_DIR / filename
        if not src_path.is_file():
            raise FileNotFoundError(f"Source photo missing: {src_path}")
        img = Image.open(src_path)
        img = fit_into(img, cell_w, cell_h)
        canvas.paste(img, (x, y))

    canvas.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"OK wrote {OUTPUT_PATH} ({canvas.size})")


if __name__ == "__main__":
    main()
