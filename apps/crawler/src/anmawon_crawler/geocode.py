from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Tuple

import httpx

from .models import ShopRecord


KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"


def geocode_address(
    client: httpx.Client,
    api_key: str,
    address: str,
) -> Tuple[float | None, float | None, str, str | None]:
    try:
        response = client.get(
            KAKAO_GEOCODE_URL,
            params={"query": address},
            headers={"Authorization": f"KakaoAK {api_key}"},
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        return None, None, "failed", f"{type(error).__name__}: {error}"

    documents = response.json().get("documents", [])
    if not documents:
        return None, None, "failed", "not_found"

    document = documents[0]
    return float(document["y"]), float(document["x"]), "success", None


def summarize_geocoding(
    results: List[ShopRecord],
    failures: List[dict],
    *,
    cache_hits: int,
    cache_misses: int,
) -> dict:
    status_counts = Counter(record.geocode_status for record in results)
    failure_reasons = Counter(failure.get("reason", "unknown") for failure in failures)

    return {
        "total": len(results),
        "success": status_counts.get("success", 0),
        "failed": status_counts.get("failed", 0),
        "skipped": status_counts.get("skipped", 0),
        "pending": status_counts.get("pending", 0),
        "cacheHits": cache_hits,
        "cacheMisses": cache_misses,
        "failureReasons": dict(failure_reasons),
    }


def _apply_geocoding_with_client(
    client: httpx.Client,
    records: Iterable[ShopRecord],
    *,
    api_key: str,
    cache: Dict[str, Dict[str, float | str | None]],
) -> Tuple[List[ShopRecord], Dict[str, Dict[str, float | str | None]], List[dict], dict]:
    results: List[ShopRecord] = []
    failures: List[dict] = []
    cache_hits = 0
    cache_misses = 0

    for record in records:
        address = record.address_normalized or record.address_raw

        if not address:
            record.geocode_status = "skipped"
            results.append(record)
            failures.append(
                {
                    "shopId": record.shop_id,
                    "address": address,
                    "detailUrl": record.detail_url,
                    "reason": "missing_address",
                }
            )
            continue

        if address in cache:
            cache_hits += 1
            cached = cache[address]
            record.lat = cached.get("lat")  # type: ignore[assignment]
            record.lng = cached.get("lng")  # type: ignore[assignment]
            record.geocode_status = str(cached.get("status", "failed"))
            if record.geocode_status != "success":
                failures.append(
                    {
                        "shopId": record.shop_id,
                        "address": address,
                        "detailUrl": record.detail_url,
                        "reason": str(cached.get("reason", "cached_failure")),
                        "detail": cached.get("detail"),
                        "source": "cache",
                    }
                )
            results.append(record)
            continue

        cache_misses += 1
        lat, lng, status, detail = geocode_address(client, api_key, address)
        record.lat = lat
        record.lng = lng
        record.geocode_status = status

        cache[address] = {
            "lat": lat,
            "lng": lng,
            "status": status,
            "reason": None if status == "success" else detail,
            "detail": detail,
        }

        if status != "success":
            failures.append(
                {
                    "shopId": record.shop_id,
                    "address": address,
                    "detailUrl": record.detail_url,
                    "reason": detail or "unknown_failure",
                    "detail": detail,
                    "source": "api",
                }
            )

        results.append(record)

    summary = summarize_geocoding(
        results,
        failures,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )

    return results, cache, failures, summary


def apply_geocoding(
    records: Iterable[ShopRecord],
    *,
    api_key: str,
    timeout: float,
    cache: Dict[str, Dict[str, float | str | None]],
    client: httpx.Client | None = None,
) -> Tuple[List[ShopRecord], Dict[str, Dict[str, float | str | None]], List[dict], dict]:
    if not api_key:
        raise RuntimeError(
            "KAKAO_REST_API_KEY is required for the geocode command. "
            "Add it to apps/crawler/.env before running geocode."
        )

    if client is not None:
        return _apply_geocoding_with_client(
            client,
            records,
            api_key=api_key,
            cache=cache,
        )

    with httpx.Client(timeout=timeout) as client:
        return _apply_geocoding_with_client(
            client,
            records,
            api_key=api_key,
            cache=cache,
        )
