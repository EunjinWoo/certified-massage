# Data Model

최종 산출물은 `data/processed/shops.geo.json`입니다.

```json
{
  "generatedAt": "2026-03-24T00:00:00+09:00",
  "count": 1,
  "shops": [
    {
      "shopId": "031-0193",
      "name": "예시 안마원",
      "addressRaw": "경기도 ...",
      "addressNormalized": "경기도 ...",
      "phone": "031-000-0000",
      "areaCode": "031",
      "sourceListPage": 24,
      "detailUrl": "https://www.anmawon.com/FindShop/Detail?page=24&shopId=031-0193",
      "lat": 37.123,
      "lng": 127.456,
      "geocodeStatus": "success",
      "sourceFetchedAt": "2026-03-24T00:00:00+09:00"
    }
  ]
}
```

## Shop Fields

- `shopId`: 사이트의 고유 식별자
- `name`: 안마원 상호명
- `addressRaw`: 원본 주소
- `addressNormalized`: 정제된 주소
- `phone`: 전화번호
- `areaCode`: 지역 코드
- `sourceListPage`: 목록 페이지 번호
- `detailUrl`: 상세 페이지 주소
- `lat`: 위도
- `lng`: 경도
- `geocodeStatus`: `pending | success | failed | skipped`
- `sourceFetchedAt`: 마지막 수집 시각

## Validation

최종 dataset은 아래 명령으로 JSON Schema 기준 검증할 수 있습니다.

```bash
cd apps/crawler
anmawon-crawler validate-dataset
```
