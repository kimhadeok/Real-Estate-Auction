"""
src/tutor/ui.py — 권리분석 튜터 UI 모듈

말소기준권리, 대항력 등 권리분석 핵심 개념에 대한 튜터링과 Q&A를 지원합니다.
"""

from __future__ import annotations

import streamlit as st
from src.core.common import init_page, check_api_key, ensure_db, get_agent_badge, render_footer, render_top_menu
import agents

def render_page():
    # 페이지 설정
    init_page("권리분석 튜터 | AI 튜터", "📚")
    check_api_key()
    render_top_menu()
    ensure_db()

    # 그라데이션 타이틀 배너
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📚 권리분석 튜터</div>
        <div class="hero-subtitle">가장 까다로운 권리분석의 핵심 개념(말소기준권리, 임차인의 대항력, 인수/소멸 권리)을 AI 튜터와 단계적으로 마스터하세요.</div>
    </div>
    """, unsafe_allow_html=True)

    # 2열 배치
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("💬 권리분석 Q&A 및 대화")
        
        # 권리분석 튜터 전용 세션 히스토리
        if "tutor_messages" not in st.session_state:
            st.session_state["tutor_messages"] = []

        # 기존 대화 표시
        for msg in st.session_state["tutor_messages"]:
            with st.chat_message(msg["role"]):
                if msg.get("badge"):
                    st.markdown(msg["badge"], unsafe_allow_html=True)
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 출처"):
                        for src in msg["sources"]:
                            st.markdown(f"• {src}")

        # 사용자 입력 및 질문 감지
        pending = st.session_state.pop("pending_tutor_question", None)
        user_input = st.chat_input("권리분석에 대해 궁금한 점을 질문해보세요... (예: 말소기준권리가 무엇인가요?)")
        question = pending or user_input

        if question:
            # 사용자 메시지 렌더링
            st.session_state["tutor_messages"].append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            # 에이전트 답변 호출 및 렌더링
            with st.chat_message("assistant"):
                with st.spinner("🤔 권리분석 지식베이스 검색 중..."):
                    result = agents.tutor_agent.query(question)
                
                badge = get_agent_badge("tutor", result["agent"])
                st.markdown(badge, unsafe_allow_html=True)
                st.markdown(result["answer"])
                
                sources = result.get("sources", [])
                if sources:
                    with st.expander("📚 출처"):
                        for src in sources:
                            st.markdown(f"• {src}")
                            
                st.session_state["tutor_messages"].append({
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
            "말소기준권리가 뭐야?",
            "대항력은 어떻게 판단해?",
            "대항력 있는 임차인의 보증금은 왜 낙찰자가 인수하나요?",
            "유치권이나 법정지상권도 말소기준권리로 소멸하나요?",
        ]
        q_cols = st.columns(2)
        for i, q in enumerate(quick_qs):
            col_idx = i % 2
            if q_cols[col_idx].button(q, key=f"quick_tutor_{i}", use_container_width=True):
                st.session_state["pending_tutor_question"] = q
                st.rerun()

        # 초기화 버튼
        if st.session_state["tutor_messages"]:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 대화 기록 초기화", key="reset_tutor_chat", use_container_width=True):
                st.session_state["tutor_messages"] = []
                st.rerun()

    with col2:
        st.subheader("📝 권리분석 핵심 족보")
        st.caption("권리분석의 핵심 원칙을 요약한 가이드라인입니다. 대화 중 언제든 참고하세요.")

        # 말소기준권리 요약
        st.info("""
        **🔍 말소기준권리 후보 6가지**
        등기부상 기록된 아래 권리 중 **가장 접수일자가 빠른 권리**가 말소기준권리가 됩니다:
        1. **(근)저당권**
        2. **(가)압류**
        3. **담보가등기**
        4. **경매개시결정등기**
        5. **전세권** (선순위이며 배당요구 또는 경매신청한 경우)
        
        👉 *이 시점 이후에 등기된 모든 권리는 원칙적으로 매각으로 소멸(말소)됩니다.*
        """)

        # 대항력 판단 요약
        st.warning("""
        **🏠 임차인 대항력 요건**
        - **대항력 요건**: 주택 인도(점유) + 주민등록(전입신고)
        - **대항력 발생 시점**: 전입신고 완료일의 **다음 날 오전 0시**
        
        **⚖️ 대항력 유무 비교**:
        - **대항력 있음**: 대항력 발생 시점 < 말소기준권리 설정일
          ➔ 매수인(낙찰자)이 보증금 전액을 **인수**
        - **대항력 없음**: 대항력 발생 시점 ≥ 말소기준권리 설정일
          ➔ 보증금은 매각으로 소멸하고 낙찰자에게 대항 불가 (단, 배당은 우선순위에 따름)
        """)

        # 무조건 인수 권리 요약
        st.error("""
        **⚠️ 항상 인수되는 권리 (말소기준권리보다 늦어도 인수)**
        - **유치권** (경매개시결정등기 전 점유 시작 시)
        - **법정지상권** / **분묘기지권**
        - **예고등기** (현제 제도 폐지되었으나 기존 등기 유효)
        - **가처분** (토지소유자가 건물 철거를 구하는 등 일부 특정 가처분)
        """)

    render_footer()
