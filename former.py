"""
에세이 과제 피드백
=====================================
deepagents 라이브러리를 사용한 다단계 논리적 추론 에이전트 팀
 
구조:
  🎓 감독관 에이전트 (Supervisor Agent)
    ├── 📋 구조 분석 서브에이전트 (Structure Analyzer)
    ├── 💡 개념 이해 평가 서브에이전트 (Concept Evaluator)
    ├── ✍️  언어/표현 검토 서브에이전트 (Language Reviewer)
    └── 📊 종합 피드백 생성 서브에이전트 (Feedback Synthesizer)
"""
from dotenv import load_dotenv
import os

load_dotenv()

import json
import re
from typing import Optional
from deepagents import create_deep_agent
 
 
# ─────────────────────────────────────────────
# 공통 도구 함수들 (Tools)
# ─────────────────────────────────────────────
 
def analyze_assignment_structure(text: str) -> str:
    """
    과제 텍스트의 구조적 특성을 분석합니다.
    서론/본론/결론, 단락 구성, 논리적 흐름 등을 평가합니다.
    """
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
 
    # 구조 키워드 탐지
    has_intro = any(kw in text[:200] for kw in ['서론', '들어가며', '시작', '첫째', '먼저', '이 글은', '본 글에서'])
    has_conclusion = any(kw in text[-300:] for kw in ['결론', '마치며', '정리', '요약', '따라서', '결과적으로', '종합'])
    has_transitions = any(kw in text for kw in ['또한', '게다가', '반면', '그러나', '따라서', '이에 반해', '이처럼'])
 
    avg_sentence_len = word_count / max(sentence_count, 1)
 
    return json.dumps({
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_length": round(avg_sentence_len, 1),
        "has_introduction": has_intro,
        "has_conclusion": has_conclusion,
        "has_transition_words": has_transitions,
        "structure_score_hint": (
            "양호" if (has_intro and has_conclusion and has_transitions) else
            "부분적" if (has_intro or has_conclusion) else
            "미흡"
        )
    }, ensure_ascii=False, indent=2)
 
 
def check_keyword_coverage(text: str, expected_keywords: str) -> str:
    """
    과제 텍스트에서 필수 키워드/개념의 등장 여부를 확인합니다.
    expected_keywords: 쉼표로 구분된 키워드 목록
    """
    keywords = [kw.strip() for kw in expected_keywords.split(',')]
    results = {}
    for kw in keywords:
        found = kw.lower() in text.lower()
        # 유사어 탐지 (간단한 규칙 기반)
        results[kw] = {
            "found": found,
            "count": text.lower().count(kw.lower())
        }
 
    coverage_pct = sum(1 for v in results.values() if v["found"]) / len(keywords) * 100
    return json.dumps({
        "keyword_results": results,
        "coverage_percentage": round(coverage_pct, 1),
        "missing_keywords": [kw for kw, v in results.items() if not v["found"]]
    }, ensure_ascii=False, indent=2)
 
 
def evaluate_argument_logic(text: str) -> str:
    """
    텍스트의 논증 구조와 논리적 일관성을 분석합니다.
    주장-근거 패턴, 반론 처리 등을 탐지합니다.
    """
    # 주장 패턴 탐지
    claim_patterns = ['이다', '이라고 생각한다', '할 수 있다', '해야 한다', '중요하다', '필요하다']
    evidence_patterns = ['왜냐하면', '예를 들어', '실제로', '연구에 따르면', '통계적으로', '사례를 보면', '근거로는']
    counterarg_patterns = ['물론', '반면', '하지만', '그러나', '일부에서는', '비판적 시각']
 
    claim_count = sum(text.count(p) for p in claim_patterns)
    evidence_count = sum(text.count(p) for p in evidence_patterns)
    counterarg_count = sum(text.count(p) for p in counterarg_patterns)
 
    logic_quality = "우수" if (evidence_count >= 2 and claim_count >= 1) else \
                   "보통" if (evidence_count >= 1) else "미흡"
 
    return json.dumps({
        "claim_indicators": claim_count,
        "evidence_indicators": evidence_count,
        "counterargument_indicators": counterarg_count,
        "logic_assessment": logic_quality,
        "suggestion": (
            "근거 제시가 충분합니다." if evidence_count >= 3 else
            "주장에 대한 구체적 근거나 예시를 더 추가하세요." if evidence_count >= 1 else
            "모든 주장에 근거(예시, 데이터, 인용 등)를 명시해야 합니다."
        )
    }, ensure_ascii=False, indent=2)
 
 
