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
        "\n\n[에이전트 분석 최종 결과]\n"
        "1. Professor Agent: 서론의 논리적 전개가 다소 부족하나, 연구 목적은 뚜렷함.\n"
        "2. Writer Agent: 학술적 용어(예: '제안한다' -> '규명하고자 한다')로 문체 교정 완료.\n"
        "3. Editor Agent: 인용구 형식 검토 완료 및 최종 승인(PASS).\n\n"
        "▶ 수정된 본문: 본 연구는 딥러닝 아키텍처를 기반으로 자원 순환 효율을 극대화하는 "
        "지능형 분리수거 시스템의 메커니즘을 규명하고자 한다..."
    )

    return FeedbackResponse(
        status="success",
        message=f"분석 완료 (수신: {len(request.text)}자). {demo_result}"
    )
