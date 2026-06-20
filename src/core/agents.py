"""
agents.py — 전문 에이전트 정의

1) 절차 안내 에이전트 (procedure_agent)
2) 권리분석 튜터 에이전트 (tutor_agent)

모든 에이전트는 RagAgent를 사용하며, 라우터(router.py)가
description을 보고 적절한 에이전트로 질문을 분배합니다.
"""

from rag import RagAgent
import config

# ────────────────────────────────────────────
# ① 절차 안내 에이전트
# ────────────────────────────────────────────

PROCEDURE_SYSTEM_PROMPT = config.load_prompt("procedure_system.prompt")

procedure_agent = RagAgent(
    name="절차 안내",
    description="경매 절차, 단계, 흐름, 시간순서에 대한 질문. 예: '배당요구 종기란?', '경매 절차가 어떻게 되나요?', '입찰 방법은?'",
    system_prompt=PROCEDURE_SYSTEM_PROMPT,
    collections=[config.COLLECTION_PROCEDURES, config.COLLECTION_LAWS],
)

# ────────────────────────────────────────────
# ② 권리분석 튜터 에이전트
# ────────────────────────────────────────────

TUTOR_SYSTEM_PROMPT = config.load_prompt("tutor_system.prompt")

tutor_agent = RagAgent(
    name="권리분석 튜터",
    description="권리분석 개념, 말소기준권리, 대항력, 인수/말소, 유치권, 법정지상권 등에 대한 학습 질문. 예: '말소기준권리가 뭐야?', '대항력은 어떻게 판단해?', '유치권이 위험한 이유는?'",
    system_prompt=TUTOR_SYSTEM_PROMPT,
    collections=[
        config.COLLECTION_CASES,
        config.COLLECTION_LAWS,
        config.COLLECTION_GLOSSARY,
    ],
)

# ────────────────────────────────────────────
# 에이전트 목록 (라우터용)
# ────────────────────────────────────────────

ALL_AGENTS = [procedure_agent, tutor_agent]
