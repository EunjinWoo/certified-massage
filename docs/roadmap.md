# Roadmap

## Phase 1: Scaffold

- 모노레포 구조 생성
- 데이터 스키마 정의
- 웹과 크롤러 기본 실행 경로 확보

## Phase 2: Crawl

- 지역 코드 자동 발견
- 목록 페이지 순회
- 상세 페이지 병합
- `shopId` 기준 중복 제거

## Phase 3: Clean

- 주소 정규화 규칙 추가
- 실패 주소 로그 분리
- 전화번호/상호명 표준화

## Phase 4: Geocode

- 카카오 로컬 API 연동
- 주소 캐시 구축
- 실패 건 수동 보정 루프 정리

## Phase 5: Web MVP

- JSON 데이터 로딩
- 검색, 지역 필터, 목록 패널
- 카카오 지도 렌더링

## Phase 6: Automation

- GitHub Actions 스케줄링
- 증분 수집
- 데이터 품질 리포트
