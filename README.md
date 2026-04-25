## 1. 문제 정의

학생 논문을 섹션별로 분석하여 반복적인 랄프 루프(Ralph Loop)를 통해 품질을 개선하는 자동화 도구입니다.

## 2. 기술 스택

| 도구 | 역할 | 선택 근거 |
|------|------|---------|
| deepagents | AI 에이전트 프레임워크 | Ralph Mode 지원, Sub-agent 패턴 구현 가능 |
| langchain-openai | LLM 연동 | OpenAI/OpenRouter API 통합 |
| FastAPI | REST API 서버 | 빠른 개발, 자동 Swagger UI 제공 |
| Docker | 컨테이너화 | 환경 독립적 실행 보장 |
| GitHub Actions | CI/CD | 자동 빌드/테스트 파이프라인 |

## 3. 실행 방법

### 로컬 실행
```bash
pip install uv
uv sync
uv run python main.py
```

### API 서버 실행
```bash
uv run uvicorn src.api:app --reload
# http://localhost:8000/docs 에서 Swagger UI 확인
```

## 4. Docker 실행 방법

```bash
# 단일 컨테이너
docker build -t auto-feedback .
docker run --env-file .env auto-feedback

# 다중 서비스 (agent + api)
docker-compose up --build
```
## 5. 의존성 및 라이선스

| 라이브러리 | 버전 | 라이선스 |
|-----------|------|---------|
| deepagents | >=0.5.1 | MIT |
| deepagents-cli | >=0.0.3 | MIT |
| langchain-openai | >=1.1.12 | MIT |
| langchain-openrouter | >=0.2.1 | MIT |
| fastapi | >=0.110.0 | MIT |
| uvicorn | >=0.29.0 | BSD |

본 프로젝트를 오픈소스로 공개할 경우 **MIT 라이선스** 채택 예정.  
이유: 사용한 라이브러리가 모두 MIT/BSD이며 상업적 제한 없이 자유롭게 활용 가능하기 때문.

## 6. 보안 점검

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