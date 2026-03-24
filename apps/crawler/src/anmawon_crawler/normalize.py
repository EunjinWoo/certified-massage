from __future__ import annotations

import re
from typing import Iterable, List

from .models import ShopRecord


CITY_REPLACEMENTS = {
    "서울시 ": "서울특별시 ",
    "부산시 ": "부산광역시 ",
    "대구시 ": "대구광역시 ",
    "인천시 ": "인천광역시 ",
    "광주시 ": "광주광역시 ",
    "대전시 ": "대전광역시 ",
    "울산시 ": "울산광역시 ",
    "세종시 ": "세종특별자치시 ",
}

PROVINCE_REPLACEMENTS = {
    "서울 ": "서울특별시 ",
    "부산 ": "부산광역시 ",
    "대구 ": "대구광역시 ",
    "인천 ": "인천광역시 ",
    "광주 ": "광주광역시 ",
    "대전 ": "대전광역시 ",
    "울산 ": "울산광역시 ",
    "세종 ": "세종특별자치시 ",
    "경기 ": "경기도 ",
    "강원 ": "강원특별자치도 ",
    "충북 ": "충청북도 ",
    "충남 ": "충청남도 ",
    "전북 ": "전북특별자치도 ",
    "전남 ": "전라남도 ",
    "경북 ": "경상북도 ",
    "경남 ": "경상남도 ",
    "제주 ": "제주특별자치도 ",
}

PHONE_DIGITS_PATTERN = re.compile(r"\d")


def normalize_whitespace(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_address(value: str) -> str:
    normalized = normalize_whitespace(value)

    for old, new in CITY_REPLACEMENTS.items():
        if normalized.startswith(old):
            normalized = normalized.replace(old, new, 1)
            break

    for old, new in PROVINCE_REPLACEMENTS.items():
        if normalized.startswith(old):
            normalized = normalized.replace(old, new, 1)
            break

    normalized = normalized.replace("특별시특별시", "특별시")
    normalized = normalized.replace("광역시광역시", "광역시")
    normalized = normalized.replace("특별자치도특별자치도", "특별자치도")
    return normalized.strip(" ,")


def normalize_phone(value: str) -> str:
    normalized = normalize_whitespace(value)

    if not normalized:
        return ""

    digits = "".join(PHONE_DIGITS_PATTERN.findall(normalized))

    if len(digits) == 9 and digits.startswith("02"):
        return f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"

    if len(digits) == 10 and digits.startswith("02"):
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"

    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"

    return normalized


def clean_records(records: Iterable[ShopRecord]) -> List[ShopRecord]:
    cleaned: List[ShopRecord] = []

    for record in records:
        cleaned.append(
            ShopRecord(
                shop_id=record.shop_id,
                name=normalize_whitespace(record.name),
                address_raw=normalize_whitespace(record.address_raw),
                address_normalized=normalize_address(
                    record.address_normalized or record.address_raw
                ),
                phone=normalize_phone(record.phone),
                area_code=record.area_code.strip(),
                source_list_page=record.source_list_page,
                detail_url=record.detail_url,
                lat=record.lat,
                lng=record.lng,
                geocode_status=record.geocode_status,
                source_fetched_at=record.source_fetched_at,
            )
        )

    return cleaned
