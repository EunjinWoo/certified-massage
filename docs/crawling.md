# Crawling Notes

## Rules

- 요청 간격을 두고 천천히 수집합니다.
- `shopId` 기준으로 중복 제거합니다.
- 지역 코드와 페이지 수는 페이지에서 자동 발견하도록 시도합니다.
- 셀렉터는 한 파일에 모아 관리합니다.

## Outputs

- `data/raw/shops.raw.json`: 크롤링 직후 원본 데이터
- `data/processed/shops.cleaned.json`: 주소 정제 결과
- `data/processed/shops.geocoded.json`: 지오코딩 결과
- `data/processed/shops.geo.json`: 웹에서 소비하는 최종 데이터

## Validation Tips

- 실사이트 연결이 안 되는 환경에서는 먼저 파서 단위 테스트로 셀렉터 로직을 검증합니다.
- 필요하면 `ANMAWON_BASE_URL`과 `ANMAWON_USER_AGENT`를 환경변수로 조정해 재시도합니다.
- 샘플 검증은 `--max-pages-per-area` 옵션으로 범위를 제한해 진행합니다.

## Known Follow-up Work

- 상세 페이지 HTML 구조 확인 후 셀렉터 보정
- 주소 정규화 규칙 확장
- 실패 주소 수동 보정 프로세스 추가
