1. 시스템 설계 및 에이전트 구축
**AI 도구:** 
Claude Code

**프롬프트:** 
학생 과제를 자동으로 피드백해주는 시스템을 만들고 싶어. 구조, 개념, 언어 3가지 관점으로 나눠서 각각 전문 에이전트가 평가하고, 메인 에이전트가 결과를 통합하는 방식으로. LangChain DeepAgents 써서 만들어줘.

**생성된 것:** 
main.py 전체 초안 (Supervisor + 3개 SubAgent 구조)

**수정한 부분 및 이유:**
-에이전트 시스템 프롬프트에 "파일 요청 금지" 지시 수동 추가
→ AI가 파일 시스템 접근을 기본으로 설계해서 루프가 중단되는 문제 발생

-NO_FILE_TOOL 상수 정의 및 각 에이전트 프롬프트 앞에 삽입
→ 메시지 텍스트만 분석하도록 강제

2. 터미널 UI 고도화
**AI 도구:** 
Claude Code

**프롬프트:** 
지금 터미널 UI가 wcwidth로 한글 너비 수동 계산해서
박스 그리는 방식인데, VS Code 터미널에서 자꾸 틀어져.
rich 라이브러리로 전부 교체해줘. 심플하고 깔끔하게.

**생성된 것:** UI 헬퍼 함수 전체 교체
-기존: vlen / pad_right / wrap_text / box_top / box_mid / box_bot / box_row
변경: Panel / Table / Rule / console.print() 마크업

**수정한 부분 및 이유:**
Panel padding 값 수동 조정 (0, 2) → 한글 텍스트 여백이 맞지 않아 직접 수정
PASS는 green / FAIL은 red border_style로 색상 구분 추가

3. 실행 환경 컨테이너화 (Docker)
**AI 도구:**
Claude Code

**프롬프트:** 
uv로 의존성 관리하는 파이썬 프로젝트야.
pyproject.toml이랑 uv.lock 있어. Dockerfile 작성해줘.

**생성된 결과:** 
Dockerfile 초안
