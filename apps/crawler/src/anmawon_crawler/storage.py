from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List
from zoneinfo import ZoneInfo

from .models import ShopRecord


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = REPO_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "shops.raw.json"
CLEAN_DATA_PATH = DATA_DIR / "processed" / "shops.cleaned.json"
GEOCODED_DATA_PATH = DATA_DIR / "processed" / "shops.geocoded.json"
FINAL_DATA_PATH = DATA_DIR / "processed" / "shops.geo.json"
GEOCODE_CACHE_PATH = DATA_DIR / "cache" / "geocode-cache.json"
GEOCODE_FAILURE_PATH = DATA_DIR / "logs" / "geocode-failures.json"
SEOUL_TZ = ZoneInfo("Asia/Seoul")


def now_iso() -> str:
    return datetime.now(SEOUL_TZ).isoformat(timespec="seconds")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_dataset(path: Path, shops: Iterable[ShopRecord]) -> None:
    ensure_parent(path)
    serialized = [shop.to_dict() for shop in shops]

    path.write_text(
        json.dumps(
            {
                "generatedAt": now_iso(),
                "count": len(serialized),
                "shops": serialized,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def read_dataset(path: Path) -> List[ShopRecord]:
    if not path.exists():
        return []

    payload = json.loads(path.read_text(encoding="utf-8"))
    return [ShopRecord.from_dict(item) for item in payload.get("shops", [])]


def read_json(path: Path, default):
    if not path.exists():
        return default

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    ensure_parent(path)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
