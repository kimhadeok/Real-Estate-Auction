# -*- coding: utf-8 -*-
"""
src/glossary/ui.py — 경매 용어 사전 UI 모듈

경매 전문 용어를 초성별로 탐색하고 키워드로 실시간 검색할 수 있는 사전 페이지입니다.
"""

from __future__ import annotations

import streamlit as st
import config
import json
from src.core.common import init_page, check_api_key, ensure_db, render_footer, render_top_menu

def get_chosung(word: str) -> str:
    if not word:
        return ""
    code = ord(word[0]) - 0xAC00
    if 0 <= code <= 11171:
        chosung_index = code // 588
        chosung_list = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        return chosung_list[chosung_index]
    return word[0].upper()

def render_page():
    # 페이지 초기화
    init_page("경매 용어 사전 | AI 튜터", "🔍")
    check_api_key()
    render_top_menu()
    ensure_db()

    # 그라데이션 타이틀 배너
    st.markdown("""<style>
.glossary-card {
    background-color: #ffffff !important;
    padding: 1.6rem;
    border-radius: 18px;
    border: 1px solid #f1f5f9 !important;
    border-left: 6px solid var(--secondary) !important;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03), 0 4px 6px -2px rgba(0,0,0,0.01) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.glossary-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.06), 0 10px 10px -5px rgba(0,0,0,0.02) !important;
    border-color: #cbd5e1 !important;
}
.glossary-term {
    color: #0f172a !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}
.glossary-definition {
    font-size: 0.96rem !important;
    color: #334155 !important;
    line-height: 1.8 !important;
    text-align: justify;
    margin-bottom: 14px;
}
.glossary-meta {
    padding-top: 12px;
    border-top: 1px dashed #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.82rem;
    color: #64748b;
}
.glossary-law {
    color: #1e293b;
    font-weight: 600;
}
.glossary-badge {
    background-color: rgba(13, 148, 136, 0.08) !important;
    color: #0f766e !important;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.78rem;
}
</style>
<div class="hero-container" style="border-left: 6px solid var(--secondary);">
    <div class="hero-title">🔍 경매 용어 사전</div>
    <div class="hero-subtitle">법원경매, 권리분석 등 어렵고 복잡한 부동산 경매 전문 용어를 쉽고 친절하게 정리해 드립니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        if config.GLOSSARY_PATH.exists():
            with open(config.GLOSSARY_PATH, encoding="utf-8") as f:
                glossary_data = json.load(f)
            
            # 용어 가나다 정렬
            glossary_data = sorted(glossary_data, key=lambda x: x["term"])
            
            # 검색창과 초성 필터 레이아웃
            search_query = st.text_input(
                "🔎 용어 실시간 검색",
                placeholder="검색할 용어 또는 단어를 입력하세요 (예: 대항력, 유치권 등)...",
            )
            
            # 초성 버튼 필터 목록
            st.write("##### 🔠 초성 필터 검색")
            chosungs = ['전체', 'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
            
            if "selected_chosung" not in st.session_state:
                st.session_state["selected_chosung"] = "전체"
                
            cols_chosung = st.columns(len(chosungs))
            for idx, ch in enumerate(chosungs):
                # 선택된 초성에 강조 스타일 적용
                btn_label = f"**{ch}**" if st.session_state["selected_chosung"] == ch else ch
                if cols_chosung[idx].button(btn_label, key=f"btn_ch_{ch}", use_container_width=True):
                    st.session_state["selected_chosung"] = ch
                    st.rerun()

            # 데이터 필터링
            filtered_data = glossary_data
            
            # 1. 텍스트 검색어 필터링
            if search_query.strip():
                query = search_query.strip().lower()
                filtered_data = [
                    item for item in filtered_data
                    if query in item["term"].lower() or query in item["definition"].lower()
                ]
            
            # 2. 초성 필터링 (선택되었고 '전체'가 아닌 경우)
            elif st.session_state["selected_chosung"] != "전체":
                target_ch = st.session_state["selected_chosung"]
                filtered_data = [
                    item for item in filtered_data
                    if get_chosung(item["term"]) == target_ch
                ]

            # 결과 리스트 렌더링
            st.divider()
            
            # 검색 기준 설명 표시
            if search_query.strip():
                st.caption(f"🔎 **'{search_query}'** 검색 결과: 총 {len(filtered_data)}건")
            elif st.session_state["selected_chosung"] != "전체":
                st.caption(f"🔠 초성 필터 **'{st.session_state['selected_chosung']}'** 검색 결과: 총 {len(filtered_data)}건")
            else:
                st.caption(f"📙 전체 용어 목록: 총 {len(filtered_data)}건")

            if filtered_data:
                for match in filtered_data:
                    st.markdown(f"""<div style="background-color: #ffffff; padding: 1.6rem; border-radius: 18px; border: 1px solid #f1f5f9; border-left: 6px solid #0d9488; margin-bottom: 1.2rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03);"><h4 style="color: #0f172a; font-size: 1.25rem; font-weight: 800; margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;">📙 {match['term']}</h4><p style="font-size: 0.96rem; color: #334155; line-height: 1.8; text-align: justify; margin: 0 0 14px 0;">{match['definition']}</p><table style="width: 100%; border: none; margin: 12px 0 0 0; padding: 0; border-collapse: collapse;"><tr style="border: none;"><td style="text-align: left; border: none; padding: 12px 0 0 0; border-top: 1px dashed #e2e8f0; font-size: 0.82rem; color: #64748b;">⛓️ 관련 조문 근거: <strong style="color: #1e293b; font-weight: 600;">{match.get('related_law', '정보 없음')}</strong></td><td style="text-align: right; border: none; padding: 12px 0 0 0; border-top: 1px dashed #e2e8f0; font-size: 0.82rem; width: 90px;"><span style="background-color: rgba(13, 148, 136, 0.08); color: #0f766e; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 0.78rem; display: inline-block;">초성: {get_chosung(match['term'])}</span></td></tr></table></div>""", unsafe_allow_html=True)
            else:
                st.info("조건에 부합하는 경매 용어가 없습니다. 다른 검색어를 입력하거나 다른 초성을 선택해 보세요.")
        else:
            st.warning("용어집 파일(glossary.json)을 로드할 수 없습니다.")
    except Exception as e:
        st.error(f"용어 사전 검색 엔진 로드 실패: {e}")

    render_footer()
