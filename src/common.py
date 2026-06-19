"""
src/common.py — 공통 레이아웃 및 헬퍼 함수

모든 멀티페이지에서 사용될 공통 로직, 스타일(CSS), 그리고 유효성 검사를 제공합니다.
"""

from __future__ import annotations

import os
import streamlit as st
import config

def secrets_bridge():
    """Streamlit Cloud Secrets를 로컬 환경변수로 동기화합니다."""
    try:
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER", "EMBEDDING_PROVIDER"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
    except Exception:
        pass

def init_page(title: str, icon: str):
    """페이지 초기 설정 및 글로벌 프리미엄 테마 CSS를 적용합니다."""
    secrets_bridge()
    
    # page_config 적용 (이미 설정된 경우 경고 발생 방지를 위해 try-except 처리)
    try:
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&display=swap');
        
        /* 왼쪽 사이드바 기본 네비게이션 리스트 완전히 감추기 */
        [data-testid="sidebar-nav-container"], [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* 폰트 설정 */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Pretendard', sans-serif !important;
        }
        
        /* 그라데이션 히어로 배너 */
        .hero-container {
            background: linear-gradient(to bottom right, #0F172A, #0F172A, rgba(30, 58, 138, 0.3));
            padding: 2.5rem 2rem;
            border-radius: 16px;
            color: #F8FAFC;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            border: 1px solid #1E293B;
            border-left: 6px solid #10B981;
        }
        
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #FFFFFF, #E2E8F0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hero-subtitle {
            font-size: 1.05rem;
            font-weight: 300;
            color: #94A3B8;
            line-height: 1.5;
        }
        
        /* 홈페이지형 퀵 메뉴 카드 */
        .card-link {
            text-decoration: none !important;
            color: inherit !important;
        }
        .card-container {
            background-color: #0F172A;
            padding: 1.8rem;
            border-radius: 16px;
            border: 1px solid #1E293B;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin-bottom: 1rem;
            min-height: 180px;
        }
        .card-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5), 0 10px 10px -5px rgba(0,0,0,0.4);
            border-color: #334155;
        }
        .card-icon {
            font-size: 2rem;
            margin-bottom: 0.8rem;
        }
        .card-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 0.5rem;
        }
        .card-desc {
            font-size: 0.9rem;
            color: #94A3B8;
            line-height: 1.6;
        }
        
        /* 에이전트 배지 스타일링 */
        .agent-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        .badge-procedure {
            background-color: rgba(59, 130, 246, 0.1);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        .badge-tutor {
            background-color: rgba(16, 185, 129, 0.1);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .badge-quiz {
            background-color: rgba(239, 68, 68, 0.1);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        
        /* 디스클레이머 */
        .disclaimer {
            background-color: rgba(245, 158, 11, 0.05);
            border-left: 5px solid #F59E0B;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #F59E0B;
            line-height: 1.6;
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-left: 5px solid #F59E0B;
        }
        
        /* 하단 푸터 */
        .custom-footer {
            text-align: center;
            padding: 2rem 0;
            margin-top: 4rem;
            font-size: 0.8rem;
            color: #64748B;
            border-top: 1px solid #1E293B;
        }
        
        /* 테이블 프리미엄 스타일 */
        .premium-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background-color: #0F172A;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #1E293B;
        }
        .premium-table th {
            background-color: #020617;
            color: #94A3B8;
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 2px solid #1E293B;
            text-align: left;
        }
        .premium-table td {
            padding: 12px 16px;
            border-bottom: 1px solid #1E293B;
            color: #E2E8F0;
        }
        .premium-table tr:hover {
            background-color: #1E293B;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #020617;
        }
        ::-webkit-scrollbar-thumb {
            background: #1E293B;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
    </style>
    """, unsafe_allow_html=True)

def ensure_db():
    """ChromaDB 로컬 디렉터리가 없으면 자동으로 빌드를 작동시킵니다."""
    if not config.CHROMA_DB_DIR.exists():
        with st.spinner("📦 RAG용 지식베이스(ChromaDB)를 자동 구축하고 있습니다. 최초 1회 실행이며 약 1분 소요됩니다..."):
            from ingest import run_ingest
            run_ingest(dry_run=False)
        st.success("✅ 지식베이스 구축 완료!")
        st.rerun()

def check_api_key():
    """필수 API 키 입력 상태를 유효성 검증합니다."""
    if config.LLM_PROVIDER == "openai" and not config.OPENAI_API_KEY:
        st.error(
            "🔑 **OpenAI API Key 미설정 오류**\n\n"
            "프로젝트 루트의 `.env` 파일에 `OPENAI_API_KEY=your-key`를 설정해 주시거나, "
            "Streamlit Cloud 배포의 경우 APP 설정 내 Secrets에 환경변수 키를 입력해 주세요."
        )
        st.stop()
    elif config.LLM_PROVIDER == "anthropic" and not config.ANTHROPIC_API_KEY:
        st.error(
            "🔑 **Anthropic API Key 미설정 오류**\n\n"
            "프로젝트 루트의 `.env` 파일에 `ANTHROPIC_API_KEY=your-key`를 설정해 주세요."
        )
        st.stop()

def get_agent_badge(route: str, agent_name: str) -> str:
    """답변 창에 노출되는 에이전트 전용 HTML 배지를 빌드합니다."""
    badge_class = {
        "procedure": "badge-procedure",
        "tutor": "badge-tutor",
        "quiz": "badge-quiz",
    }.get(route, "badge-tutor")
    emoji = {"procedure": "📋", "tutor": "📚", "quiz": "📝"}.get(route, "🤖")
    return f'<span class="agent-badge {badge_class}">{emoji} {agent_name}</span>'

def render_footer():
    """하단 공통 디스클레이머 푸터를 렌더링합니다."""
    st.markdown(
        '<div class="custom-footer">'
        '🏛️ **부동산 경매 AI 튜터 플랫폼**<br>'
        '본 서비스는 법원경매 지식을 가르치고 모의 권리분석을 연습하는 교육 목적으로 제작되었습니다. '
        '실제 부동산 입찰 전에는 반드시 전문가의 조언 및 확인 절차를 거치시기 바라며, 투자 행위에 대한 일체의 책임을 지지 않습니다.'
        '</div>',
        unsafe_allow_html=True
    )

def render_top_menu():
    """상단 가로형 네비게이션 메뉴바를 렌더링합니다."""
    st.markdown("""
    <style>
        /* 각 버튼 간의 간격 조정 및 호버 스타일링 */
        .stPageLink > a {
            font-weight: 600 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease-in-out !important;
            padding: 8px 12px !important;
        }
        .stPageLink > a:hover {
            color: #48bb78 !important;
            border: 1px solid #48bb78 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 5개 열을 정의하여 메뉴 버튼들을 가로로 나열
    cols = st.columns([1.5, 1.2, 1.2, 1.2, 3.1])
    with cols[0]:
        st.page_link("app.py", label="🏛️ 경매 AI 튜터 홈", use_container_width=True)
    with cols[1]:
        st.page_link("pages/1_📋_경매_절차_안내.py", label="📋 경매 절차 안내", use_container_width=True)
    with cols[2]:
        st.page_link("pages/2_📚_권리분석_튜터.py", label="📚 권리분석 튜터", use_container_width=True)
    with cols[3]:
        st.page_link("pages/3_📝_사례_퀴즈_연습.py", label="📝 사례 퀴즈 연습", use_container_width=True)
