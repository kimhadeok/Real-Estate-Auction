"""
src/quiz/ui.py — 사례 퀴즈 연습 UI 모듈

실제 경매 물건의 권리 분석을 모의 연습하고 AI에게 채점을 받을 수 있는 공간입니다.
등기부 및 임차인 현황을 세련된 테이블과 카드로 렌더링합니다.
"""

from __future__ import annotations

import streamlit as st
import quiz as quiz_module
from src.common import init_page, check_api_key, ensure_db, render_footer, render_top_menu
import textwrap

def render_page():
    # 페이지 설정
    init_page("사례 퀴즈 연습 | AI 튜터", "📝")
    render_top_menu()
    check_api_key()
    ensure_db()

    # 그라데이션 타이틀 배너
    st.markdown(textwrap.dedent("""
    <div class="hero-container">
        <div class="hero-title">📝 사례 및 퀴즈 연습</div>
        <div class="hero-subtitle">가상 법원경매 매각물건명세서를 정밀하게 분석하여 권리분석 실력을 테스트하고, AI의 채점 및 맞춤형 피드백을 받으세요.</div>
    </div>
    """), unsafe_allow_html=True)

    # 퀴즈 선택 컨트롤 패널
    st.subheader("🎯 새로운 문제 출제")
    col_diff, col_btn = st.columns([3, 1])
    
    with col_diff:
        st.selectbox(
            "난이도 선택",
            ["랜덤", "입문", "중급", "고급"],
            key="quiz_difficulty",
            label_visibility="collapsed",
        )
    with col_btn:
        if st.button("🎯 퀴즈 시작하기", use_container_width=True, type="secondary"):
            raw_diff = st.session_state.get("quiz_difficulty", "랜덤")
            difficulty = None if raw_diff == "랜덤" else raw_diff
            
            with st.spinner("🎲 새로운 문제 생성 중..."):
                try:
                    q_data, _ = quiz_module.get_formatted_question(difficulty=difficulty)
                    st.session_state["quiz_state"] = q_data
                    st.session_state["quiz_answer"] = ""
                    st.session_state["quiz_feedback"] = None
                except Exception as e:
                    st.error(f"문제를 가져오는 중 오류가 발생했습니다: {e}")
            st.rerun()

    st.divider()

    # 활성화된 퀴즈가 있는 경우
    if st.session_state.get("quiz_state"):
        q_data = st.session_state["quiz_state"]
        
        st.subheader(f"📋 {q_data['title']}")
        st.markdown(f"**난이도**: `{q_data['difficulty']}` | **사례 ID**: `{q_data['case_id']}`")
        
        # 1. 물건 정보
        prop = q_data["property"]
        st.markdown(textwrap.dedent(f"""
        <div style="background-color: #0F172A; padding: 1.25rem; border-radius: 12px; border: 1px solid #1E293B; margin-bottom: 1.5rem;">
            <span style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC;">🏠 실물 물건 정보</span><br>
            <div style="margin-top: 8px; font-size: 0.9rem; line-height: 1.6; color: #94A3B8;">
                📍 <strong>소재지</strong>: {prop['location']}<br>
                🏢 <strong>용도</strong>: {prop['type']} | 📐 <strong>면적</strong>: {prop['area_m2']}㎡<br>
                💰 <strong>감정평가액</strong>: <span style="color: #3B82F6; font-weight: 600;">{prop['appraisal_value']:,}원</span> | 📉 <strong>최저매각가격</strong>: <span style="color: #F87171; font-weight: 600;">{prop['minimum_bid_price']:,}원</span>
            </div>
        </div>
        """), unsafe_allow_html=True)

        # 2. 등기부 현황 (을구)
        st.markdown("##### 📜 등기사항전부증명서 (을구 순위 목록)")
        registry_entries = q_data["registry"]["entries"]
        
        html_reg = textwrap.dedent("""
        <table class="premium-table">
            <thead>
                <tr>
                    <th style="width: 15%">접수일자</th>
                    <th style="width: 15%">등기목적</th>
                    <th style="width: 30%">권리자 및 채권액</th>
                    <th style="width: 40%">기타 내용</th>
                </tr>
            </thead>
            <tbody>
        """)
        for entry in registry_entries:
            amt = f" ({entry['amount']:,}원)" if "amount" in entry else ""
            details = entry.get("details", "-")
            html_reg += textwrap.dedent(f"""
                <tr>
                    <td>{entry['date']}</td>
                    <td><span style="background-color: #1E293B; color: #F8FAFC; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; border: 1px solid #334155;">{entry['type']}</span></td>
                    <td><strong>{entry['holder']}</strong>{amt}</td>
                    <td><span style="color: #94A3B8; font-size: 0.85em;">{details}</span></td>
                </tr>
            """)
        html_reg += "</tbody></table>"
        st.markdown(html_reg, unsafe_allow_html=True)
        
        # 3. 임차인 현황
        st.markdown("##### 🏠 임차인 점유 및 보증금 현황")
        tenants = q_data.get("tenants", [])
        if tenants:
            html_ten = textwrap.dedent("""
            <table class="premium-table">
                <thead>
                    <tr>
                        <th style="width: 20%">임차인명 (점유부분)</th>
                        <th style="width: 25%">전입신고일 (대항요건)</th>
                        <th style="width: 25%">확정일자</th>
                        <th style="width: 30%">보증금 / 차임(월세)</th>
                    </tr>
                </thead>
                <tbody>
            """)
            for t in tenants:
                fixed = t.get("fixed_date") or "-"
                dep = f"{t['deposit']:,}원"
                rent = f" / {t['monthly_rent']:,}원" if t.get("monthly_rent") else ""
                html_ten += textwrap.dedent(f"""
                    <tr>
                        <td><strong>{t['name']}</strong></td>
                        <td>{t['registration_date']}</td>
                        <td>{fixed}</td>
                        <td><span style="color: #2b6cb0; font-weight: 500;">{dep}{rent}</span></td>
                    </tr>
                """)
            html_ten += "</tbody></table>"
            st.markdown(html_ten, unsafe_allow_html=True)
        else:
            st.info("조사된 임차인 내역이 없습니다. (현재 채무자/소유자 점유 추정)")

        # 4. 특수 권리 주장 (있는 경우에만 표시)
        special = q_data.get("special_claims", [])
        if special:
            st.markdown("##### ⚠️ 특수 권리 현황")
            for sc in special:
                st.markdown(textwrap.dedent(f"""
                <div style="background-color: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 15px; margin-bottom: 10px;">
                    <span style="color: #F87171; font-weight: 700;">[특수권리] {sc['type']}</span> | 주장인: <strong>{sc['claimant']}</strong> | 주장금액: <strong>{sc['amount']:,}원</strong><br>
                    <small style="color: #94A3B8;">설명: {sc['details']}</small>
                </div>
                """), unsafe_allow_html=True)

        # 5. 분석 과제 공지
        st.markdown(textwrap.dedent(f"""
        <div style="background-color: rgba(59, 130, 246, 0.05); border: 1px solid #1E293B; border-left: 5px solid #3B82F6; border-radius: 8px; padding: 1rem; margin: 1.5rem 0;">
            <strong style="color: #60A5FA; font-size: 1rem;">❓ 권리분석 미션</strong><br>
            <span style="font-size: 0.95rem; line-height: 1.6; color: #E2E8F0;">{q_data['question']}</span>
        </div>
        """), unsafe_allow_html=True)

        # 6. 답안 작성
        st.subheader("✍️ 내 답안 작성하기")
        st.caption("답안에는 다음 내용을 포함해 주세요: 1) 말소기준권리 후보와 결정일자 2) 임차인의 대항력 여부 3) 인수/소멸 권리 4) 최종 입찰 시 리스크 위험도")
        
        user_answer = st.text_area(
            "이곳에 답안을 작성한 뒤 채점하기 버튼을 눌러주세요.",
            height=220,
            placeholder="예시:\n1. 말소기준권리는 2024년 2월 1일 을구 2번 근저당권(국민은행)입니다.\n2. 임차인 홍길동은 2024년 1월 15일 전입하여 말소기준권리보다 전입일이 빠르므로 대항력이 있습니다.\n3. 따라서 낙찰자가 임차보증금 1억 원을 인수해야 합니다.\n4. 리스크는 보통 수준이나 인수금액만큼 감가가 필요합니다.",
            key="user_quiz_answer_text",
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            grade_btn = st.button("📝 채점하기", type="primary", use_container_width=True)
        with col2:
            if st.button("🔄 다른 문제", use_container_width=False):
                st.session_state["quiz_state"] = None
                st.session_state["quiz_feedback"] = None
                st.rerun()

        # 채점 로직
        if grade_btn:
            if not user_answer.strip():
                st.warning("답안을 먼저 입력하신 후 채점하기를 눌러주세요.")
            else:
                with st.spinner("🤖 AI 교사가 정답안과 비교하여 채점 중입니다..."):
                    try:
                        grade_result = quiz_module.grade(
                            case_id=q_data["case_id"],
                            user_answer=user_answer,
                        )
                        st.session_state["quiz_feedback"] = grade_result["feedback"]
                    except Exception as e:
                        st.error(f"채점 중 오류가 발생했습니다: {e}")
                st.rerun()

        # 채점 결과 출력
        if st.session_state.get("quiz_feedback"):
            st.success("🎉 채점이 완료되었습니다! 아래 피드백을 확인하세요.")
            st.markdown(textwrap.dedent("""
            <div style="background-color: #0F172A; border: 1px solid #1E293B; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);">
                <h4 style="margin-top:0; color:#F8FAFC; border-bottom: 2px solid #1E293B; padding-bottom: 8px;">🎓 AI 튜터의 모의고사 피드백</h4>
            </div>
            """), unsafe_allow_html=True)
            st.markdown(st.session_state["quiz_feedback"])
            
            if st.button("✅ 피드백 확인 완료 (문제 닫기)", use_container_width=True):
                st.session_state["quiz_state"] = None
                st.session_state["quiz_feedback"] = None
                st.rerun()

    else:
        # 퀴즈 대기화면
        st.info("상단에서 난이도를 고르신 뒤 **[🎯 퀴즈 시작하기]** 버튼을 클릭하시면 모의 명세서 분석이 시작됩니다.")

    render_footer()
