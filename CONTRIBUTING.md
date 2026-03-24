# Contributing Guide

이 레포는 크롤러와 지도 웹앱이 함께 있는 모노레포입니다. 작업 흐름을 최대한 단순하게 유지하면서도, 이슈/브랜치/커밋/PR 연결이 또렷하게 남도록 아래 규칙을 기본으로 사용합니다.

## Branch Strategy

- 기본 브랜치: `main`
- 작업 브랜치: `<type>/#<issue-number>-<short-slug>`
- 예시:
  - `feat/#1-timer`
  - `fix/#12-crawler-selector`
  - `setting/#3-project-bootstrap`

### Allowed Branch Types

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `ci`
- `perf`
- `setting`
- `deploy`

## Issue Workflow

1. 먼저 GitHub Issue를 만듭니다.
2. Issue에 목적, 범위, 검증 기준을 적습니다.
3. 해당 이슈를 해결하는 브랜치를 팝니다.
4. PR 본문에 이슈 번호를 연결합니다.

작은 변경이라도 가능하면 이슈 기준으로 묶습니다. 그래야 크롤링 규칙 변경, 주소 보정, 지도 UI 개선 이력이 남습니다.

## Commit Convention

커밋 메시지는 Conventional Commits 형식을 사용합니다.

### Format

```text
<type>: <한국어 제목>

<상세 설명 본문>
```

제목은 소문자 타입으로 시작하고, 내용은 한국어로 씁니다. 본문은 비워두지 않고 왜 바꿨는지 간단히 남깁니다. 관련 이슈가 이미 있을 때만 제목 끝이나 본문에 `#번호`를 함께 남깁니다.

### Allowed Commit Types

- `feat`: 기능 개발
- `fix`: 버그 수정
- `docs`: 문서 작업
- `refactor`: 동작 변경 없는 구조 개선
- `test`: 테스트 추가/수정
- `chore`: 일반 유지보수
- `ci`: CI/CD, GitHub Actions, 자동화
- `perf`: 성능 개선
- `setting`: 프로젝트 설정, 환경 세팅
- `deploy`: 배포, 인프라, 릴리즈 작업

### Label Mapping

- `feat` -> `Feature`
- `fix` -> `BugFix`
- `docs` -> `Docs`
- `refactor` -> `Refactor`
- `test` -> `Test`
- `chore` -> `Chore`
- `perf` -> `Performance`
- `setting` -> `Setting`
- `deploy` -> `Deploy`
- `ci` -> 상황에 따라 `Chore` 또는 `Deploy`

### Good Examples

```text
setting: 프로젝트 기본 세팅

프로젝트 기본 구조를 세팅합니다.
Next.js 웹 앱과 Python 크롤러를 함께 관리할 수 있도록 모노레포 기반을 추가합니다.
```

```text
feat: 지도 마커 렌더링 추가

카카오 지도 위에 안마원 마커를 표시합니다.
좌표가 없는 항목은 목록에서만 보이도록 분리합니다.
```

```text
perf: 목록 필터링 성능 개선

검색 시 불필요한 재계산을 줄이도록 필터링 흐름을 정리합니다.
대량 마커 데이터에서도 목록 응답 속도가 급격히 느려지지 않도록 개선합니다.
```

```text
fix: 상세 페이지 주소 파싱 보완 #14

일부 상세 페이지에서 주소가 빈 값으로 저장되는 문제를 수정합니다.
테이블 기반 파싱이 실패할 때 보조 추출 규칙을 사용하도록 보완합니다.
```

### Avoid

- `update stuff`
- `fix bug`
- `WIP`
- 본문 없는 커밋
- 존재하지 않는 이슈 번호를 습관적으로 붙인 커밋

## Pull Request Rules

- PR 하나는 하나의 목적에 집중합니다.
- PR 템플릿의 `Related Issue`, `Task Details`, `Review Requirements`를 채웁니다.
- UI 변경이면 스크린샷을 첨부합니다.
- 데이터 모델 변경이면 영향 범위를 적습니다.
- 크롤링/지오코딩 로직 변경이면 재현 방법을 적습니다.

## Validation Before PR

- Python:
  - `PYTHONPATH=apps/crawler/src python3 -m unittest discover -s apps/crawler/tests`
- Web:
  - `cd apps/web && npm install && npm run lint && npm run build`

## Automation Notes

- 로컬 코드 편집, 테스트, 커밋은 이 환경에서 처리할 수 있습니다.
- 원격 GitHub 이슈/PR 생성까지 자동화하려면 GitHub 접근 권한이 필요합니다.
- 가장 깔끔한 방법은 GitHub MCP 연결입니다.
- MCP를 연결하면 이슈 생성, 브랜치/PR 생성, 상태 확인, 리뷰 반영까지 대화 중에 이어서 할 수 있습니다.
- 원하면 매번 사용자 허가를 먼저 받고 원격 작업을 진행하는 방식으로 운영할 수 있습니다.

## Recommended Git Config

아래 설정을 해두면 원하는 커밋 스타일을 더 쉽게 유지할 수 있습니다.

```bash
git config commit.template .gitmessage.txt
```
