# -*- coding: utf-8 -*-
"""
app.py — 메인 홈페이지 랜딩 화면

부동산 경매 교육 멀티에이전트 RAG 플랫폼의 중앙 포털입니다.
각각의 개별 에이전트 페이지로 안내하고, 실시간 용어 사전 검색 및 전체 절차 흐름도를 보여줍니다.
"""

from __future__ import annotations

import streamlit as st
import config
import json
from src.common import init_page, check_api_key, ensure_db, render_footer, render_top_menu

def main():
    # 페이지 초기 설정 및 공통 스타일 주입
    init_page("부동산 경매 AI 튜터 | 홈", "🏛️")
    render_top_menu()
    check_api_key()
    ensure_db()

    # 1. Hero Section (그라데이션 타이틀)
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🏛️ 부동산 경매 AI 교육 플랫폼</div>
        <div class="hero-subtitle">
            어렵고 위험한 법원경매 권리분석, 인공지능 RAG 멀티에이전트와 함께 체계적으로 정복하세요.<br>
            경매 절차 Q&A부터 핵심 권리분석 개념 학습, 가상 물건 사례 퀴즈 모의고사까지 한 번에 지원합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 3대 기능 메뉴 카드 배치 (HTML + st.page_link 연계)
    st.subheader("🚀 핵심 서비스 메뉴 바로가기")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon">📋</div>
            <div class="card-title">1. 경매 절차 안내</div>
            <div class="card-desc">경매신청부터 입찰, 대금 납부, 배당 순서까지 9단계의 흐름도와 관련 법령 조문을 챗봇과 공부합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/경매_절차_안내.py", label="👉 경매 절차 안내봇 이동", use_container_width=True)

    with col2:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon">📚</div>
            <div class="card-title">2. 권리분석 튜터</div>
            <div class="card-desc">가장 위험하고 손실이 빈번한 말소기준권리 찾기, 임차인의 대항력 유무 판단 요건을 집중 학습합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/권리분석_튜터.py", label="👉 권리분석 튜터봇 이동", use_container_width=True)

    with col3:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon">📝</div>
            <div class="card-title">3. 사례 퀴즈 연습</div>
            <div class="card-desc">가상 등기부와 임차인 명세서를 분석하고 직접 리스크 답안을 작성하여 AI 맞춤 채점 피드백을 받습니다.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/사례_퀴즈_연습.py", label="👉 사례 및 퀴즈 연습실 이동", use_container_width=True)

    # 3. 실시간 경매 용어 사전 검색 (홈페이지 상호작용성 강화)
    st.divider()
    st.subheader("🔍 실시간 경매 용어 사전 검색")
    st.caption("궁금한 경매 전문 용어(예: 대항력, 말소기준권리, 배당요구종기 등)를 입력해보세요. 용어집에서 즉석 검색합니다.")

    try:
        if config.GLOSSARY_PATH.exists():
            with open(config.GLOSSARY_PATH, encoding="utf-8") as f:
                glossary_data = json.load(f)
            
            search_query = st.text_input(
                "용어 검색창",
                placeholder="검색어를 입력하고 Enter를 누르세요 (예: 유치권, 배당요구)...",
                label_visibility="collapsed",
                key="home_glossary_search"
            )

            if search_query.strip():
                query = search_query.strip().lower()
                matches = [
                    item for item in glossary_data
                    if query in item["term"].lower() or query in item["definition"].lower()
                ]
                
                if matches:
                    st.success(f"총 {len(matches)}개의 관련 용어를 찾았습니다:")
                    for match in matches:
                        st.markdown(f"""
                        <div style="background-color: #f7fafc; padding: 1.25rem; border-radius: 12px; border-left: 5px solid #319795; margin-bottom: 0.75rem; border: 1px solid #edf2f7; border-left: 5px solid #319795;">
                            <strong style="color: #2c5282; font-size: 1.15rem;">📙 {match['term']}</strong><br>
                            <div style="margin-top: 6px; font-size: 0.95rem; color: #2d3748; line-height: 1.6;">{match['definition']}</div>
                            <small style="color: #718096; margin-top: 6px; display: block;">⛓️ 관련 조문 근거: {match.get('related_law', '정보 없음')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("검색 조건에 맞는 용어가 없습니다. 다른 단어로 검색해 보세요.")
        else:
            st.warning("용어집 파일(glossary.json)을 로드할 수 없습니다.")
    except Exception as e:
        st.error(f"용어 사전 검색 엔진 로드 실패: {e}")

    # 4. 경매 절차 9단계 일람
    st.divider()
    st.subheader("🛤️ 법원경매 핵심 9단계 흐름 요약")
    st.markdown("전체 경매는 아래의 법적 프로세스 단계에 따라 순차적으로 진행됩니다. (각 페이지의 상세 탭을 통해 법률 근거를 보실 수 있습니다)")
    
    flow_cols = st.columns(9)
    steps_flow = [
        ("1. 경매 신청", "채권자의 신청"),
        ("2. 개시 결정", "개시 등기/압류"),
        ("3. 배당 공고", "배당요구 종기"),
        ("4. 현황 조사", "집행관 임대조사"),
        ("5. 명세 작성", "매각명세서 작성"),
        ("6. 매각 기일", "입찰 및 최고가"),
        ("7. 매각 허가", "법원 적법 심사"),
        ("8. 대금 납부", "소유권 취득"),
        ("9. 배당/인도", "채권배당/명도")
    ]
    for idx, (title, desc) in enumerate(steps_flow):
        with flow_cols[idx]:
            st.markdown(f"""
            <div style="background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 6px; text-align: center; min-height: 110px; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                <span style="font-size: 0.9rem; font-weight: 700; color: #2d3748; display: block;">{title}</span>
                <span style="font-size: 0.75rem; color: #718096; margin-top: 6px; display: block; line-height: 1.3;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    # 5. 시스템 정보 대시보드
    st.divider()
    st.subheader("⚙️ 플랫폼 작동 정보")
    
    db_exists = config.CHROMA_DB_DIR.exists()
    db_badge = "Active & Connected ✅" if db_exists else "Not Configured ❌"
    
    dash_cols = st.columns(4)
    with dash_cols[0]:
        st.metric("LLM Provider", config.LLM_PROVIDER.upper())
    with dash_cols[1]:
        st.metric("LLM Active Model", config.OPENAI_MODEL if config.LLM_PROVIDER == 'openai' else config.ANTHROPIC_MODEL)
    with dash_cols[2]:
        st.metric("Embedding Provider", config.EMBEDDING_PROVIDER.upper())
    with dash_cols[3]:
        st.metric("Vector DB Status", db_badge)

    # 공통 푸터
    render_footer()

if __name__ == "__main__":
    main()