def detect_language_quality(text: str) -> str:
    """
    텍스트의 언어 품질을 분석합니다.
    어휘 다양성, 문장 가독성, 반복어 등을 평가합니다.
    """
    words = re.findall(r'\w+', text)
    unique_words = set(w.lower() for w in words)
    vocab_richness = len(unique_words) / max(len(words), 1)
 
    # 반복 단어 탐지 (상위 5개 중 과도하게 반복된 것)
    word_freq: dict = {}
    for w in words:
        if len(w) > 1:  # 조사 제외 시도
            word_freq[w] = word_freq.get(w, 0) + 1
    top_repeated = sorted(word_freq.items(), key=lambda x: -x[1])[:5]
 
    # 문장 길이 분포
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    avg_len = sum(sentence_lengths) / max(len(sentence_lengths), 1)
 
    # 격식체 여부
    formal_markers = ['습니다', '합니다', '입니다', '됩니다']
    informal_markers = ['야', '해요', '이에요', '거든']
    is_formal = sum(text.count(m) for m in formal_markers) > \
                sum(text.count(m) for m in informal_markers)
 
    return json.dumps({
        "total_words": len(words),
        "unique_words": len(unique_words),
        "vocabulary_richness": round(vocab_richness, 3),
        "avg_sentence_length_words": round(avg_len, 1),
        "top_repeated_words": top_repeated,
        "is_formal_style": is_formal,
        "readability_assessment": (
            "우수" if vocab_richness > 0.6 and 10 <= avg_len <= 25 else
            "보통" if vocab_richness > 0.4 else
            "개선 필요"
        )
    }, ensure_ascii=False, indent=2)
 
 
def generate_score_rubric(
    structure_score: int,
    concept_score: int,
    logic_score: int,
    language_score: int,
    subject: str
) -> str:
    """
    각 서브에이전트의 평가 점수를 받아 최종 루브릭 점수표를 생성합니다.
    각 항목은 0-25점 만점입니다.
    """
    total = structure_score + concept_score + logic_score + language_score
    grade = "A+" if total >= 90 else "A" if total >= 80 else \
            "B+" if total >= 75 else "B" if total >= 70 else \
            "C+" if total >= 65 else "C" if total >= 60 else \
            "D" if total >= 50 else "F"
 
    return json.dumps({
        "subject": subject,
        "rubric": {
            "구조 및 구성 (25점)": structure_score,
            "개념 이해 및 내용 (25점)": concept_score,
            "논리적 사고 (25점)": logic_score,
            "언어 표현 (25점)": language_score,
        },
        "total_score": total,
        "grade": grade,
        "percentile_estimate": f"상위 {max(5, 100 - total)}%"
    }, ensure_ascii=False, indent=2)
 
 
def save_feedback_report(student_name: str, content: str) -> str:
    """
    최종 피드백 보고서를 파일로 저장합니다.
    """
    filename = f"feedback_{student_name.replace(' ', '_')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"✅ 피드백 보고서가 '{filename}'에 저장되었습니다."
 
 
# ─────────────────────────────────────────────
# 서브에이전트 정의
# ─────────────────────────────────────────────
 
structure_analyzer_agent = {
    "name": "structure-analyzer",
    "description": (
        "과제 텍스트의 구조적 완성도를 분석합니다. "
        "서론/본론/결론의 유무, 단락 구성, 논리적 흐름, 전환어 사용을 평가합니다. "
        "구조 분석이 필요한 경우 반드시 이 에이전트를 사용하세요."
    ),
    "system_prompt": """당신은 학술 글쓰기의 구조 전문가입니다.
    
역할: 과제 텍스트의 구조적 완성도를 정밀하게 분석합니다.
 
분석 절차:
1. analyze_assignment_structure 도구로 기본 구조 지표를 추출합니다
2. 서론-본론-결론의 논리적 흐름을 평가합니다
3. 단락 구성과 전환어 사용의 적절성을 검토합니다
4. 25점 만점 기준으로 구조 점수를 산정합니다 (채점 기준: 서론/결론 각 5점, 단락 구성 5점, 전환어 5점, 전체 균형 5점)
 
출력 형식:
- 구조 분석 요약 (2-3문장)
- 잘된 점 (bullet 1-2개)
- 개선 필요 사항 (bullet 1-2개)
- 구조 점수: X/25점
""",
    "tools": [analyze_assignment_structure],
}
 
