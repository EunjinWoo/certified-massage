from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import httpx

from .models import ShopRecord


KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"


def geocode_address(
    client: httpx.Client,
    api_key: str,
    address: str,
) -> Tuple[float | None, float | None, str]:
    response = client.get(
        KAKAO_GEOCODE_URL,
        params={"query": address},
        headers={"Authorization": f"KakaoAK {api_key}"},
    )
    response.raise_for_status()

    documents = response.json().get("documents", [])
    if not documents:
        return None, None, "failed"

    document = documents[0]
    return float(document["y"]), float(document["x"]), "success"


def apply_geocoding(
    records: Iterable[ShopRecord],
    *,
    api_key: str,
    timeout: float,
    cache: Dict[str, Dict[str, float | str | None]],
) -> Tuple[List[ShopRecord], Dict[str, Dict[str, float | str | None]], List[dict]]:
    if not api_key:
        raise RuntimeError("KAKAO_REST_API_KEY is required for the geocode command.")

    results: List[ShopRecord] = []
    failures: List[dict] = []

    with httpx.Client(timeout=timeout) as client:
        for record in records:
            address = record.address_normalized or record.address_raw

            if not address:
                record.geocode_status = "skipped"
                results.append(record)
                failures.append(
                    {
                        "shopId": record.shop_id,
                        "reason": "missing_address",
                    }
                )
                continue

            if address in cache:
                cached = cache[address]
                record.lat = cached.get("lat")  # type: ignore[assignment]
                record.lng = cached.get("lng")  # type: ignore[assignment]
                record.geocode_status = str(cached.get("status", "failed"))
                results.append(record)
                continue

            lat, lng, status = geocode_address(client, api_key, address)
            record.lat = lat
            record.lng = lng
            record.geocode_status = status

            cache[address] = {
                "lat": lat,
                "lng": lng,
                "status": status,
            }

            if status != "success":
                failures.append(
                    {
                        "shopId": record.shop_id,
                        "address": address,
                        "reason": "not_found",
                    }
                )

            results.append(record)

    return results, cache, failures
