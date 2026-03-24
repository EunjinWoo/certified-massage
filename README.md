# Certified Massage Map

국가 공인 안마원 목록을 수집하고, 주소를 정제한 뒤, 지도에 표시하기 위한 모노레포입니다.

현재 구조는 다음 흐름에 맞춰 설계되어 있습니다.

1. `apps/crawler`가 목록/상세 데이터를 수집합니다.
2. 수집 결과를 정제하고 좌표를 붙입니다.
3. `data/processed/shops.geo.json`을 생성합니다.
4. `apps/web`이 최종 JSON을 읽어서 지도와 검색 UI를 렌더링합니다.

## Stack

- Web: Next.js + TypeScript
- Crawler: Python + `httpx` + `beautifulsoup4`
- Storage: JSON files
- Backend: 없음

## Repository Layout

```text
apps/
  crawler/   # 수집, 정제, 지오코딩 CLI
  web/       # 지도 프론트
packages/
  schema/    # 데이터 계약 문서 및 JSON Schema
data/
  raw/       # 원본 수집 결과
  processed/ # 정제 + 좌표 포함 결과
  cache/     # 지오코딩 캐시
  logs/      # 실패 로그
docs/        # 구현 문서
```

## Local Requirements

- Node.js 18.20+
- Python 3.9+

`apps/web`은 Node 18에서 안정적으로 시작할 수 있도록 Next.js 14 계열 기준으로 잡았습니다.

## Quick Start

### 1. Web

```bash
cd apps/web
npm install
npm run dev
```

`.env.local`은 아래 예시를 참고해 생성합니다.

```bash
cp .env.local.example .env.local
```

### 2. Crawler

```bash
cd apps/crawler
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

환경변수 파일은 다음처럼 준비합니다.

```bash
cp .env.example .env
```

선택적으로 아래 값을 설정하면 실사이트 검증 환경을 더 유연하게 맞출 수 있습니다.

```bash
ANMAWON_BASE_URL=https://www.anmawon.com
ANMAWON_USER_AGENT=Mozilla/5.0 ...
ANMAWON_REQUEST_DELAY=1.2
ANMAWON_TIMEOUT=20
KAKAO_REST_API_KEY=your_kakao_rest_api_key
```

### 3. Dataset Pipeline

```bash
cd apps/crawler
anmawon-crawler probe-source
anmawon-crawler crawl
anmawon-crawler clean
anmawon-crawler geocode
anmawon-crawler build-dataset
anmawon-crawler validate-dataset
```

실행 결과는 루트의 `data/` 디렉터리에 저장됩니다.
`geocode` 단계는 `apps/crawler/.env`에 `KAKAO_REST_API_KEY`가 있어야 실행할 수 있습니다.

## Current Status

- 모노레포 초기 구조 생성
- 웹 MVP 스캐폴딩 생성
- 크롤러 CLI 스캐폴딩 생성
- 데이터 스키마 초안 생성

실제 셀렉터 보정과 주소 보정 규칙은 사이트 HTML을 보면서 추가로 다듬으면 됩니다.
실사이트 연결이 네트워크 환경에 따라 실패할 수 있으므로, 파서 단위 테스트를 먼저 통과시키고 제한된 범위의 샘플 크롤링으로 검증하는 흐름을 권장합니다.
샘플 크롤링 전에 `anmawon-crawler probe-source`를 실행하면 DNS, HTTPS, HTTP fallback 상태를 먼저 확인할 수 있습니다.
HTTPS 연결이 리셋되는 환경에서는 아래처럼 HTTP base URL과 제한된 범위를 사용해 샘플 검증을 시작할 수 있습니다.

```bash
cd apps/crawler
ANMAWON_BASE_URL=http://www.anmawon.com anmawon-crawler crawl --area-code 031 --max-pages-per-area 1
```

## Team Workflow

- 이슈/PR 템플릿: `.github/`
- 기여 규칙: `CONTRIBUTING.md`
- 빠른 작업 체크리스트: `docs/workflow.md`
- 라벨 스펙: `.github/labels.yml`
