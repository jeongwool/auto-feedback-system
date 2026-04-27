# 자동 피드백 제공 시스템 (Auto Feedback System)

AI 에이전트를 활용한 논문 섹션별 자동 첨삭 시스템.  
학생 논문을 섹션별로 분석하여 반복적인 Ralph Loop를 통해 품질을 개선합니다.

---

## 1. 문제 정의

논문 제출 전, 지도교수의 예상 피드백을 미리 확인하고 학술적 격식(인용, 문체, 논리)을 스스로 보강하기 위한 도구.  
단순 문법 체크를 넘어, 학술적 일관성과 증거의 깊이를 비판적으로 검토하는 **가상의 지도교수 AI**가 필요했습니다.

---

## 2. 기술 스택

| 도구 | 역할 | 선택 근거 | 대안 |
|------|------|---------|------|
| deepagents | AI 에이전트 프레임워크 | Ralph Mode 지원, Sub-agent 패턴 구현 가능 | CrewAI |
| langchain-openai | LLM 연동 | OpenAI/OpenRouter API 통합 | LlamaIndex |
| FastAPI | REST API 서버 | 빠른 개발, 자동 Swagger UI 제공 | Flask |
| Docker + Compose | 컨테이너화 | 환경 독립적 실행, 다중 서비스 구성 | venv |
| GitHub Actions | CI/CD | 자동 빌드/테스트 파이프라인 | Jenkins |
| requests | 외부 API 호출 | GitHub API 호출, 표준 라이브러리 | httpx |
| pandas | 데이터 처리/분석 | 레포 통계 수집·정리, 표준 라이브러리 | polars |

---

## 3. 프로젝트 구조
auto-feedback-system/
├── main.py              # 메인 에이전트 루프
├── src/
│   ├── api.py           # FastAPI 엔드포인트
│   └── stats.py         # GitHub API + pandas 분석
├── docs/
│   ├── PROMPT.md        # 프로젝트 목표 선언
│   ├── ralph-log.md     # 반복 개선 기록
│   └── ai-usage-log.md  # AI 도구 사용 기록
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml       # 의존성 버전 고정
├── .gitignore
└── README.md

---

## 4. 에이전트 협업 플로우
PROMPT.md (프로젝트 목표 선언)
├── Professor Agent   ← 논문 심사위원급 평가
├── Writer Agent      ← 피드백 반영 수정
└── Editor Agent      ← PASS/FAIL 판정

**Ralph Mode 핵심:**
```bash
while :; do cat PROMPT.md | agent ; done
```
매 반복마다 에이전트가 기존 파일을 보고 개선합니다.

**소통 프로토콜:**
- PR description = "목적 / 변경 내용 / 검증 방법"
- 브랜치 = 각 에이전트의 격리된 작업 공간
- merge = 결과 통합

플로우 정의 후 에이전트 간 역할이 명확해져 루프 중단 없이 자율적으로 논문 첨삭이 가능해졌습니다.

---

## 5. 로컬 실행 방법

```bash
pip install uv
uv sync
uv run python main.py
```

### API 서버 실행
```bash
uv run uvicorn src.api:app --reload
# http://localhost:8000/docs 에서 Swagger UI 확인

## GitHub 레포 통계 확인 (Pandas 활용)
uv run python src/stats.py

---

## 6. Docker 실행 방법

```bash
# 단일 컨테이너
docker build -t auto-feedback .
docker run --env-file .env auto-feedback

# 다중 서비스 (agent + api)
docker-compose up --build
# http://localhost:8000/docs 에서 API 확인
```

다른 컴퓨터에서도 Docker로 동일하게 실행 가능합니다 (환경 독립적).

---

## 7. AI 코딩 도구 활용

Claude Code를 사용하여 코드를 생성하고 검증했습니다.  
자세한 내용은 [docs/ai-usage-log.md](docs/ai-usage-log.md) 참고.

**AI가 만든 코드 중 수정이 필요했던 부분:**
- 에이전트가 파일 시스템 접근을 기본으로 설계 → `NO_FILE_TOOL` 상수 수동 추가
- 터미널 UI 한글 여백 오류 → Panel padding 직접 수정
- Dockerfile에서 `COPY src/` 누락 → 수동 추가

---

## 8. 의존성 및 라이선스

| 라이브러리 | 버전 | 라이선스 |
|-----------|------|---------|
| deepagents | >=0.5.1 | MIT |
| deepagents-cli | >=0.0.3 | MIT |
| langchain-openai | >=1.1.12 | MIT |
| langchain-openrouter | >=0.2.1 | MIT |
| fastapi | >=0.110.0 | MIT |
| uvicorn | >=0.29.0 | BSD |
| requests | latest | Apache 2.0 |
| pandas | latest | BSD |

본 프로젝트를 오픈소스로 공개할 경우 **MIT 라이선스** 채택 예정.  
이유: 사용한 라이브러리가 모두 MIT/BSD이며 상업적 제한 없이 자유롭게 활용 가능하기 때문.

---

## 9. 보안 점검

```bash
python -m pip install pip-audit
python -m pip_audit
```

점검 결과 (2026-04-26 기준):

| 패키지 | 버전 | 취약점 ID | 수정 버전 |
|--------|------|-----------|---------|
| langchain-openai | 1.1.12 | GHSA-r7w7-9xr2-qq2r | 1.1.14 |
| langsmith | 0.7.29 | GHSA-rr7j-v2q5-chgv | 0.7.31 |
| pip | 26.0.1 | CVE-2026-3219 | - |

취약점 대응: langchain-openai 및 langsmith는 pyproject.toml 버전 업데이트로 해결 가능. 프로덕션 배포 전 패키지 업데이트 필요.
