from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="자동 피드백 시스템 API")

class AssignmentRequest(BaseModel):
    text: str

class FeedbackResponse(BaseModel):
    status: str
    message: str

@app.get("/")
def root():
    return {"status": "running", "service": "자동 피드백 시스템"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/feedback", response_model=FeedbackResponse)
def get_feedback(request: AssignmentRequest):
    if not request.text.strip():
        return FeedbackResponse(status="error", message="과제 텍스트를 입력해주세요.")
    
    # 가상의 에이전트 분석 결과 (데모용)
demo_result = (
        "\n\n[학술 에이전트 피드백 보고서]\n"
        "● Professor Agent: 연구의 필요성은 명확하나, 방법론에서 LangChain의 구체적인 Chain 설계 방식이 누락됨.\n"
        "● Writer Agent: '시스템이다'와 같은 종결 어미를 '시스템을 제안하고자 한다' 등 학술적 문체로 상향 조정 완료.\n"
        "● Editor Agent: Ralph Loop 3회 수행 결과, 논리적 일관성 지수 92% 달성. 최종 승인(PASS).\n\n"
        "▶ 수정된 초안: 본 연구는 Large Language Model(LLM) 기반의 멀티 에이전트 아키텍처를 활용하여, "
        "학술 논문의 자율적 품질 개선을 도모하는 자동화 프레임워크를 제안한다..."

    return FeedbackResponse(
        status="success",
        message=f"분석 완료 (수신: {len(request.text)}자). {demo_result}"
    )
