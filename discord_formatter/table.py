import uuid
import tempfile
import re
from pathlib import Path
from typing import Union

from .payload import DiscordPayload

# ── theme ──────────────────────────────────────────────────────────────────────
HEADER_BG = "#1a1a2e"
BG_ALT    = "#d0d0d0"
BG        = "#e8e8e8"
BORDER    = "#000000"

DPI        = 300
ROW_HEIGHT = 0.18
FONT_SIZE  = 9


def _tmp_path() -> str:
    tmp = Path(tempfile.gettempdir())
    return str(tmp / f"discord_fmt_{uuid.uuid4().hex}.png")


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _parse_markdown_table(md: str) -> list[list[str]]:
    rows = []
    for line in md.strip().splitlines():
        line = line.strip()
        if not line or re.match(r"^\|?[-:| ]+\|?$", line):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line) if c.strip() != ""]
        if cells:
            rows.append(cells)
    return rows


def _normalize_rows(data) -> list[list[str]]:
    if isinstance(data, str):
        return _parse_markdown_table(data)
    if not data:
        return []
    if isinstance(data[0], dict):
        headers = list(data[0].keys())
        return [headers] + [[str(row.get(h, "")) for h in headers] for row in data]
    return [[str(cell) for cell in row] for row in data]


def _render_table_image(rows: list[list[str]], title: str = "") -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    num_cols = max(len(r) for r in rows)
    rows = [r + [""] * (num_cols - len(r)) for r in rows]

    header = rows[0]
    data   = rows[1:]

    # Let matplotlib auto-size — we pass None and call auto_set_column_width after
    col_widths = None

    col_chars = [max(len(rows[r][c]) for r in range(len(rows))) for c in range(num_cols)]
    num_rows  = len(data)
    fig_w     = max(4, sum(col_chars) * 0.11)
    fig_h     = (num_rows + 1) * ROW_HEIGHT * 1.6

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DPI)
    ax.axis("off")

    table = ax.table(
        cellText=data,
        colLabels=header,
        cellLoc="left",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(FONT_SIZE)
    table.auto_set_column_width(col=list(range(num_cols)))

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(BORDER)
        cell.set_linewidth(0.8)
        cell.set_height(ROW_HEIGHT)
        if r == 0:
            cell.set_facecolor(HEADER_BG)
            cell.get_text().set_color("#ffffff")
            cell.get_text().set_fontweight("bold")
        else:
            if c == 0:
                cell.set_facecolor("#ffffff")  # label column stays white
                cell.get_text().set_fontweight("bold")
            else:
                cell.set_facecolor(BG_ALT if r % 2 == 0 else BG)
            cell.get_text().set_color("#000000")

    plt.tight_layout(pad=0.1)
    path = _tmp_path()
    plt.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)

    # Autocrop whitespace
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    img = Image.open(path).convert("RGB")
    bg  = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        pad = 8
        bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad),
                min(img.width, bbox[2]+pad), min(img.height, bbox[3]+pad))
        img = img.crop(bbox)

    # Stamp title above table using Pillow — avoids matplotlib spacing issues
    if title:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
        except (IOError, OSError):
            font = ImageFont.load_default()
        dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tw, th = dummy.textbbox((0, 0), title, font=font)[2:]
        pad_x, pad_top, pad_bot = 8, 8, 6
        title_h = th + pad_top + pad_bot
        canvas = Image.new("RGB", (img.width, img.height + title_h), (255, 255, 255))
        d = ImageDraw.Draw(canvas)
        d.text(((img.width - tw) // 2, pad_top), title, font=font, fill=(0, 0, 0))
        canvas.paste(img, (0, title_h))
        img = canvas

    img.save(path)
    return path


def format_table(data: Union[str, list], title: str = "") -> DiscordPayload:
    """Render a table as a PNG image.

    data can be:
      - a markdown table string
      - list of lists  (first row treated as header)
      - list of dicts  (keys become header)
    """
    rows = _normalize_rows(data)
    if not rows:
        return DiscordPayload(content="*(empty table)*")
    path = _render_table_image(rows, title=title)
    return DiscordPayload(file_path=path)
