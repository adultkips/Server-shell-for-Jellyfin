from pathlib import Path
import os
def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)
JELLYFIN_URL = _env("JELLYFIN_URL", "http://localhost:8096")
USERNAME = _env("JELLYFIN_USERNAME", "")
PASSWORD = _env("JELLYFIN_PASSWORD", "")
SERVER_ID = _env("JELLYFIN_SERVER_ID", "")
try:
    from . import config_local as _local
except Exception:
    _local = None
if _local:
    for _k in ("JELLYFIN_URL", "USERNAME", "PASSWORD", "SERVER_ID"):
        if hasattr(_local, _k):
            globals()[_k] = getattr(_local, _k)
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR
DASHBOARD_OUT = OUT_DIR / "dashboard.html"
FILMS_OUT = OUT_DIR / "films.html"
MODELS_OUT = OUT_DIR / "models.html"
STUDIOS_OUT = OUT_DIR / "studios.html"
GENRES_OUT = OUT_DIR / "genres.html"
