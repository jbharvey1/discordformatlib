import textwrap
from .payload import DiscordPayload
from .table import _tmp_path, _hex_to_rgb, HEADER_BG

BG  = "#ffffff"
FG  = "#000000"

def _load_fonts(size: int = 14):
    from PIL import ImageFont
    import platform
    candidates = []
    if platform.system() == "Windows":
        candidates = [
            ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"),
            ("C:/Windows/Fonts/arial.ttf",   "C:/Windows/Fonts/arialbd.ttf"),
        ]
    else:
        candidates = [
            ("/System/Library/Fonts/SFNS.ttf",         "/System/Library/Fonts/SFNSBold.ttf"),
            ("/System/Library/Fonts/Helvetica.ttc",    "/System/Library/Fonts/Helvetica.ttc"),
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]
    for reg, bold in candidates:
        try:
            return ImageFont.truetype(reg, size), ImageFont.truetype(bold, size)
        except (IOError, OSError):
            continue
    default = ImageFont.load_default()
    return default, default

DISCORD_LIMIT = 2000

# Image rendering config
IMG_WIDTH   = 800   # logical pixels (rendered at 2x)
LINE_PAD    = 6     # extra px between lines
MARGIN      = 20
SCALE       = 10
FONT_SIZE   = 13
WRAP_WIDTH  = 95    # chars per line


def _render_text_image(text: str, title: str = "") -> str:
    from PIL import Image, ImageDraw

    font, font_bold = _load_fonts(FONT_SIZE * SCALE)
    font_title, _  = _load_fonts(16 * SCALE)

    margin  = MARGIN * SCALE
    lpad    = LINE_PAD * SCALE
    line_h  = font.size + lpad
    w       = IMG_WIDTH * SCALE

    lines = []
    if title:
        lines.append(("title", title))
        lines.append(("spacer", ""))

    for raw_line in text.splitlines():
        if raw_line.strip() == "":
            lines.append(("spacer", ""))
        else:
            for wrapped in textwrap.wrap(raw_line, width=WRAP_WIDTH) or [""]:
                lines.append(("text", wrapped))

    title_h  = (font_title.size + lpad + margin) if title else 0
    total_h  = margin + title_h + len(lines) * line_h + margin

    img = Image.new("RGB", (w, total_h), _hex_to_rgb(BG))
    d   = ImageDraw.Draw(img)
    d.fontmode = "1"  # disable AA — supersampling + LANCZOS handles smoothing

    y = margin
    if title:
        d.text((margin, y), title, font=font_title, fill=_hex_to_rgb(HEADER_BG))
        y += font_title.size + lpad + margin // 2
        d.line([margin, y, w - margin, y], fill=_hex_to_rgb(ACCENT), width=SCALE)
        y += margin // 2

    for kind, line in lines:
        if kind == "spacer":
            y += line_h // 2
        else:
            d.text((margin, y), line, font=font, fill=_hex_to_rgb(FG))
            y += line_h

    # Downsample 2x → 1x
    img = img.resize((IMG_WIDTH, total_h // SCALE), Image.LANCZOS)

    path = _tmp_path()
    img.save(path)
    return path


def format_long_text(text: str, title: str = "") -> DiscordPayload:
    """If text fits in Discord's 2000-char limit, return it as content.
    If it's too long, render it as a crisp image and return file_path.
    """
    if len(text) <= DISCORD_LIMIT:
        return DiscordPayload(content=text)
    path = _render_text_image(text, title=title)
    return DiscordPayload(file_path=path)