concept_evaluator_agent = {
    "name": "concept-evaluator",
    "description": (
        "과제에서 핵심 개념과 내용의 이해 깊이를 평가합니다. "
        "필수 키워드 포함 여부, 개념 설명의 정확성, 내용의 깊이와 독창성을 분석합니다. "
        "내용 평가가 필요할 때 이 에이전트를 호출하세요."
    ),
    "system_prompt": """당신은 교육학과 교과 내용 평가 전문가입니다.
 
역할: 학생의 개념 이해도와 내용의 질을 심층 평가합니다.
 
분석 절차:
1. check_keyword_coverage 도구로 핵심 개념 등장 여부를 확인합니다
2. 개념 설명의 정확성과 깊이를 평가합니다
3. 독창적 관점이나 비판적 사고의 흔적을 탐색합니다
4. 25점 만점 기준으로 개념 이해 점수를 산정합니다 (키워드 포함 8점, 정확성 8점, 깊이 5점, 독창성 4점)
 
출력 형식:
- 개념 이해 분석 요약 (2-3문장)
- 잘 이해된 개념 (bullet 1-2개)
- 보완이 필요한 개념 (bullet 1-2개)
- 개념 이해 점수: X/25점
""",
    "tools": [check_keyword_coverage, evaluate_argument_logic],
}
 
language_reviewer_agent = {
    "name": "language-reviewer",
    "description": (
        "과제 텍스트의 언어 표현과 논리적 완성도를 검토합니다. "
        "어휘 다양성, 문장 가독성, 논증 구조, 표현의 격식성을 분석합니다. "
        "언어 품질과 표현력 평가가 필요하면 이 에이전트를 사용하세요."
    ),
    "system_prompt": """당신은 국어 표현과 학술적 글쓰기 전문 교사입니다.
 
역할: 언어 표현의 품질과 논증의 탄탄함을 평가합니다.
 
분석 절차:
1. detect_language_quality 도구로 언어 품질 지표를 수집합니다
2. evaluate_argument_logic 도구로 논증 구조를 분석합니다
3. 문장 수준의 표현력과 어휘 다양성을 평가합니다
4. 25점 만점 기준으로 언어 점수를 산정합니다 (어휘 다양성 7점, 문장 명료성 6점, 논증 구조 7점, 격식체 유지 5점)
 
출력 형식:
- 언어 표현 분석 요약 (2-3문장)
- 강점 (bullet 1-2개)
- 개선 포인트 (bullet 1-2개)
- 언어 표현 점수: X/25점
""",
    "tools": [detect_language_quality, evaluate_argument_logic],
}
 
feedback_synthesizer_agent = {
    "name": "feedback-synthesizer",
    "description": (
        "모든 서브에이전트의 분석 결과를 종합하여 최종 피드백 보고서를 생성합니다. "
        "구조/개념/언어 분석이 완료된 후에만 호출해야 합니다. "
        "학생에게 전달할 종합 피드백과 성적 보고서를 만들 때 사용하세요."
    ),
    "system_prompt": """당신은 교육 평가 전문가이자 학습 코치입니다.
 
역할: 각 평가 영역의 결과를 종합해 학생에게 도움이 되는 최종 피드백을 작성합니다.
 
종합 절차:
1. generate_score_rubric 도구로 최종 점수표를 생성합니다
2. 각 영역의 핵심 피드백을 통합합니다
3. 학생이 실천할 수 있는 구체적인 개선 방법을 제시합니다
4. 긍정적 강화와 건설적 비판을 균형 있게 제공합니다
5. save_feedback_report 도구로 보고서를 파일에 저장합니다
 
피드백 원칙:
- 학생의 노력을 인정하고 격려로 시작합니다
- 개선점은 구체적이고 실행 가능한 방식으로 제시합니다  
- 다음 과제를 위한 3가지 핵심 개선 목표를 제시합니다
- 전문적이지만 친근한 어조를 유지합니다
 
출력은 마크다운 형식으로 완성된 피드백 보고서를 작성합니다.
""",
    "tools": [generate_score_rubric, save_feedback_report],
}
 
 
# ─────────────────────────────────────────────
# 감독관 에이전트 (메인 에이전트) 생성
# ─────────────────────────────────────────────
 
