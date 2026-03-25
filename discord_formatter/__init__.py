from .payload import DiscordPayload
from .text import format_text, format_code
from .table import format_table
from .image import format_image
from .markdown import format_markdown
from .long_text import format_long_text
from .markdown_image import format_markdown_image


class DiscordFormatter:
    @staticmethod
    def text(s: str) -> DiscordPayload:
        """Plain text → DiscordPayload."""
        return format_text(s)

    @staticmethod
    def code(code: str, language: str = "") -> DiscordPayload:
        """Code string → fenced code block DiscordPayload."""
        return format_code(code, language)

    @staticmethod
    def table(data, title: str = "") -> DiscordPayload:
        """Table (markdown str / list of lists / list of dicts) → image DiscordPayload."""
        return format_table(data, title)

    @staticmethod
    def image(source) -> DiscordPayload:
        """File path or PIL Image → DiscordPayload with file_path set."""
        return format_image(source)

    @staticmethod
    def markdown(md: str) -> list[DiscordPayload]:
        """Markdown string → list of DiscordPayloads (text parts + table images)."""
        return format_markdown(md)

    @staticmethod
    def long_text(text: str, title: str = "") -> DiscordPayload:
        """Auto-format text: ≤2000 chars → content string, >2000 chars → rendered PNG image."""
        return format_long_text(text, title)

    @staticmethod
    def markdown_image(md: str, title: str = "") -> DiscordPayload:
        """Render markdown as a fully styled PNG image (headings, code blocks, tables, etc.)."""
        return format_markdown_image(md, title)


__all__ = ["DiscordFormatter", "DiscordPayload"]
