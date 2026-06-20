"""
src/common.py — 공통 레이아웃 및 헬퍼 함수

모든 멀티페이지에서 사용될 공통 로직, 스타일(CSS), 그리고 유효성 검사를 제공합니다.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import os
import streamlit as st
import config

def is_app2_mode() -> bool:
    """sys.argv에 app2.py가 인자로 전달되었는지 확인하여 구동 모드를 감지합니다."""
    import sys
    return any("app2.py" in arg for arg in sys.argv)

def secrets_bridge():
    """Streamlit Cloud Secrets를 로컬 환경변수로 동기화합니다."""
    try:
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER", "EMBEDDING_PROVIDER"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
    except Exception:
        pass

# ── 전역 CSS 문자열 (모듈 로드 시 1회 구성) ──────────────────────────────────
# Tailwind CDN(~350KB JS)은 커스텀 CSS와 기능이 중복되므로 제거했습니다.
# Google Fonts는 아래 <style> @import로 처리합니다.
_GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    :root {
        --primary: #2563eb;
        --secondary: #0d9488;
        --accent: #fb7185;
        --warning: #f59e0b;
        --dark: #0f172a;
        --light: #f8fafc;
        --success: #10B981;
    }

    /* GNB 가로정렬 강제 조정 및 최상위 컴포넌트 덮어쓰기 */
    html body [data-testid="stAppViewContainer"] [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        background-color: #ffffff !important;
        padding: 16px 20px !important;
        border-radius: 24px !important;
        box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.05), 0 4px 12px -2px rgba(0, 0, 0, 0.02) !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 2.5rem !important;
    }
    
    /* 3x GNB 텍스트 크기 확대 오버라이드 */
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] *,
    html body [data-testid="stAppViewContainer"] .stPageLink *,
    .stPageLink * {
        font-size: 1.58rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.5px !important;
        white-space: nowrap !important;
        line-height: 1.1 !important;
    }
    
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a,
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button,
    .stPageLink > a,
    .stPageLink > button {
        border-radius: 14px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        padding: 10px 18px !important;
        border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04) !important;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-decoration: none !important;
    }
    
    /* 호버 시 세련된 그라데이션 및 입체 피드백 */
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a:hover,
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button:hover,
    .stPageLink > a:hover,
    .stPageLink > button:hover {
        color: #0d9488 !important;
        border-color: #0d9488 !important;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.04) 0%, rgba(13, 148, 136, 0.06) 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 30px rgba(13, 148, 136, 0.14) !important;
    }
    
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a:hover *,
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button:hover *,
    .stPageLink > a:hover *,
    .stPageLink > button:hover * {
        color: #0d9488 !important;
    }

    /* 활성 포커스 해제 및 클릭 액션 */
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a:focus,
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a:active,
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button:focus,
    html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button:active,
    .stPageLink > a:focus,
    .stPageLink > button:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.2) !important;
    }

    /* 반응형 GNB 텍스트 스케일 다운 */
    @media (max-width: 1600px) {
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] *,
        html body [data-testid="stAppViewContainer"] .stPageLink *,
        .stPageLink * {
            font-size: 1.3rem !important;
            letter-spacing: -0.4px !important;
        }
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a,
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button,
        .stPageLink > a,
        .stPageLink > button {
            padding: 8px 14px !important;
        }
    }
    @media (max-width: 1200px) {
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] *,
        html body [data-testid="stAppViewContainer"] .stPageLink *,
        .stPageLink * {
            font-size: 1.15rem !important;
            letter-spacing: -0.3px !important;
        }
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a,
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button,
        .stPageLink > a,
        .stPageLink > button {
            padding: 6px 12px !important;
        }
    }
    @media (max-width: 768px) {
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] *,
        html body [data-testid="stAppViewContainer"] .stPageLink *,
        .stPageLink * {
            font-size: 0.95rem !important;
            letter-spacing: -0.2px !important;
        }
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > a,
        html body [data-testid="stAppViewContainer"] [data-testid="stPageLink"] > button,
        .stPageLink > a,
        .stPageLink > button {
            padding: 5px 10px !important;
        }
    }

    /* 왼쪽 사이드바 기본 네비게이션 리스트 완전히 감추기 */
    [data-testid="sidebar-nav-container"], [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* 폰트 설정 */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Noto Sans KR', 'Inter', sans-serif !important;
    }
    
    /* 그라데이션 히어로 배너 */
    .hero-container {
        background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: #0f172a;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        border-left: 6px solid var(--secondary);
        position: relative;
        overflow: hidden;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 0.75rem;
        letter-spacing: -0.5px;
        background: linear-gradient(to right, #0f172a, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #475569;
        line-height: 1.6;
    }
    
    /* 홈페이지형 퀵 메뉴 카드 */
    .card-link {
        text-decoration: none !important;
        color: inherit !important;
    }
    .card-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 1rem;
        min-height: 190px;
    }
    .card-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border-color: var(--secondary);
    }
    .card-icon {
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
    }
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .card-desc {
        font-size: 0.95rem;
        color: #475569;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-procedure {
        background-color: rgba(37, 99, 235, 0.08);
        color: #1d4ed8;
        border: 1px solid rgba(37, 99, 235, 0.2);
    }
    .badge-tutor {
        background-color: rgba(13, 148, 136, 0.08);
        color: #0f766e;
        border: 1px solid rgba(13, 148, 136, 0.2);
    }
    .badge-quiz {
        background-color: rgba(225, 29, 72, 0.08);
        color: #be123c;
        border: 1px solid rgba(225, 29, 72, 0.2);
    }
    
    /* 디스클레이머 */
    .disclaimer {
        background-color: rgba(217, 119, 6, 0.04);
        border-left: 5px solid var(--warning);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
        font-size: 0.9rem;
        color: #b45309;
        line-height: 1.6;
        border: 1px solid rgba(217, 119, 6, 0.15);
    }
    
    /* 하단 푸터 */
    .custom-footer {
        text-align: center;
        padding: 2.5rem 0;
        margin-top: 4rem;
        font-size: 0.85rem;
        color: #64748B;
        border-top: 1px solid #e2e8f0;
    }
    
    /* 테이블 프리미엄 스타일 */
    .premium-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background-color: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    .premium-table th {
        background-color: #f1f5f9;
        color: #475569;
        font-weight: 600;
        padding: 12px 16px;
        border-bottom: 2px solid #e2e8f0;
        text-align: left;
    }
    .premium-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #e2e8f0;
        color: #0f172a;
    }
    .premium-table tr:hover {
        background-color: #f8fafc;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* 4단계 멀티에이전트 워크플로우 화살표 스타일 */
    .flow-arrow-horizontal {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        min-width: 20px;
    }
    @media (max-width: 992px) {
        .flow-arrow-horizontal {
            transform: rotate(90deg);
            margin: 0.5rem auto;
            min-height: 30px;
        }
    }
</style>
"""

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

    # ── CSS 주입 ─────────────────────────────────────────────────────
    # Streamlit은 페이지 이동 시 DOM을 완전히 새로 그립니다.
    # session_state는 유지되지만 이전에 주입한 CSS는 DOM에서 사라지므로,
    # 캐싱 없이 매 렌더링마다 주입합니다.
    # ※ Tailwind CDN(~350KB)은 이미 제거했으므로 순수 CSS(~8KB) 재주입
    #   비용은 미미하며, Google Fonts는 브라우저 캐시가 처리합니다.
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)



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
    import os
    
    # app.py 모드일 때 최초 진입 시 기존 .env에서 읽어왔을 수 있는 키를 강제 공백 리셋
    if not is_app2_mode() and "api_key_initialized" not in st.session_state:
        config.OPENAI_API_KEY = ""
        config.ANTHROPIC_API_KEY = ""
        if "OPENAI_API_KEY" in os.environ:
            os.environ["OPENAI_API_KEY"] = ""
        if "ANTHROPIC_API_KEY" in os.environ:
            os.environ["ANTHROPIC_API_KEY"] = ""
        st.session_state["api_key_initialized"] = True

    if is_app2_mode():
        # app2.py 모드: .env 설정만 로드
        if config.LLM_PROVIDER == "openai" and not config.OPENAI_API_KEY:
            st.error(
                "🔑 **OpenAI API Key 미설정 오류**\n\n"
                "프로젝트 루트의 `.env` 파일에 `OPENAI_API_KEY=your-key`를 설정해 주세요."
            )
            st.stop()
        elif config.LLM_PROVIDER == "anthropic" and not config.ANTHROPIC_API_KEY:
            st.error(
                "🔑 **Anthropic API Key 미설정 오류**\n\n"
                "프로젝트 루트의 `.env` 파일에 `ANTHROPIC_API_KEY=your-key`를 설정해 주세요."
            )
            st.stop()
    else:
        # app.py 모드: 화면 최상단 본문 입력 유도
        provider = config.LLM_PROVIDER
        active_key = config.OPENAI_API_KEY if provider == "openai" else config.ANTHROPIC_API_KEY
        
        # 1. API Key가 설정되지 않은 최초 단계
        if not active_key:
            st.warning(f"🔑 **{provider.upper()} API Key 미설정**")
            st.info("🏛️ 부동산 경매 AI 튜터 플랫폼 이용을 위해 아래에 API Key를 기입해 주시기 바랍니다.")
            
            with st.form("api_key_initial_form"):
                label = "OpenAI API Key 입력" if provider == "openai" else "Anthropic API Key 입력"
                ph = "sk-..." if provider == "openai" else "sk-ant-..."
                inline_key = st.text_input(label, value="", type="password", placeholder=ph)
                submit_key = st.form_submit_button("🔑 키 등록 및 활성화")
                
            if submit_key and inline_key.strip():
                user_key = inline_key.strip()
                if provider == "openai":
                    st.session_state["openai_api_key"] = user_key
                    config.OPENAI_API_KEY = user_key
                    os.environ["OPENAI_API_KEY"] = user_key
                elif provider == "anthropic":
                    st.session_state["anthropic_api_key"] = user_key
                    config.ANTHROPIC_API_KEY = user_key
                    os.environ["ANTHROPIC_API_KEY"] = user_key
                st.rerun()
                
            st.stop()
            
        # 2. API Key가 이미 설정되어 원활히 구동되는 단계 (GNB보다 위에 접이식 아코디언 제공)
        else:
            with st.expander(f"🔑 API Key 설정 및 재설정 (현재: {provider.upper()} 적용 중)", expanded=False):
                with st.form("api_key_reset_form"):
                    label = "새로운 OpenAI API Key 입력" if provider == "openai" else "새로운 Anthropic API Key 입력"
                    default_key = st.session_state.get("openai_api_key" if provider == "openai" else "anthropic_api_key", active_key)
                    new_key_input = st.text_input(label, value=default_key, type="password")
                    col_apply, _ = st.columns([1, 4])
                    with col_apply:
                        apply_btn = st.form_submit_button("🔄 변경 적용")
                        
                if apply_btn:
                    cleaned_key = new_key_input.strip()
                    if provider == "openai":
                        st.session_state["openai_api_key"] = cleaned_key
                        config.OPENAI_API_KEY = cleaned_key
                        os.environ["OPENAI_API_KEY"] = cleaned_key
                    elif provider == "anthropic":
                        st.session_state["anthropic_api_key"] = cleaned_key
                        config.ANTHROPIC_API_KEY = cleaned_key
                        os.environ["ANTHROPIC_API_KEY"] = cleaned_key
                    st.success("✅ API Key가 동적으로 업데이트되었습니다.")
                    st.rerun()

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
    
    # 7개 열의 너비를 재분배 — AI 입찰가 예측 메뉴 추가
    cols = st.columns([2.0, 2.0, 1.9, 1.9, 1.9, 2.1, 0.6])
    home_file = "app2.py" if is_app2_mode() else "app.py"
    with cols[0]:
        st.page_link(home_file, label="🏛️ HOME", use_container_width=True)
    with cols[1]:
        st.page_link("pages/auction_procedure.py", label="📋 경매 절차 안내", use_container_width=True)
    with cols[2]:
        st.page_link("pages/rights_analysis.py", label="📚 권리분석 튜터", use_container_width=True)
    with cols[3]:
        st.page_link("pages/case_quiz.py", label="📝 사례 퀴즈 연습", use_container_width=True)
    with cols[4]:
        st.page_link("pages/glossary.py", label="🔍 경매 용어 사전", use_container_width=True)
    with cols[5]:
        st.page_link("pages/bid_prediction.py", label="💰 AI 입찰가 예측", use_container_width=True)
