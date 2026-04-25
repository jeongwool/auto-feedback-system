import os
import re
from dotenv import load_dotenv
from deepagents import create_deep_agent

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box as rich_box

# ── 환경 설정 ──────────────────────────────────────────────────────────────────
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENROUTER_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["OPENROUTER_MAX_TOKENS"] = "2000"

MODEL_ID = "openrouter:openai/gpt-4o:2000"

console = Console()

# ── 상수 ──────────────────────────────────────────────────────────────────────
MAX_CYCLES_PER_SECTION = 5

CRITERIA_LABELS = {
    "1": "구조적 완성도",
    "2": "논리적 일관성",
    "3": "학술적 문체",
    "4": "증거 및 인용",
    "5": "분량 및 깊이",
}

ACADEMIC_CRITERIA = """
[검수 통과 기준 — 5개 항목 모두 충족해야 PASS]
1. 구조적 완성도 : 해당 섹션이 논문 구조 내에서 역할을 완벽히 수행하는가?
2. 논리적 일관성 : 섹션 내 주장이 일관되며 전체 논지에서 벗어나지 않는가?
3. 학술적 문체   : 해요체·구어체 없이 전문적인 문어체를 사용했는가?
4. 증거 및 인용  : 주장을 뒷받침하는 구체적 사례나 연구가 언급되었는가?
                   (정확한 서지 출처 형식은 요구하지 않음)
5. 분량 및 깊이  : 단순 나열이 아닌 심층 분석이 포함되어 있는가?
"""

NO_FILE_TOOL = (
    "중요: 논문 내용은 이미 메시지에 포함되어 있습니다. "
    "파일 읽기·쓰기, 외부 도구 사용 없이 메시지 텍스트만 분석하세요. "
    "절대로 파일 경로를 참조하거나 파일 시스템에 접근하지 마세요.\n\n"
)

INSPECT_FORMAT = """
출력 형식 (반드시 준수):
첫 줄: '결과: PASS' 또는 '결과: FAIL'
이후 각 항목:
[ITEM]
번호: <1~5>
상태: PASS 또는 FAIL
지시: (FAIL인 경우만) 수정 지시 한 줄
[/ITEM]
- 점수 금지. 수정본 출력 금지. 질문 금지.
"""


# ── UI 헬퍼 ───────────────────────────────────────────────────────────────────
def print_main_title(title: str):
    console.print()
    console.print(Panel(
        Text(title, justify="center", style="bold white"),
        style="dim",
        padding=(0, 4),
    ))
    console.print()


def print_section_start(idx: int, total: int, title: str):
    console.print()
    console.rule(f"[bold]섹션 {idx}/{total}  ·  {title}[/bold]", style="dim")


def print_cycle_header(cycle: int, max_c: int):
    console.print()
    console.print(f"  [dim]🔄  사이클 {cycle} / {max_c}[/dim]")


def print_feedback(feedback: str):
    console.print()
    console.rule("[dim]교수 에이전트 피드백[/dim]", style="dim")
    console.print(Panel(
        feedback.strip(),
        border_style="dim",
        padding=(0, 2),
    ))


def print_revised(content: str):
    console.print()
    console.rule("[green]PASS — 최종 수정본[/green]", style="green")
    console.print(Panel(
        content.strip(),
        border_style="green",
        padding=(0, 2),
    ))


