"""Generate the SudokuSolver logo: a stylized 3x3 sudoku grid with digits.

Style: dark cosmic background, warm gold accents, clean typography.
Produces logo.png (512), logo_64.png (64), logo.ico (multi-size).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024  # render at 2x then downscale for anti-aliasing
FINAL = 512

BG_OUTER = (16, 22, 40)
BG_INNER = (28, 42, 78)
GRID_DARK = (240, 220, 160)
GRID_LIGHT = (255, 245, 210)
DIGIT_MAIN = (255, 240, 190)
DIGIT_FADED = (180, 200, 230, 120)
ACCENT = (255, 196, 80)


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    # Try a few common fonts; fall back to default
    for name in (
        "segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_digit(draw: ImageDraw.ImageDraw, cx: int, cy: int, digit: str, size: int, color) -> None:
    font = _get_font(size)
    try:
        bbox = draw.textbbox((0, 0), digit, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), digit, font=font, fill=color)
    except Exception:
        draw.text((cx, cy), digit, font=font, fill=color)


def _radial_bg(size: int) -> Image.Image:
    """Fast radial gradient using a 1-D mask blurred with Pillow.

    Replaces the pure-Python per-pixel loop (≈1M iterations) with a
    constant-time composite based on a linear alpha mask + solid fills.
    """
    # Inner color solid
    inner = Image.new("RGB", (size, size), BG_INNER)
    outer = Image.new("RGB", (size, size), BG_OUTER)

    # Build a radial alpha mask: bright in the center, dark at the edges.
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    steps = 32
    max_d = int(size * 0.6)
    for i in range(steps, 0, -1):
        alpha = int(255 * (i / steps))
        r = int(max_d * (1 - (i - 1) / steps))
        draw.ellipse(
            (size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r),
            fill=alpha,
        )
    # The mask controls how much `inner` shows through over `outer`.
    return Image.composite(inner, outer, mask)


def make_logo(output_dir: Path) -> None:
    img = _radial_bg(SIZE).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Outer rounded square frame (darker)
    pad = 90
    draw.rounded_rectangle(
        (pad - 10, pad - 10, SIZE - pad + 10, SIZE - pad + 10),
        radius=60,
        outline=ACCENT,
        width=6,
    )

    grid_w = SIZE - 2 * pad
    cell = grid_w / 9
    # Cell thin lines
    for i in range(10):
        x = pad + i * cell
        y = pad + i * cell
        width = 10 if i % 3 == 0 else 3
        color = GRID_DARK if i % 3 == 0 else (*GRID_LIGHT, 200)
        draw.line([(x, pad), (x, SIZE - pad)], fill=color, width=width)
        draw.line([(pad, y), (SIZE - pad, y)], fill=color, width=width)

    # A pleasant 3x3 pattern of "solved" main digits + a few ghosted
    pattern = [
        ["5", "", "", "", "3", "", "", "", "7"],
        ["", "", "", "6", "", "", "", "", ""],
        ["", "9", "8", "", "", "", "", "6", ""],
        ["", "", "", "", "6", "", "", "", "3"],
        ["4", "", "", "8", "", "3", "", "", "1"],
        ["7", "", "", "", "2", "", "", "", ""],
        ["", "6", "", "", "", "", "2", "8", ""],
        ["", "", "", "4", "", "9", "", "", "5"],
        ["3", "", "", "", "8", "", "", "", "9"],
    ]

    digit_font_size = int(cell * 0.6)
    for r in range(9):
        for c in range(9):
            v = pattern[r][c]
            if not v:
                continue
            cx = int(pad + (c + 0.5) * cell)
            cy = int(pad + (r + 0.5) * cell)
            _draw_digit(draw, cx, cy, v, digit_font_size, DIGIT_MAIN)

    # Corner accent: small glowing star top-right
    star_x = SIZE - pad - 40
    star_y = pad + 40
    for radius, alpha in ((60, 40), (40, 80), (20, 180)):
        glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse(
            (star_x - radius, star_y - radius, star_x + radius, star_y + radius),
            fill=(*ACCENT, alpha),
        )
        img = Image.alpha_composite(img, glow)

    # Downscale for anti-aliasing
    final = img.resize((FINAL, FINAL), Image.LANCZOS)

    final.convert("RGB").save(output_dir / "logo.png")
    final.resize((64, 64), Image.LANCZOS).convert("RGB").save(output_dir / "logo_64.png")

    # Multi-size .ico
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    final.save(output_dir / "logo.ico", sizes=sizes)

    print(f"Logo written to {output_dir}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent
    make_logo(out)
