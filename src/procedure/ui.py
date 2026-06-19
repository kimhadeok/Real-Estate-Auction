"""
src/procedure/ui.py — 경매 절차 안내 UI 모듈

경매의 9단계 절차를 타임라인으로 보여주고, 관련 질문에 답변하는 전용 챗봇을 제공합니다.
"""

from __future__ import annotations

import streamlit as st
import config
from src.common import init_page, check_api_key, ensure_db, get_agent_badge, render_footer, render_top_menu
import agents

def render_page():
    # 페이지 초기화
    init_page("경매 절차 안내 | AI 튜터", "📋")
    render_top_menu()
    check_api_key()
    ensure_db()

    # 그라데이션 타이틀 배너
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📋 경매 절차 안내</div>
        <div class="hero-subtitle">법원 경매의 9단계 절차와 관련 법령(민사집행법 등)을 학습하고 질문할 수 있는 전용 공간입니다.</div>
    </div>
    """, unsafe_allow_html=True)

    # 2열 레이아웃 배치
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("💬 절차 안내 챗봇")
        
        # 해당 페이지 전용 대화 세션 상태 관리
        if "procedure_messages" not in st.session_state:
            st.session_state["procedure_messages"] = []

        # 기존 대화 내용 표시
        for msg in st.session_state["procedure_messages"]:
            with st.chat_message(msg["role"]):
                if msg.get("badge"):
                    st.markdown(msg["badge"], unsafe_allow_html=True)
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 출처"):
                        for src in msg["sources"]:
                            st.markdown(f"• {src}")

        # 퀵 질문 링크 또는 직접 입력 감지
        pending = st.session_state.pop("pending_procedure_question", None)
        user_input = st.chat_input("경매 절차에 대해 질문해보세요... (예: 배당요구 종기가 무엇인가요?)")
        question = pending or user_input

        if question:
            # 사용자 메시지 추가 및 렌더링
            st.session_state["procedure_messages"].append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            # 에이전트 호출 및 응답 렌더링
            with st.chat_message("assistant"):
                with st.spinner("🤔 절차 지식베이스 탐색 중..."):
                    result = agents.procedure_agent.query(question)
                
                badge = get_agent_badge("procedure", result["agent"])
                st.markdown(badge, unsafe_allow_html=True)
                st.markdown(result["answer"])
                
                sources = result.get("sources", [])
                if sources:
                    with st.expander("📚 출처"):
                        for src in sources:
                            st.markdown(f"• {src}")
                            
                st.session_state["procedure_messages"].append({
                    "role": "assistant",
                    "content": result["answer"],
                    "badge": badge,
                    "sources": sources
                })
                st.rerun()

        st.divider()

        # 자주 묻는 질문 퀵버튼들
        st.markdown("##### 💡 자주 묻는 질문")
        quick_qs = [
            "경매 절차가 어떻게 되나요?",
            "배당요구 종기란 무엇인가요?",
            "매각물건명세서는 왜 중요한가요?",
            "대금 납부 기한을 지키지 못하면 어떻게 되나요?",
        ]
        q_cols = st.columns(2)
        for i, q in enumerate(quick_qs):
            col_idx = i % 2
            if q_cols[col_idx].button(q, key=f"quick_proc_{i}", use_container_width=True):
                st.session_state["pending_procedure_question"] = q
                st.rerun()

        # 초기화 버튼
        if st.session_state["procedure_messages"]:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 대화 기록 초기화", key="reset_proc_chat", use_container_width=True):
                st.session_state["procedure_messages"] = []
                st.rerun()

    with col2:
        st.subheader("🗓️ 경매 9단계 절차 일람")
        st.caption("각 단계를 클릭하시면 상세 설명과 핵심 개념을 확인하실 수 있습니다.")

        # 안내 파일 로드 및 가시성 높은 아코디언 컴포넌트 렌더링
        try:
            guide_file = config.PROCEDURES_DIR / "auction_procedure_guide.md"
            if guide_file.exists():
                guide_text = guide_file.read_text(encoding="utf-8")
                steps = []
                current_step = None
                current_content = []
                
                for line in guide_text.splitlines():
                    if line.startswith("## ") and "단계" in line:
                        if current_step:
                            steps.append((current_step, "\n".join(current_content).strip()))
                        current_step = line.replace("## ", "").strip()
                        current_content = []
                    elif current_step is not None:
                        if line.strip() != "---":
                            current_content.append(line)
                if current_step:
                    steps.append((current_step, "\n".join(current_content).strip()))

                for step_title, step_body in steps:
                    with st.expander(f"📌 {step_title}", expanded=False):
                        st.markdown(step_body)
            else:
                st.error("경매 절차 가이드 파일이 존재하지 않습니다.")
        except Exception as e:
            st.error(f"가이드를 로드하는 중 오류가 발생했습니다: {e}")

    render_footer()
