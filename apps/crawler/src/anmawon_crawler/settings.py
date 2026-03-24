from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


APP_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Settings:
    request_delay: float = 1.2
    timeout: float = 20.0
    kakao_rest_api_key: str = ""


def load_settings() -> Settings:
    load_dotenv(APP_ROOT / ".env")

    return Settings(
        request_delay=float(os.getenv("ANMAWON_REQUEST_DELAY", "1.2")),
        timeout=float(os.getenv("ANMAWON_TIMEOUT", "20")),
        kakao_rest_api_key=os.getenv("KAKAO_REST_API_KEY", ""),
    )
