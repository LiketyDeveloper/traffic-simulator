from pathlib import Path


SRC_PATH = Path(__file__).parent
BASE_PATH = SRC_PATH.parent
MEDIA_PATH = BASE_PATH / "media"


def get_media_path(media_name: str) -> str:
    return str(MEDIA_PATH / media_name)

def find_instance[T](of: type[T], in_: list) -> T | None:
    return next((obj for obj in in_ if isinstance(obj, of)), None)