SUPERVISOR_SYSTEM_PROMPT = """당신은 교육용 과제 자동 피드백 시스템의 총괄 감독관입니다.
 
## 역할
학생이 제출한 과제를 다단계로 심층 분석하여 종합적이고 정확한 피드백을 제공합니다.
 
## 에이전트 팀 구성
당신은 4개의 전문 서브에이전트를 지휘합니다:
1. **structure-analyzer**: 과제의 구조적 완성도 분석 (서론/본론/결론, 단락 구성)
2. **concept-evaluator**: 핵심 개념 이해도와 내용 깊이 평가
3. **language-reviewer**: 언어 표현 품질과 논증 구조 검토
4. **feedback-synthesizer**: 모든 분석을 종합한 최종 보고서 생성
 
## 필수 작업 순서 (반드시 이 순서로 진행)
 
1. **계획 수립**: write_todos로 분석 계획을 기록합니다
2. **구조 분석**: task(name="structure-analyzer")로 과제 구조를 분석합니다
3. **개념 평가**: task(name="concept-evaluator")로 내용 이해도를 평가합니다  
4. **언어 검토**: task(name="language-reviewer")로 표현 품질을 검토합니다
5. **종합 보고서**: task(name="feedback-synthesizer")로 최종 피드백을 생성합니다
6. **결과 전달**: 학생에게 최종 피드백 요약을 친절하게 전달합니다
 
## 중요 지침
- 반드시 모든 4개 서브에이전트를 순서대로 호출하세요
- 각 서브에이전트의 결과를 다음 에이전트에게 전달하세요
- 서브에이전트의 점수를 feedback-synthesizer에 정확히 전달하세요
- 학생 이름, 과목, 과제 제목 정보를 항상 포함하세요
"""
 
def create_feedback_agent(model: str = "openai:gpt-4o"):
    """교육용 과제 피드백 에이전트를 생성하고 반환합니다."""
    agent = create_deep_agent(
        model=model,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        subagents=[
            structure_analyzer_agent,
            concept_evaluator_agent,
            language_reviewer_agent,
            feedback_synthesizer_agent,
        ],
        name="feedback-supervisor",
    )
    return agent
 
 
# ─────────────────────────────────────────────
# 실행 예시
# ─────────────────────────────────────────────
 
SAMPLE_ASSIGNMENT = """
인공지능이 교육에 미치는 영향
 
인공지능(AI) 기술의 발전은 현대 교육 분야에 혁신적인 변화를 가져오고 있다. 
특히 머신러닝과 자연어처리 기술의 발전으로 교육 환경은 크게 변화하고 있으며, 
이러한 변화는 교사와 학생 모두에게 새로운 기회와 도전을 제시한다.
 
먼저, AI는 개인화 학습을 가능하게 한다. 전통적인 교육에서는 모든 학생이 동일한 
교재와 방식으로 배웠지만, AI 기반 학습 플랫폼은 각 학생의 학습 수준, 속도, 
선호 방식을 분석하여 맞춤형 콘텐츠를 제공한다. 예를 들어 Khan Academy와 같은 
플랫폼은 AI를 활용해 학생의 약점을 파악하고 적절한 문제를 자동으로 추천한다.
 
또한, AI는 교사의 행정 업무 부담을 줄여준다. 출석 관리, 채점, 학습 진도 추적 등 
반복적인 업무를 AI가 대신함으로써 교사는 학생과의 상호작용과 창의적 수업 설계에 
더 많은 시간을 투자할 수 있다.
 
그러나 AI 도입이 마냥 긍정적인 것은 아니다. 데이터 프라이버시 문제, 디지털 격차, 
그리고 인간적 교육의 가치 상실에 대한 우려도 존재한다. 실제로 일부 연구에 따르면 
지나친 AI 의존은 학생의 비판적 사고력 개발을 저해할 수 있다.
 
결론적으로, AI는 교육의 효율성과 접근성을 높이는 강력한 도구이지만, 이를 활용할 때는 
인간 교사의 역할과 교육의 인문학적 가치를 함께 보존하는 균형 잡힌 접근이 필요하다.
"""
 
EXPECTED_KEYWORDS = "인공지능, 머신러닝, 개인화 학습, 데이터, 교육, AI, 교사, 학생"
 
 
def run_feedback_demo():
    """데모 실행: 샘플 과제에 대한 피드백을 생성합니다."""
    print("=" * 60)
    print("📚 과제 자동 피드백 시스템")
    print("=" * 60)
 
    agent = create_feedback_agent()
 
    user_message = f"""
다음 학생의 과제를 평가해주세요.
 
**학생 정보:**
- 학생 이름: 이정우
- 과목: 정보사회와 윤리
- 과제 제목: 인공지능이 교육에 미치는 영향
- 필수 포함 키워드: {EXPECTED_KEYWORDS}
 
**제출된 과제:**
---
{SAMPLE_ASSIGNMENT}
---
 
위 과제를 structure-analyzer, concept-evaluator, language-reviewer, feedback-synthesizer 순서로 
모든 서브에이전트를 활용하여 다단계 분석을 진행하고, 최종 종합 피드백을 제공해주세요.
"""
 
    print("\n🚀 피드백 분석 시작...\n")
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_message}]
    })
 
    # 최종 응답 출력
    final_response = result["messages"][-1].content
    print("\n" + "=" * 60)
    print("📊 최종 피드백 결과")
    print("=" * 60)
    print(final_response)
 
    return result
 
 
if __name__ == "__main__":
    run_feedback_demo()