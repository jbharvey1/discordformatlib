import re
from .payload import DiscordPayload
from .table import format_table


# Matches a full markdown table block (header + separator + rows)
_TABLE_RE = re.compile(
    r"(\|.+\|\n\|[-| :]+\|\n(?:\|.+\|\n?)+)",
    re.MULTILINE,
)


def _convert_markdown(md: str) -> str:
    """Convert markdown to Discord-compatible markdown (text only, no tables)."""
    lines = md.splitlines()
    out = []
    for line in lines:
        # Headings → bold
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            line = f"**{m.group(2).strip()}**"
        out.append(line)
    return "\n".join(out)


def format_markdown(md: str) -> list[DiscordPayload]:
    """Convert markdown into one or more DiscordPayloads.

    Tables are extracted and rendered as images; the rest becomes
    Discord-safe text. Returns a list so callers can send each part
    in sequence (text first, then image attachments).
    """
    payloads: list[DiscordPayload] = []
    parts = _TABLE_RE.split(md)

    for part in parts:
        if not part.strip():
            continue
        if _TABLE_RE.match(part.strip()):
            payloads.append(format_table(part.strip()))
        else:
            converted = _convert_markdown(part).strip()
            if converted:
                payloads.append(DiscordPayload(content=converted))

    return payloads or [DiscordPayload(content=_convert_markdown(md).strip())]
