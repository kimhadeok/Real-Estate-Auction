# -*- coding: utf-8 -*-
"""
src/price_oracle/ui.py — AI 입찰가 예측 (Price Oracle) UI 렌더러

성능 최적화 포인트:
  1. session_state로 분석 결과를 캐싱 → 동일 입력에 대한 중복 계산 방지
  2. @st.cache_resource 로 엔진 인스턴스를 재사용
  3. common.py CSS 캐싱과 연계하여 rerun 시 렌더링 속도 향상
"""

from __future__ import annotations

import hashlib
import json

import streamlit as st
from src.core.common import init_page, check_api_key, render_top_menu, render_footer
from src.price_oracle.engine import PriceOracleEngine

# ──────────────────────────────────────────
# 엔진 캐싱 — @st.cache_resource 로 세션 전체에서 단일 인스턴스 재사용
# ──────────────────────────────────────────
@st.cache_resource
def _get_engine() -> PriceOracleEngine:
    """PriceOracleEngine 인스턴스를 세션 전체에서 1회만 생성합니다."""
    return PriceOracleEngine()


# ──────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────
PROPERTY_TYPES = [
    "아파트",
    "다세대·빌라",
    "오피스텔",
    "상가",
    "토지",
    "단독·다가구주택",
]

COURTS = [
    "서울중앙지법",
    "서울동부지법",
    "서울서부지법",
    "서울남부지법",
    "서울북부지법",
    "수원지법",
    "인천지법",
    "의정부지법",
    "춘천지법",
    "대전지법",
    "청주지법",
    "대구지법",
    "부산지법",
    "울산지법",
    "창원지법",
    "광주지법",
    "전주지법",
    "제주지법",
]


