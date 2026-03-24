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

### 3. Dataset Pipeline

```bash
cd apps/crawler
anmawon-crawler crawl
anmawon-crawler clean
anmawon-crawler geocode
anmawon-crawler build-dataset
```

실행 결과는 루트의 `data/` 디렉터리에 저장됩니다.

## Current Status

- 모노레포 초기 구조 생성
- 웹 MVP 스캐폴딩 생성
- 크롤러 CLI 스캐폴딩 생성
- 데이터 스키마 초안 생성

실제 셀렉터 보정과 주소 보정 규칙은 사이트 HTML을 보면서 추가로 다듬으면 됩니다.
