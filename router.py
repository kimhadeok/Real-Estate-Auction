"""
router.py — 멀티에이전트 오케스트레이터

사용자 질문을 분류하여 적절한 에이전트로 라우팅합니다:
  - procedure → 절차 안내 에이전트
  - tutor    → 권리분석 튜터 에이전트
  - quiz     → 사례·퀴즈 에이전트
"""

from __future__ import annotations

from agents import ALL_AGENTS, procedure_agent, tutor_agent
import quiz as quiz_module
import config


# ────────────────────────────────────────────
# 라우팅 분류
# ────────────────────────────────────────────

ROUTER_SYSTEM_PROMPT = config.load_prompt("router_system.prompt")


def classify(question: str, llm=None) -> str:
    """질문을 procedure / tutor / quiz 중 하나로 분류합니다."""
    from providers import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    if llm is None:
        llm = get_llm(temperature=0.0)

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    response = llm.invoke(messages)
    label = response.content.strip().lower() if hasattr(response, "content") else ""

    # 부분 일치로 견고하게 파싱
    if "procedure" in label:
        return "procedure"
    elif "quiz" in label:
        return "quiz"
    elif "tutor" in label:
        return "tutor"
    else:
        # 폴백: tutor
        return "tutor"


# ────────────────────────────────────────────
# 핸들러
# ────────────────────────────────────────────

def handle(question: str, difficulty: str | None = None, llm=None) -> dict:
    """
    질문을 분류하고 적절한 에이전트로 전달합니다.

    Returns:
        {
            "route": str,         # procedure / tutor / quiz
            "agent": str,         # 에이전트 이름
            "answer": str,        # 답변 텍스트
            "sources": list[str], # 출처 목록
            "quiz_data": dict,    # (quiz일 때만) 출제 데이터
        }
    """
    route = classify(question, llm=llm)

    if route == "procedure":
        result = procedure_agent.query(question)
        return {
            "route": route,
            "agent": result["agent"],
            "answer": result["answer"],
            "sources": result["sources"],
            "quiz_data": None,
        }

    elif route == "quiz":
        q_data, q_text = quiz_module.get_formatted_question(difficulty=difficulty)
        return {
            "route": route,
            "agent": "사례·퀴즈",
            "answer": q_text,
            "sources": [],
            "quiz_data": q_data,
        }

    else:  # tutor (기본)
        result = tutor_agent.query(question)
        return {
            "route": route,
            "agent": result["agent"],
            "answer": result["answer"],
            "sources": result["sources"],
            "quiz_data": None,
        }
