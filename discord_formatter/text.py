from .payload import DiscordPayload


def format_text(s: str) -> DiscordPayload:
    return DiscordPayload(content=s.strip())


def format_code(code: str, language: str = "") -> DiscordPayload:
    return DiscordPayload(content=f"```{language}\n{code.strip()}\n```")