# ──────────────────────────────────────────
# 입력값 해시 헬퍼 — 동일 입력 중복 계산 방지용
# ──────────────────────────────────────────
def _inputs_hash(inputs: dict) -> str:
    """입력값 딕셔너리를 SHA-1 해시 문자열로 변환합니다."""
    serialized = json.dumps(inputs, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(serialized.encode()).hexdigest()


# ──────────────────────────────────────────
# 입력 섹션 렌더러
# ──────────────────────────────────────────
def _render_input_section() -> dict | None:
    """입력 폼을 렌더링하고 제출 시 입력값 딕셔너리를 반환합니다."""

    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">💰 AI 입찰가 예측</div>
            <div class="hero-subtitle">
                <strong>Price Oracle</strong> — 목표 수익률과 비용을 역산하여 최적 입찰 마지노선을 제안합니다.<br>
                법원별 낙찰가율 통계 기반으로 낙찰 확률 구간과 예상 경쟁자 수를 시뮬레이션합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="disclaimer">⚠️ 본 예측 결과는 <strong>교육·참고용</strong>이며, '
        "실제 부동산 입찰 전에는 반드시 전문가(경매 전문 변호사·감정평가사)의 확인이 필요합니다. "
        "AI 예측 수치에만 의존한 투자 결과에 대한 책임을 지지 않습니다.</div>",
        unsafe_allow_html=True,
    )

    with st.form(key="price_oracle_form"):
        st.subheader("📋 물건 기본 정보")
        col1, col2, col3 = st.columns(3)
        with col1:
            property_type = st.selectbox("물건 유형", PROPERTY_TYPES, index=0)
        with col2:
            court = st.selectbox("소재 법원", COURTS, index=0)
        with col3:
            foreclosure_count = st.number_input(
                "유찰 횟수", min_value=0, max_value=10, value=1, step=1,
                help="유찰 횟수가 많을수록 최저가가 낮아집니다."
            )

        st.divider()
        st.subheader("💵 가격 정보")
        col4, col5 = st.columns(2)
        with col4:
            appraisal_price = st.number_input(
                "감정가 (만원)", min_value=1_000, max_value=500_000,
                value=50_000, step=1_000,
                help="법원 감정 기준 금액 (예: 50000 = 5억 원)"
            )
        with col5:
            min_price = st.number_input(
                "현재 최저가 (만원)", min_value=1_000, max_value=500_000,
                value=40_000, step=1_000,
                help="유찰 횟수가 반영된 현재 최저 입찰가"
            )

        st.divider()
        st.subheader("🎯 목표 수익 & 대출 조건")
        col6, col7 = st.columns(2)
        with col6:
            target_profit = st.number_input(
                "목표 세후 순수익 (만원)", min_value=0, max_value=100_000,
                value=3_000, step=500,
                help="최종적으로 손에 쥐고 싶은 순수익 (예: 3000 = 3천만 원)"
            )
        with col7:
            loan_ratio = st.slider(
                "대출 비율 (%)", min_value=0, max_value=80, value=60, step=5,
                help="LTV 기준 대출 비중"
            )

        col8, col9 = st.columns(2)
        with col8:
            interest_rate = st.slider(
                "대출 금리 (연, %)", min_value=2.0, max_value=10.0, value=4.5, step=0.1,
                help="주택담보대출 연이율"
            )
        with col9:
            holding_months = st.number_input(
                "예상 보유 기간 (개월)", min_value=1, max_value=120, value=12, step=1,
                help="대출 이자 계산 기준 보유 기간"
            )

        st.divider()
        st.subheader("🔧 추가 비용 추정 (선택)")
        col10, col11, col12 = st.columns(3)
        with col10:
            legal_cost = st.number_input(
                "법무비 (만원)", min_value=0, max_value=5_000, value=150, step=50,
                help="법무사·등기 비용 예상액"
            )
        with col11:
            eviction_cost = st.number_input(
                "명도비 (만원)", min_value=0, max_value=10_000, value=300, step=100,
                help="점유자 이사비 및 명도 협상 예상 비용"
            )
        with col12:
            renovation_cost = st.number_input(
                "인테리어비 (만원)", min_value=0, max_value=50_000, value=500, step=100,
                help="수리·인테리어 예상 비용"
            )

        submitted = st.form_submit_button(
            "🔮 입찰가 예측 분석 실행", use_container_width=True, type="primary"
        )

    if submitted:
        return {
            "property_type": property_type,
            "court": court,
            "foreclosure_count": foreclosure_count,
            "appraisal_price": appraisal_price,        # 만원
            "min_price": min_price,                    # 만원
            "target_profit": target_profit,            # 만원
            "loan_ratio": loan_ratio / 100,            # 소수
            "interest_rate": interest_rate / 100,      # 소수 (연이율)
            "holding_months": holding_months,
            "legal_cost": legal_cost,                  # 만원
            "eviction_cost": eviction_cost,            # 만원
            "renovation_cost": renovation_cost,        # 만원
        }
    return None


