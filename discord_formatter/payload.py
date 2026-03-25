from dataclasses import dataclass, field


@dataclass
class DiscordPayload:
    content: str = ""
    file_path: str | None = None

    def has_content(self) -> bool:
        return bool(self.content)

    def has_file(self) -> bool:
        return self.file_path is not None
