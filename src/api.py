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
    return FeedbackResponse(
        status="success",
        message=f"과제 수신 완료 ({len(request.text)}자). 에이전트 분석 시작."
    )