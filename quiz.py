"""
quiz.py — 사례·퀴즈 에이전트

가상 매각물건명세서를 출제하고, 학습자의 답안을 채점합니다.
벡터 검색이 아닌 JSON 직접 로드 방식으로 **정답 누출을 방지**합니다.

핵심 설계:
- get_question(): 사실관계만 포함된 문제 출제 (정답 숨김)
- grade(): 항목별 채점 (말소기준권리/대항력/인수·말소/위험도)
"""

from __future__ import annotations

import json
import random
from typing import Optional

import config


def _load_cases() -> list[dict]:
    """사례 JSON을 로드합니다."""
    return json.loads(config.CASES_PATH.read_text(encoding="utf-8"))


def get_question(
    difficulty: Optional[str] = None,
    case_id: Optional[str] = None,
) -> dict:
    """
    퀴즈 문제를 출제합니다. 정답(analysis)은 포함하지 않습니다.

    Args:
        difficulty: '입문', '중급', '고급' 또는 None(랜덤)
        case_id: 특정 사례 지정 (있으면 difficulty 무시)

    Returns:
        {
            "case_id": str,
            "difficulty": str,
            "title": str,
            "property": dict,
            "registry": dict,
            "tenants": list,
            "special_claims": list,  # (있는 경우)
            "question": str,
        }
    """
    cases = _load_cases()

    if case_id:
        selected = [c for c in cases if c["case_id"] == case_id]
        if not selected:
            raise ValueError(f"사례 '{case_id}'를 찾을 수 없습니다.")
        case = selected[0]
    elif difficulty:
        filtered = [c for c in cases if c["difficulty"] == difficulty]
        if not filtered:
            raise ValueError(f"난이도 '{difficulty}'에 해당하는 사례가 없습니다.")
        case = random.choice(filtered)
    else:
        case = random.choice(cases)

    # 정답(analysis)을 제외하고 반환
    result = {
        "case_id": case["case_id"],
        "difficulty": case["difficulty"],
        "title": case["title"],
        "property": case["property"],
        "registry": case["registry"],
        "tenants": case.get("tenants", []),
        "question": case["question"],
    }

    # 유치권 등 특수 청구가 있으면 포함
    if "special_claims" in case:
        result["special_claims"] = case["special_claims"]

    return result


def _format_question_text(q: dict) -> str:
    """문제를 사람이 읽을 수 있는 텍스트로 포맷합니다."""
    lines = []
    lines.append(f"📋 **{q['title']}** (난이도: {q['difficulty']})")
    lines.append("")

    # 물건 정보
    prop = q["property"]
    lines.append(f"**물건 정보**: {prop['type']} | {prop['location']} | "
                 f"{prop['area_m2']}㎡")
    lines.append(f"감정가: {prop['appraisal_value']:,}원 | "
                 f"최저매각가격: {prop['minimum_bid_price']:,}원")
    lines.append("")

    # 등기부
    lines.append("**📜 등기부 (을구)**")
    for entry in q["registry"]["entries"]:
        amount_str = f" | {entry['amount']:,}원" if "amount" in entry else ""
        lines.append(
            f"  • {entry['date']} | {entry['type']} | "
            f"{entry['holder']}{amount_str}"
        )
        if "details" in entry:
            lines.append(f"    └ {entry['details']}")
    lines.append("")

    # 임차인
    if q["tenants"]:
        lines.append("**🏠 임차인 현황**")
        for t in q["tenants"]:
            lines.append(
                f"  • {t['name']} | 전입: {t['registration_date']} | "
                f"보증금: {t['deposit']:,}원 | "
                f"월세: {t.get('monthly_rent', 0):,}원"
            )
            if t.get("fixed_date"):
                lines.append(f"    └ 확정일자: {t['fixed_date']}")
        lines.append("")

    # 특수 청구
    if q.get("special_claims"):
        lines.append("**⚠️ 특수 권리 주장**")
        for sc in q["special_claims"]:
            lines.append(
                f"  • {sc['type']} | {sc['claimant']} | "
                f"{sc['amount']:,}원"
            )
            lines.append(f"    └ {sc['details']}")
        lines.append("")

    # 문제
    lines.append("**❓ 분석 과제**")
    lines.append(q["question"])

    return "\n".join(lines)


