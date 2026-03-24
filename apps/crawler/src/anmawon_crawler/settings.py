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
    anmawon_base_url: str = "https://www.anmawon.com"
    anmawon_user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    )


def load_settings() -> Settings:
    load_dotenv(APP_ROOT / ".env")

    return Settings(
        request_delay=float(os.getenv("ANMAWON_REQUEST_DELAY", "1.2")),
        timeout=float(os.getenv("ANMAWON_TIMEOUT", "20")),
        kakao_rest_api_key=os.getenv("KAKAO_REST_API_KEY", ""),
        anmawon_base_url=os.getenv("ANMAWON_BASE_URL", "https://www.anmawon.com"),
        anmawon_user_agent=os.getenv(
            "ANMAWON_USER_AGENT",
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
            ),
        ),
    )
