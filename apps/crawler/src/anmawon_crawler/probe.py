from __future__ import annotations

import json
import socket
from dataclasses import asdict, dataclass
from typing import List
from urllib.parse import urljoin, urlparse

import httpx


LIST_PATH = "/FindShop/List"


@dataclass
class ProbeResult:
    name: str
    target: str
    ok: bool
    detail: str
    status_code: int | None = None
    final_url: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def build_probe_targets(base_url: str) -> List[tuple[str, str]]:
    normalized = normalize_base_url(base_url)
    parsed = urlparse(normalized)

    targets = [("configured-list", urljoin(normalized, LIST_PATH))]

    if parsed.scheme == "https":
        http_base = parsed._replace(scheme="http").geturl().rstrip("/")
        targets.append(("http-fallback-list", urljoin(http_base, LIST_PATH)))

    return targets


def probe_dns(hostname: str) -> ProbeResult:
    try:
        addresses = sorted(
            {
                result[4][0]
                for result in socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
            }
        )
    except OSError as error:
        return ProbeResult(
            name="dns",
            target=hostname,
            ok=False,
            detail=f"{type(error).__name__}: {error}",
        )

    return ProbeResult(
        name="dns",
        target=hostname,
        ok=bool(addresses),
        detail=", ".join(addresses) if addresses else "no addresses returned",
    )


def probe_url(client: httpx.Client, name: str, url: str) -> ProbeResult:
    try:
        response = client.get(url)
    except httpx.HTTPError as error:
        return ProbeResult(
            name=name,
            target=url,
            ok=False,
            detail=f"{type(error).__name__}: {error}",
        )

    return ProbeResult(
        name=name,
        target=url,
        ok=response.is_success,
        detail=f"HTTP {response.status_code}",
        status_code=response.status_code,
        final_url=str(response.url),
    )


def run_source_probe(
    *,
    base_url: str,
    timeout: float,
    user_agent: str,
) -> List[ProbeResult]:
    normalized = normalize_base_url(base_url)
    hostname = urlparse(normalized).hostname or normalized
    results = [probe_dns(hostname)]

    headers = {"User-Agent": user_agent}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        for name, target in build_probe_targets(normalized):
            results.append(probe_url(client, name, target))

    return results


def format_probe_report(base_url: str, results: List[ProbeResult]) -> str:
    payload = {
        "baseUrl": normalize_base_url(base_url),
        "results": [result.to_dict() for result in results],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