def get_formatted_question(
    difficulty: Optional[str] = None,
    case_id: Optional[str] = None,
) -> tuple[dict, str]:
    """
    문제를 출제하고 포맷된 텍스트도 함께 반환합니다.

    Returns:
        (원본 dict, 포맷된 텍스트)
    """
    q = get_question(difficulty=difficulty, case_id=case_id)
    text = _format_question_text(q)
    return q, text


def grade(case_id: str, user_answer: str, llm=None) -> dict:
    """
    학습자의 답안을 채점합니다.

    Args:
        case_id: 사례 ID
        user_answer: 학습자가 작성한 답안 텍스트

    Returns:
        {
            "case_id": str,
            "scores": dict,      # 항목별 점수 (0 or 1)
            "total": int,        # 총점 (0~4)
            "feedback": str,     # LLM이 생성한 항목별 피드백
        }
    """
    from providers import get_llm

    if llm is None:
        llm = get_llm(temperature=0.1)

    # 정답 로드
    cases = _load_cases()
    selected = [c for c in cases if c["case_id"] == case_id]
    if not selected:
        raise ValueError(f"사례 '{case_id}'를 찾을 수 없습니다.")

    case = selected[0]
    analysis = case["analysis"]

    # 채점 프롬프트 구성
    grading_prompt = _build_grading_prompt(case, analysis, user_answer)

    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=GRADING_SYSTEM_PROMPT),
        HumanMessage(content=grading_prompt),
    ]

    response = llm.invoke(messages)
    feedback = response.content if hasattr(response, "content") else str(response)

    return {
        "case_id": case_id,
        "total": 4,  # 만점
        "feedback": feedback,
        "correct_analysis": analysis,
    }


GRADING_SYSTEM_PROMPT = """당신은 부동산 경매 권리분석 **채점 교사**입니다.

학습자의 답안을 정답과 비교하여 4가지 항목별로 채점하고 피드백을 제공하세요.

## 채점 항목 (각 1점, 총 4점)
1. **말소기준권리** — 올바른 말소기준권리를 찾았는가?
2. **대항력 판단** — 각 임차인의 대항력 유무를 정확히 판단했는가?
3. **인수/말소 구분** — 인수되는 권리와 말소되는 권리를 정확히 구분했는가?
4. **위험도 평가** — 물건의 위험도를 합리적으로 평가했는가?

## 피드백 형식
각 항목별로:
- ✅ 정답 / ❌ 오답 / ⚠️ 부분 정답
- 간단한 피드백
- 정답 설명 (근거 법령 포함)

마지막에 총점과 종합 피드백을 작성하세요.

⚠️ 교육 목적 채점이므로, 격려하면서도 정확한 지식을 전달하세요.
"""


def _build_grading_prompt(case: dict, analysis: dict, user_answer: str) -> str:
    """채점용 프롬프트를 구성합니다."""
    # 사실관계
    facts = {
        "title": case["title"],
        "registry": case["registry"],
        "tenants": case.get("tenants", []),
    }
    if "special_claims" in case:
        facts["special_claims"] = case["special_claims"]

    # 정답
    correct = json.dumps(analysis, ensure_ascii=False, indent=2)
    facts_str = json.dumps(facts, ensure_ascii=False, indent=2)

    return (
        f"## 사례 사실관계\n```json\n{facts_str}\n```\n\n"
        f"## 정답 (채점 기준)\n```json\n{correct}\n```\n\n"
        f"## 학습자 답안\n{user_answer}\n\n"
        f"위 정답을 기준으로 학습자 답안을 4개 항목별로 채점해주세요."
    )
