## 목표
학생 논문을 섹션별로 자동 분석하여 반복적인 Ralph Loop를 통해
학술적 품질을 개선하는 피드백 시스템을 구축한다.

## 에이전트 구조
- Professor Agent: 논문 심사위원급 엄격한 비평 수행. 5개 기준(구조적 완성도, 논리적 일관성, 학술적 문체, 증거 및 인용, 분량 및 깊이)으로 섹션 평가
- Writer Agent: 교수 피드백과 편집장 수정 지시를 반영하여 섹션을 직접 수정·보강
- Editor Agent: 5개 기준 충족 여부를 판단하여 PASS/FAIL 판정 및 구체적 수정 가이드 제시

## 기술 스택
- LangChain DeepAgents: 멀티 에이전트 위계 구조 및 Ralph Loop 관리
- OpenRouter (GPT-4o): 고성능 추론 모델
- FastAPI + uvicorn: REST API 엔드포인트 (/health, /feedback)
- rich: 터미널 UI (Panel / Table / Rule)
- Docker + docker-compose: 실행 환경 컨테이너화
- uv: 의존성 관리 및 실행

## 완료 조건
- Professor → Writer → Editor 순서로 1사이클 완료
- 5개 기준 모두 PASS 시 해당 섹션 종료
- FAIL 시 최대 5회 반복 후 최적 버전 출력
- 전체 섹션 첨삭 완료 후 통합 논문 출력

## 실행
`uv run python main.py` 또는 `docker run --env-file .env auto-feedback`
