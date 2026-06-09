import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any

from app.core.logger import logger
from app.core.exceptions import ConfigException

def _resolve_config_path(path: str | None = None) -> Path:
    default_path = Path(__file__).resolve().parents[1] / "config.json"
    return Path(path).resolve() if path else default_path


def load_config(path: str | None = None) -> Dict[str, Any]:
    p = _resolve_config_path(path)
    logger.info(f"the path is {p}")
    if not p.exists():
        raise ConfigException(
            message=f"Config file not found: {p}",
            context={"module": "core.config", "function": "load_config", "path": str(p)}
        )

    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigException(
            message=f"Invalid JSON format in {p}: {e}",
            context={"module": "core.config", "function": "load_config", "path": str(p)}
        )
    except OSError as e:
        raise ConfigException(
            message=f"Unable to read config file {p}: {e}",
            context={"module": "core.config", "function": "load_config", "path": str(p)}
        )


def save_config(data: Dict[str, Any], path: str | None = None) -> None:
    """
    Atomic write: write temp file then replace original.
    """
    p = _resolve_config_path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)

        with NamedTemporaryFile("w", delete=False, dir=str(p.parent), encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name

        os.replace(tmp_name, p)  # atomic replace
        logger.info(f"Config saved successfully: {p}")

    except OSError as e:
        raise ConfigException(
            message=f"Unable to write config file {p}: {e}",
            context={"module": "core.config", "function": "save_config", "path": str(p)}
        )


def backup_config(path: str | None = None) -> Path:
    """
    Optional helper before destructive operations (delete/update).
    """
    p = _resolve_config_path(path)
    backup = p.with_suffix(".backup.json")
    try:
        backup.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        logger.info(f"Config backup created: {backup}")
        return backup
    except OSError as e:
        raise ConfigException(
            message=f"Unable to backup config file {p}: {e}",
            context={"module": "core.config", "function": "backup_config", "path": str(p)}
        )