def print_editor_result(is_pass: bool, items: list[dict], editor_comment: str):
    console.print()
    console.rule("[dim]편집장 검수 결과[/dim]", style="dim")

    table = Table(box=rich_box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("상태", width=3)
    table.add_column("항목")
    table.add_column("지시", style="dim")

    for it in items:
        mark  = "[green]✓[/green]" if it["pass"] else "[red]✗[/red]"
        label = CRITERIA_LABELS.get(it["num"], f"항목 {it['num']}")
        guide = it["guide"] if not it["pass"] and it["guide"] else ""
        table.add_row(mark, f"{it['num']}. {label}", guide)

    pc = sum(1 for i in items if i["pass"])
    result_label = "[green]PASS[/green]" if is_pass else f"[red]FAIL  {pc}/5[/red]"

    console.print(Panel(
        table,
        title=result_label,
        border_style="green" if is_pass else "red",
        padding=(0, 1),
    ))


def status_line(emoji: str, msg: str):
    console.print(f"\n  {emoji}  [dim]{msg}[/dim]")


def print_section_final(
    title: str,
    passed: bool,
    best_cycle: int,
    best_content: str,
    best_items: list[dict],
    fail_reason: str = "",
):
    if passed:
        console.print(f"\n  [green]✓[/green]  섹션 완료: [bold]{title}[/bold] — PASS")
        return

    # FAIL: 최적 버전 출력
    console.print()
    console.rule(f"[yellow]⚠  최대 사이클 초과 — {title}[/yellow]", style="yellow")
    if fail_reason:
        console.print(Panel(fail_reason, border_style="yellow", padding=(0, 2)))

    console.print(Panel(
        best_content.strip(),
        title=f"[dim]최적 버전 (사이클 {best_cycle})[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))


def print_final_integrated(sections_result: list[dict]):
    console.print()
    console.rule("[bold white]최종 통합 논문[/bold white]")
    console.print()

    for sec in sections_result:
        console.rule(f"[dim]{sec['title']}[/dim]", style="dim")
        console.print(sec["best_content"].strip())
        console.print()

    console.rule("[green]논문 전체 첨삭 완료[/green]", style="green")


def print_overall_history(sections_result: list[dict]):
    console.print()
    table = Table(
        title="전체 섹션 첨삭 이력",
        box=rich_box.SIMPLE_HEAD,
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("섹션", style="bold")
    table.add_column("결과", justify="center")
    table.add_column("통과 기준", justify="center")

    for sec in sections_result:
        pc     = sum(1 for i in sec["best_items"] if i["pass"])
        result = "[green]PASS[/green]" if sec["passed"] else "[yellow]FAIL[/yellow]"
        table.add_row(sec["title"], result, f"{pc}/5")

    console.print(table)


# ── 섹션 파싱 ──────────────────────────────────────────────────────────────────
HEADER_PATTERNS = [
    r'^(제?\s*\d+\s*장\s*.+)',
    r'^(\d+\.\s*.+)',
    r'^([IVX]+\.\s*.+)',
    r'^(#+\s*.+)',
    r'^([가-힣]{2,10})\s*$',
    r'^(Abstract|Introduction|Method|Result|Discussion|Conclusion)',
]

SECTION_KEYWORDS = [
    "서론", "들어가며", "연구 배경", "연구배경",
    "이론", "선행 연구", "선행연구", "문헌",
    "연구 방법", "연구방법", "방법론", "가설", "실험",
    "결과", "분석", "고찰", "논의",
    "결론", "마치며", "요약",
]

def detect_sections(text: str) -> list[dict]:
    lines = text.strip().split("\n")

    split_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pat in HEADER_PATTERNS:
            if re.match(pat, stripped, re.IGNORECASE):
                split_indices.append((i, stripped))
                break

    if len(split_indices) >= 2:
        sections = []
        for idx, (line_no, title) in enumerate(split_indices):
            start = line_no + 1
            end   = split_indices[idx + 1][0] if idx + 1 < len(split_indices) else len(lines)
            content = "\n".join(lines[start:end]).strip()
            if content:
                sections.append({"title": title, "content": content})
        return sections

    keyword_hits = []
    for i, line in enumerate(lines):
        for kw in SECTION_KEYWORDS:
            if kw in line and len(line.strip()) < 30:
                keyword_hits.append((i, line.strip()))
                break

    if len(keyword_hits) >= 2:
        sections = []
        for idx, (line_no, title) in enumerate(keyword_hits):
            start = line_no + 1
            end   = keyword_hits[idx + 1][0] if idx + 1 < len(keyword_hits) else len(lines)
            content = "\n".join(lines[start:end]).strip()
            if content:
                sections.append({"title": title, "content": content})
        return sections

    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text.strip()) if p.strip()]
    if len(paragraphs) == 0:
        return [{"title": "전체", "content": text.strip()}]

    n_sec = min(6, max(3, len(paragraphs) // 3))
    chunk = max(1, len(paragraphs) // n_sec)
    sections = []
    labels = ["서론부", "이론 배경", "연구 방법", "실험 및 결과", "고찰", "결론부"]
    for i in range(n_sec):
        start = i * chunk
        end   = (i + 1) * chunk if i < n_sec - 1 else len(paragraphs)
        content = "\n\n".join(paragraphs[start:end])
        if content:
            sections.append({"title": labels[i] if i < len(labels) else f"섹션 {i+1}", "content": content})
    return sections


# ── 응답 파싱 ──────────────────────────────────────────────────────────────────
def last_message(res) -> str:
    messages = res["messages"]
    for msg in reversed(messages):
        role    = getattr(msg, "role",    None) or (msg.get("role")    if isinstance(msg, dict) else None)
        content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else None)
        if role == "assistant" and content:
            return content.strip()
    last = messages[-1]
    content = getattr(last, "content", None) or (last.get("content") if isinstance(last, dict) else "")
    return content.strip()

def parse_items(decision: str) -> list[dict]:
    results = []
    for block in re.finditer(r'\[ITEM\](.*?)\[/ITEM\]', decision, re.DOTALL):
        b = block.group(1)
        num_m   = re.search(r'번호\s*:\s*(\d)', b)
        state_m = re.search(r'상태\s*:\s*(PASS|FAIL)', b, re.IGNORECASE)
        guide_m = re.search(r'지시\s*:\s*(.+)', b)
        if num_m and state_m:
            results.append({
                "num":   num_m.group(1),
                "pass":  state_m.group(1).upper() == "PASS",
                "guide": guide_m.group(1).strip() if guide_m else "",
            })
    return results

def pass_count(items: list[dict]) -> int:
    return sum(1 for i in items if i["pass"])


# ── 에이전트 팩토리 ────────────────────────────────────────────────────────────
def make_professor():
    return create_deep_agent(
        model=MODEL_ID,
        name="Professor-Agent",
        system_prompt=(
            NO_FILE_TOOL
            + "당신은 세계적인 석학 지도교수입니다.\n"
              "아래 기준으로 논문 섹션을 평가하세요.\n\n"
            + ACADEMIC_CRITERIA
            + "\n출력 규칙:\n"
              "- 기준 항목 번호(1~5)마다 ① 문제점, ② 개선 팁을 각각 한 줄로 작성하세요.\n"
              "- 수정본·수정 문장은 절대 쓰지 마세요.\n"
              "- 점수 금지."
        ),
    )

def make_writer():
    return create_deep_agent(
        model=MODEL_ID,
        name="Writer-Agent",
        system_prompt=(
            NO_FILE_TOOL
            + "당신은 세계 최고의 논문 집필 전문가입니다.\n"
              "교수 피드백과 편집장 수정 지시를 반영하여 섹션을 직접 수정·보강하세요.\n"
              "수정된 섹션 전문만 출력하세요. 설명·코멘트는 일절 쓰지 마세요.\n"
              "사용자에게 질문하거나 파일을 요구하지 마세요."
        ),
    )

def make_inspector():
    return create_deep_agent(
        model=MODEL_ID,
        name="Editor-Agent",
        system_prompt=(
            NO_FILE_TOOL
            + "당신은 학술지 최종 편집장입니다.\n"
              "5개 기준을 섹션이 충족했는지 판단하고, 아래 형식으로만 출력하세요.\n\n"
            + ACADEMIC_CRITERIA
            + "\n" + INSPECT_FORMAT
        ),
    )


# ── 핵심 루프 ─────────────────────────────────────────────────────────────────
def process_section(
    section_title: str,
    section_content: str,
    section_idx: int,
    total_sections: int,
    max_cycles: int = MAX_CYCLES_PER_SECTION,
) -> dict:
    print_section_start(section_idx, total_sections, section_title)

    current_content = section_content
    best_content    = section_content
    best_items      = []
    best_pc         = -1
    best_cycle      = 1
    passed          = False

    for cycle in range(1, max_cycles + 1):
        print_cycle_header(cycle, max_cycles)

        # 1) 교수 피드백
        status_line("⏳", "교수 에이전트가 섹션을 검토하고 있습니다...")
        professor = make_professor()
        prof_res  = professor.invoke({
            "messages": [{
                "role": "user",
                "content": (
                    f"아래 논문 섹션({section_title})을 평가하세요.\n\n"
                    f"{current_content}"
                ),
            }]
        })
        feedback = last_message(prof_res)
        print_feedback(feedback)

        # 2) 필자 수정
        status_line("⏳", "필자 에이전트가 섹션을 수정하고 있습니다...")
        writer    = make_writer()
        write_res = writer.invoke({
            "messages": [{
                "role": "user",
                "content": (
                    f"교수 피드백:\n{feedback}\n\n"
                    f"아래 섹션({section_title})을 수정하세요:\n\n{current_content}"
                ),
            }]
        })
        revised = last_message(write_res)

        # 3) 편집장 검수
        status_line("⏳", "편집장 에이전트가 기준 충족 여부를 확인하고 있습니다...")
        inspector    = make_inspector()
        inspect_res  = inspector.invoke({
            "messages": [{
                "role": "user",
                "content": (
                    f"섹션명: {section_title}\n\n"
                    f"[이전 버전]\n{current_content}\n\n"
                    f"[수정 버전]\n{revised}\n\n"
                    f"[교수 피드백 참고]\n{feedback}\n\n"
                    f"이전 버전 대비 수정 버전에서 개선된 부분을 긍정적으로 반영하여 검수하세요."
                ),
            }]
        })
        decision = last_message(inspect_res)
        is_pass  = "PASS" in decision.upper() and "FAIL" not in decision.upper()
        items    = parse_items(decision)
        pc       = pass_count(items)

        editor_comment = re.sub(r'\[ITEM\].*?\[/ITEM\]', '', decision, flags=re.DOTALL).strip()
        editor_comment = re.sub(r'결과\s*:\s*(PASS|FAIL)', '', editor_comment).strip()

        print_editor_result(is_pass, items, editor_comment)

        if pc > best_pc:
            best_pc      = pc
            best_content = revised
            best_items   = items
            best_cycle   = cycle

        current_content = revised

        if is_pass:
            passed = True
            print_revised(revised)
            status_line("✅", f"사이클 {cycle}에서 모든 기준 통과!")
            break

        if cycle < max_cycles:
            status_line("🔁", f"기준 미달 — 다음 사이클로 계속합니다. ({pc}/5 통과)")

    fail_reason = ""
    if not passed:
        fails = [i for i in best_items if not i["pass"]]
        if fails:
            parts = []
            for f in fails:
                label = CRITERIA_LABELS.get(f["num"], f"항목 {f['num']}")
                parts.append(f"{label}: {f['guide']}" if f["guide"] else label)
            fail_reason = (
                f"{max_cycles}회 사이클 동안 다음 기준이 충족되지 못했습니다 → "
                + " / ".join(parts)
            )

    print_section_final(
        title        = section_title,
        passed       = passed,
        best_cycle   = best_cycle,
        best_content = best_content,
        best_items   = best_items,
        fail_reason  = fail_reason,
    )

    return {
        "title":        section_title,
        "passed":       passed,
        "best_content": best_content,
        "best_items":   best_items,
        "best_cycle":   best_cycle,
        "cycles_run":   best_cycle,
    }


# ── 메인 진입점 ────────────────────────────────────────────────────────────────
def run_thesis_ralph_loop(topic: str, thesis_text: str, max_cycles: int = MAX_CYCLES_PER_SECTION):
    print_main_title("논문 섹션별 랄프 루프 첨삭 시스템")

    console.print(f"  주제         :  {topic}")
    console.print(f"  섹션당 최대  :  {max_cycles}회 랄프 루프")

    sections = detect_sections(thesis_text)
    console.print(f"  감지된 섹션  :  {len(sections)}개\n")
    for i, sec in enumerate(sections, 1):
        preview = sec["content"][:40].replace("\n", " ")
        console.print(f"    {i}. [bold]{sec['title']}[/bold]  —  {preview}...")

    results = []
    for idx, sec in enumerate(sections, 1):
        result = process_section(
            section_title    = sec["title"],
            section_content  = sec["content"],
            section_idx      = idx,
            total_sections   = len(sections),
            max_cycles       = max_cycles,
        )
        results.append(result)

    print_overall_history(results)
    print_final_integrated(results)

    integrated = "\n\n".join(r["best_content"] for r in results)
    return integrated, results


# ── 실행 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    TEST_TOPIC = "인공지능(AI)의 발달이 교육 분야에 미치는 영향"

    THESIS_WITH_HEADERS = """
1. 서론

인공지능(AI) 기술의 발전은 현대 교육 분야에 혁신적인 변화를 가져오고 있다.
특히 머신러닝과 자연어처리 기술의 발전으로 교육 환경은 크게 변화하고 있으며,
이러한 변화는 교사와 학생 모두에게 새로운 기회와 도전을 제시한다.

2. 이론적 배경 및 선행 연구

AI는 개인화 학습을 가능하게 한다. 전통적인 교육에서는 모든 학생이 동일한
교재와 방식으로 배웠지만, AI 기반 학습 플랫폼은 각 학생의 학습 수준, 속도,
선호 방식을 분석하여 맞춤형 콘텐츠를 제공한다. 예를 들어 Khan Academy와 같은
플랫폼은 AI를 활용해 학생의 약점을 파악하고 적절한 문제를 자동으로 추천한다.

3. 연구 방법 및 가설

본 연구는 국내 중·고등학교 학생 500명을 대상으로 AI 기반 학습 도구 도입 전후
학업 성취도를 비교하는 준실험 설계를 채택하였다. 연구 가설은 다음과 같다:
H1) AI 기반 학습 도구를 사용하는 학생은 그렇지 않은 학생보다 성취도가 높다.

4. 결과 및 고찰

AI 기반 학습 도구를 사용한 집단은 통제 집단에 비해 평균 성적이 15% 향상되었다.
그러나 AI 도입이 마냥 긍정적인 것은 아니다. 데이터 프라이버시 문제, 디지털 격차,
인간적 교육의 가치 상실에 대한 우려도 존재한다.

5. 결론

AI는 교육의 효율성과 접근성을 높이는 강력한 도구이지만, 이를 활용할 때는
인간 교사의 역할과 교육의 인문학적 가치를 함께 보존하는 균형 잡힌 접근이 필요하다.
    """

    run_thesis_ralph_loop(
        topic       = TEST_TOPIC,
        thesis_text = THESIS_WITH_HEADERS,
        max_cycles  = 5,
    )