# Workflow Checklist

이 문서는 이 저장소에서 이슈 생성부터 머지까지 한 사이클을 빠르게 확인하기 위한 운영 체크리스트입니다.

## 1. Issue 만들기

- 제목은 `Feature: ...`, `BugFix: ...`, `CI: ...`, `Test: ...` 형식을 사용합니다.
- 이슈 템플릿의 `Description`, `Goal`, `Acceptance Criteria`, `Tasks`, `Validation Plan`을 현재 작업 범위에 맞게 채웁니다.
- 생성 후 assignee를 작업자에게 지정합니다.
- label은 타입에 맞게 지정합니다.

현재 라벨 매핑은 아래 기준을 사용합니다.

- `Feature` -> `⭐ Feature`
- `BugFix` -> `🐞 BugFix`
- `Docs` -> `📃 Docs`
- `Refactor` -> `🔨 Refactor`
- `Test` -> `☑️ Test`
- `Setting` -> `⚙️ Setting`
- `Performance` -> `📈 Performance`
- `Deploy` -> `🌎 Deploy`
- `CI` 또는 일반 유지보수 -> `🛠 Chore`

## 2. 브랜치 만들기

- 작업 브랜치는 `<type>/#<issue-number>-<short-slug>` 형식을 사용합니다.
- 허용 타입은 `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`, `setting`, `deploy`입니다.

예시:

- `feat/#9-list-map-interaction`
- `ci/#10-workflow-guide`
- `fix/#3-detail-parser`

이 형식은 [ci.yml](/Users/eun/Documents/dev./code/frontend/certified-massage/.github/workflows/ci.yml)에서 검사합니다.

## 3. 작업 전 로컬 준비

- 루트에서 `npm install`을 한 번 실행합니다.
- 웹 개발이 필요하면 `cd apps/web && npm install`을 실행합니다.
- 크롤러 개발이 필요하면 `cd apps/crawler && pip install -e .`를 실행합니다.

루트 `npm install`은 `commitlint`를 로컬에서 바로 실행하기 위해 필요합니다.

## 4. 커밋 규칙

- 커밋 메시지는 Conventional Commits 형식을 사용합니다.
- 제목 형식은 `<type>(optional-scope): <subject>`입니다.
- 커밋 본문은 비워둘 수 없습니다.
- 본문은 한 줄이 너무 길지 않게 1~3문장으로 끊어 적는 것을 권장합니다.

예시:

```text
feat(web): 목록과 지도 선택 상태 연동

선택된 안마원 상태를 목록과 지도에서 함께 사용하도록 정리합니다.
마커 클릭과 목록 액션이 같은 상태를 바라보도록 연결합니다.
```

로컬 확인:

- `npm run lint:commit`

## 5. PR 만들기

- PR 제목은 이슈 제목과 같은 타입 접두어 형식을 유지합니다.
- PR 본문은 [pull_request_template.md](/Users/eun/Documents/dev./code/frontend/certified-massage/.github/pull_request_template.md)를 그대로 사용합니다.
- `Related Issue 🧵`에는 반드시 `Closes #번호`를 넣습니다.
- `Summary 📌`, `Task Details 🚩`, `Validation ✅`의 placeholder는 모두 실제 내용으로 교체합니다.

## 6. PR 전 검증

루트에서 아래 명령으로 기본 검증을 한 번에 실행할 수 있습니다.

```bash
npm run check:pr
```

개별 명령:

```bash
npm run test:crawler
npm run check:web
npm run lint:commit
```

## 7. 머지 전 확인

- GitHub PR에서 `branch-name`, `pr-template`, `crawler-tests`, `web-checks`, `commitlint`가 모두 초록색인지 확인합니다.
- 필요한 경우 이슈에 진행 상황이나 블로커를 코멘트로 남깁니다.
- 머지 후 로컬에서 `main`으로 돌아가 최신 원격 상태를 fast-forward로 반영합니다.

## 8. 실행 블로커 메모

- `#17` 같은 실 API 실행 이슈는 `apps/crawler/.env`의 `KAKAO_REST_API_KEY`가 없으면 완료할 수 없습니다.
- 웹 지도 실 렌더링은 `apps/web/.env.local`의 `NEXT_PUBLIC_KAKAO_MAP_APP_KEY`가 있어야 합니다.
- 실데이터 작업은 키와 네트워크 접근 여부를 먼저 확인한 뒤 시작하는 것이 안전합니다.