# ──────────────────────────────────────────
# 결과 섹션 렌더러
# ──────────────────────────────────────────
def _render_result_section(result: dict) -> None:
    """분석 결과를 시각적으로 렌더링합니다."""

    st.markdown("---")
    st.subheader("📊 Price Oracle 분석 결과")

    # ── 최대 입찰 마지노선 강조 표시
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(
            label="💡 최대 입찰 마지노선",
            value=f"{result['max_bid']:,.0f} 만원",
            delta=f"감정가 대비 {result['bid_ratio']:.1f}%",
        )
    with col_b:
        st.metric(
            label="👥 예상 경쟁자 수",
            value=f"{result['competitor_min']}~{result['competitor_max']} 명",
            delta="해당 법원 유사 물건 기준",
        )
    with col_c:
        st.metric(
            label="🎯 낙찰 성공 확률 (마지노선 기준)",
            value=f"{result['success_prob']:.0f}%",
        )

    # ── 비용 역산 내역 테이블
    st.markdown("#### 📋 비용 역산 내역")
    cost_data = result["cost_breakdown"]
    st.markdown(
        f"""
        <table class="premium-table">
            <thead>
                <tr>
                    <th>비용 항목</th>
                    <th>금액 (만원)</th>
                    <th>산출 기준</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>취득세 + 등록세</td><td style="text-align:right"><strong>{cost_data['acquisition_tax']:,.0f}</strong></td><td>{cost_data['acquisition_tax_note']}</td></tr>
                <tr><td>법무비</td><td style="text-align:right"><strong>{cost_data['legal_cost']:,.0f}</strong></td><td>입력값</td></tr>
                <tr><td>명도비</td><td style="text-align:right"><strong>{cost_data['eviction_cost']:,.0f}</strong></td><td>입력값</td></tr>
                <tr><td>인테리어비</td><td style="text-align:right"><strong>{cost_data['renovation_cost']:,.0f}</strong></td><td>입력값</td></tr>
                <tr><td>대출 이자 (보유기간)</td><td style="text-align:right"><strong>{cost_data['interest_cost']:,.0f}</strong></td><td>{cost_data['interest_note']}</td></tr>
                <tr style="background:#f0fdf4"><td><strong>총 부대비용</strong></td><td style="text-align:right"><strong>{cost_data['total_cost']:,.0f}</strong></td><td>—</td></tr>
                <tr style="background:#eff6ff"><td><strong>목표 순수익</strong></td><td style="text-align:right"><strong>{cost_data['target_profit']:,.0f}</strong></td><td>입력값</td></tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    # ── 낙찰 확률 분포 차트
    st.markdown("#### 📈 입찰가 구간별 낙찰 확률 분포")
    st.info(
        "💡 아래 차트는 해당 법원·물건 유형의 과거 낙찰가율 통계를 기반으로 시뮬레이션된 "
        "교육용 예측치입니다. 실제 낙찰 결과와 다를 수 있습니다."
    )
    chart_data = result["prob_chart_data"]
    st.bar_chart(chart_data, x="입찰가 구간 (만원)", y="낙찰 확률 (%)", color="#0d9488")

    # ── AI 전략 코멘트
    st.markdown("#### 🤖 AI 입찰 전략 코멘트")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#f0fdf4,#eff6ff);
                    border-left:5px solid #0d9488; border-radius:12px;
                    padding:1.2rem 1.5rem; font-size:1rem; line-height:1.7; color:#0f172a;">
            {result['ai_comment']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="disclaimer" style="margin-top:1.5rem;">⚠️ 위 결과는 <strong>교육·참고 목적</strong>의 시뮬레이션이며, '
        "실제 낙찰 결과를 보장하지 않습니다. 실제 입찰 전 경매 전문가 상담을 권장합니다.</div>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────
# 메인 렌더러
# ──────────────────────────────────────────
def render_page() -> None:
    """AI 입찰가 예측 페이지 전체를 렌더링합니다."""
    init_page("AI 입찰가 예측 — 경매 AI 튜터", "💰")
    check_api_key()
    render_top_menu()

    inputs = _render_input_section()

    # ── 결과 캐싱 로직 ─────────────────────────────────────────────────
    # 폼 제출 시: 입력값 해시를 비교하여 동일 입력이면 저장된 결과 재사용.
    # 다른 입력이면 새로 계산 후 session_state에 저장.
    # 폼 미제출(페이지 최초 진입·rerun) 시: 이전 결과가 있으면 그대로 표시.
    if inputs is not None:
        new_hash = _inputs_hash(inputs)
        if st.session_state.get("_oracle_hash") != new_hash:
            with st.spinner("🔮 Price Oracle 분석 중... 낙찰가율 데이터와 비용을 계산하고 있습니다."):
                engine = _get_engine()
                result = engine.analyze(inputs)
            st.session_state["_oracle_result"] = result
            st.session_state["_oracle_hash"] = new_hash
        else:
            result = st.session_state["_oracle_result"]
        _render_result_section(result)

    elif st.session_state.get("_oracle_result") is not None:
        # 폼이 재렌더링되었지만 이전 분석 결과가 있는 경우 그대로 표시
        _render_result_section(st.session_state["_oracle_result"])

    render_footer()
