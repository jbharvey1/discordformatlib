# discordformatlib

Transport-agnostic Discord message formatter. Converts text, markdown, tables, and images into `DiscordPayload` objects ready to send via any Discord bot or API client.

## Install

```bash
pip install discordformatlib
```

Or from source:

```bash
pip install .
```

**Dependencies:** `Pillow`, `matplotlib`, `markdown`

Optional — for `markdown_image`:
```bash
pip install "discordformatlib[image]"
playwright install chromium
```

---

## Usage

```python
from discord_formatter import DiscordFormatter, DiscordPayload
```

### Plain text

```python
p = DiscordFormatter.text("Hello, world!")
# p.content = "Hello, world!"
```

### Code block

```python
p = DiscordFormatter.code("print('hi')", language="python")
# p.content = "```python\nprint('hi')\n```"
```

### Table → image

Accepts a markdown table string, list of lists, or list of dicts. First row = header.

```python
# List of lists
p = DiscordFormatter.table(
    [["Name", "Role"], ["Alice", "Admin"], ["Bob", "Member"]],
    title="Server Members"
)
# p.file_path = "/tmp/discord_fmt_<uuid>.png"

# Markdown table string
p = DiscordFormatter.table("| A | B |\n|---|---|\n| 1 | 2 |")

# List of dicts
p = DiscordFormatter.table([{"Lang": "Python", "Speed": "Fast"}])
```

### Markdown → Discord-safe

Converts headings to bold, extracts tables as images. Returns a list of payloads (text + image parts).

```python
parts = DiscordFormatter.markdown("# Heading\n**bold** text\n\n| A | B |\n|---|---|\n| 1 | 2 |")
for p in parts:
    if p.has_content():
        send_text(p.content)
    if p.has_file():
        send_file(p.file_path)
```

### Long text → auto image

Stays as text if ≤ 2000 chars (Discord's limit), otherwise renders as a PNG.

```python
p = DiscordFormatter.long_text(very_long_string, title="My Report")
```

### Markdown as styled image

Renders the full markdown document as a crisp PNG using a headless Chromium screenshot.
Supports headings, code blocks with dark theme, tables, blockquotes, bold/italic, and Unicode.
Requires `playwright` (`pip install "discordformatlib[image]"` + `playwright install chromium`).

```python
p = DiscordFormatter.markdown_image(md_text, title="My Report")
# p.file_path = "/tmp/discord_fmt_<uuid>.png"
```

### Image passthrough

```python
p = DiscordFormatter.image("/path/to/photo.png")
# p.file_path = "/path/to/photo.png"

# PIL Image also accepted
from PIL import Image
img = Image.open("photo.png")
p = DiscordFormatter.image(img)
```

---

## DiscordPayload

```python
@dataclass
class DiscordPayload:
    content: str = ""        # text to send
    file_path: str | None = None  # path to file attachment

    def has_content(self) -> bool: ...
    def has_file(self) -> bool: ...
```

---

## Table Style

- White background, dark navy header (`#1a1a2e`), alternating row shading
- Black bold text in header (white) and label column
- Auto-sized columns, tight autocropped border
- Rendered via matplotlib at 300 DPI
- Title stamped via Pillow for pixel-tight spacing above the table

---

## Changelog

### 0.2.0
- Added `markdown_image()` — full markdown rendered as styled PNG via Playwright + Noto Sans
- Unicode arrows/symbols (`→`, `≥`, `✓`, etc.) pre-converted to HTML entities for headless Chromium compatibility
- Table title now rendered via Pillow (eliminates matplotlib layout gap)
- Added `markdown` core dependency; `playwright` as optional `[image]` extra

### 0.1.0
- Initial release: `text`, `code`, `table`, `image`, `markdown`, `long_text`

---

## License

MIT
