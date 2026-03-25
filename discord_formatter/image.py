import os
import uuid
import tempfile
from pathlib import Path

from .payload import DiscordPayload


def _tmp_path(suffix: str = ".png") -> str:
    tmp = Path(tempfile.gettempdir())
    return str(tmp / f"discord_fmt_{uuid.uuid4().hex}{suffix}")


def format_image(source) -> DiscordPayload:
    """Accept a file path (str/Path) or a PIL Image and return a DiscordPayload with file_path set."""
    try:
        from PIL import Image as PILImage
        if isinstance(source, PILImage.Image):
            path = _tmp_path(".png")
            source.save(path)
            return DiscordPayload(file_path=path)
    except ImportError:
        pass

    path = str(source)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    return DiscordPayload(file_path=path)
