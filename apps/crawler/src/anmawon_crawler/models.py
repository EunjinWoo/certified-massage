from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class ShopRecord:
    shop_id: str
    name: str = ""
    address_raw: str = ""
    address_normalized: str = ""
    phone: str = ""
    area_code: str = ""
    source_list_page: Optional[int] = None
    detail_url: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    geocode_status: str = "pending"
    source_fetched_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return {
            "shopId": data["shop_id"],
            "name": data["name"],
            "addressRaw": data["address_raw"],
            "addressNormalized": data["address_normalized"],
            "phone": data["phone"],
            "areaCode": data["area_code"],
            "sourceListPage": data["source_list_page"],
            "detailUrl": data["detail_url"],
            "lat": data["lat"],
            "lng": data["lng"],
            "geocodeStatus": data["geocode_status"],
            "sourceFetchedAt": data["source_fetched_at"],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ShopRecord":
        return cls(
            shop_id=str(payload.get("shopId", "")),
            name=str(payload.get("name", "")),
            address_raw=str(payload.get("addressRaw", "")),
            address_normalized=str(payload.get("addressNormalized", "")),
            phone=str(payload.get("phone", "")),
            area_code=str(payload.get("areaCode", "")),
            source_list_page=payload.get("sourceListPage"),
            detail_url=str(payload.get("detailUrl", "")),
            lat=payload.get("lat"),
            lng=payload.get("lng"),
            geocode_status=str(payload.get("geocodeStatus", "pending")),
            source_fetched_at=str(payload.get("sourceFetchedAt", "")),
        )
