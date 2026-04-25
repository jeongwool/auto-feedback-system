## 5. Docker 실행 방법

```bash
# 이미지 빌드
docker build -t auto-feedback .

# 실행 (.env 파일에 OPENAI_API_KEY 필요)
docker run --env-file .env auto-feedback
```

## 6. 의존성 및 라이선스

| 라이브러리 | 버전 | 라이선스 |
|-----------|------|---------|
| deepagents | >=0.5.1 | MIT |
| deepagents-cli | >=0.0.3 | MIT |
| langchain-openai | >=1.1.12 | MIT |

본 프로젝트를 오픈소스로 공개할 경우 **MIT 라이선스** 채택 예정.
이유: 사용한 라이브러리가 모두 MIT이며 상업적 제한 없이 자유롭게 활용 가능하기 때문.

## 7. 보안 점검

```bash
pip install pip-audit
pip-audit
```
의존성 취약점 없음 확인 (2026-04-25 기준)
