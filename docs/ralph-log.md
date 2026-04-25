## 반복 1: 기본 Supervisor-SubAgent 루프 구현
- 변경: Supervisor Agent가 Structure / Concept / Language 3개 SubAgent에
        작업을 순차 위임하는 기본 구조 구현 (main.py)
- 문제: SubAgent가 과제 텍스트를 직접 받지 않고
        "파일 경로를 알려달라"는 요청으로 루프 중단
- 문제: 터미널 출력이 한글/영문 너비 차이로 박스가 틀어짐
        (wcwidth 기반 수동 계산 방식의 한계)
- 결과: 기본 동작 확인, 에러 3건 발생

## 반복 2: 프롬프트 강화 + UI 전면 개선
- 변경: 시스템 프롬프트에 NO_FILE_TOOL 지시 추가
        ("파일 읽기/쓰기 금지, 메시지 텍스트만 분석할 것")
- 변경: "질문 금지" 강제로 에이전트 자율 완성 유도
- 변경: wcwidth 기반 수동 박스 UI 전체 제거
        → rich 라이브러리의 Panel / Table / Rule로 교체
        → console.print() 마크업으로 PASS/FAIL 색상 구분
- 결과: 루프 중단 문제 해소, 터미널 출력 깨짐 현상 완전 제거

## 반복 3: 판정 기준 완화 + Docker 환경 구성
- 변경: 편집장 에이전트 판정 기준에서 "정확한 서지 형식" 요건 제거
        → 구체적 사례/연구 언급만 있으면 인용 항목 PASS 처리
- 변경: pyproject.toml python 버전 3.14 → 3.12로 조정
        (Docker 이미지 호환성 확보)
- 변경: Dockerfile 작성, docker build + docker run 동작 확인
- 결과: FAIL 반복 횟수 평균 5회 → 3회로 단축, 전체 PASS율 향상