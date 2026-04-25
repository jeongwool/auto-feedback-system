## 목표
학생 과제를 구조 / 개념 / 언어 3가지 관점에서 자동 분석하여
정교한 피드백 리포트를 생성한다.

## 에이전트 구조
- Supervisor Agent: 전체 흐름 조율 및 3개 SubAgent에 작업 위임, 결과 통합
- Structure Agent: 과제의 논리 구조, 단락 흐름, 완성도 평가
- Concept Agent: 핵심 개념의 정확성 및 설명 깊이 평가  
- Language Agent: 문법 오류, 문체, 표현의 학술적 적절성 평가

## 기술 스택
- LangChain DeepAgents: Supervisor-SubAgent 위계 구조 및 루프 관리
- OpenRouter (GPT-4o): 고성능 추론 모델
- rich: 터미널 UI (Panel / Table / Rule)
- uv: 의존성 관리 및 실행
- Docker: 실행 환경 컨테이너화

## 완료 조건
- Structure / Concept / Language Agent 3개 모두 평가 완료
- 항목별 점수 산출 및 총점 / 등급 계산
- 개선 방향 포함한 피드백 리포트 터미널 출력

## 실행
`uv run python main.py` 또는 `docker run --env-file .env auto-feedback`