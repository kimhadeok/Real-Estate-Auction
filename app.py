# -*- coding: utf-8 -*-
"""
app.py — 메인 홈페이지 랜딩 화면

부동산 경매 교육 멀티에이전트 RAG 플랫폼의 중앙 포털입니다.
각각의 개별 에이전트 페이지로 안내하고, 실시간 용어 사전 검색, 멀티에이전트 워크플로우,
데이터 시각화 인포그래픽, 그리고 로드맵을 제공합니다.
"""

from __future__ import annotations

import streamlit as st
import config
import json
import base64
from src.common import init_page, check_api_key, ensure_db, render_footer, render_top_menu

def main():
    # 페이지 초기 설정 및 공통 스타일 주입
    init_page("부동산 경매 AI 튜터 | 홈", "🏛️")
    render_top_menu()
    check_api_key()
    ensure_db()

    # 1. Hero Section (그라데이션 타이틀 & KPI 지표 그리드)
    st.markdown("""<div class="hero-container" style="text-align: center; border-left: none;">
<div style="display: inline-block; padding: 4px 14px; margin-bottom: 1.25rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; background-color: var(--primary); border-radius: 9999px; color: #FFFFFF;">
The Future of PropTech AI
</div>
<div class="hero-title" style="font-size: 2.6rem; line-height: 1.2; margin-bottom: 1.25rem;">
AuctionAgent AI <span style="color: var(--secondary);">Platform</span>
</div>
<div class="hero-subtitle" style="max-w: 800px; margin: 0 auto 2.5rem auto; font-size: 1.05rem;">
어렵고 위험한 법원경매 권리분석, 인공지능 RAG 멀티에이전트와 함께 체계적으로 정복하세요.<br>
경매 절차 Q&A부터 핵심 권리분석 개념 학습, 가상 물건 사례 퀴즈 모의고사까지 한 번에 지원합니다.
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 2rem;">
<div style="background-color: #ffffff; padding: 1.25rem; border-radius: 16px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="font-size: 2rem; font-weight: 800; color: var(--secondary);">99.8%</div>
<div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem; font-weight: 600;">권리분석 정확도</div>
</div>
<div style="background-color: #ffffff; padding: 1.25rem; border-radius: 16px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="font-size: 2rem; font-weight: 800; color: var(--accent);">-85%</div>
<div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem; font-weight: 600;">분석 소요 시간 단축</div>
</div>
<div style="background-color: #ffffff; padding: 1.25rem; border-radius: 16px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="font-size: 2rem; font-weight: 800; color: var(--warning);">12.4%</div>
<div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem; font-weight: 600;">평균 낙찰 수익률 향상</div>
</div>
<div style="background-color: #ffffff; padding: 1.25rem; border-radius: 16px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="font-size: 2rem; font-weight: 800; color: #2563eb;">24/7</div>
<div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem; font-weight: 600;">실시간 호재 모니터링</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    # 2. 3대 기능 메뉴 카드 배치 (HTML + st.page_link 연계)
    st.subheader("🚀 핵심 서비스 메뉴 바로가기")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""<div class="card-container">
<div class="card-icon">📋</div>
<div class="card-title">1. 경매 절차 안내</div>
<div class="card-desc">경매신청부터 입찰, 대금 납부, 배당 순서까지 9단계의 흐름도와 관련 법령 조문을 챗봇과 공부합니다.</div>
</div>""", unsafe_allow_html=True)
        st.page_link("pages/auction_procedure.py", label="👉 경매 절차 안내봇 이동", use_container_width=True)

    with col2:
        st.markdown("""<div class="card-container">
<div class="card-icon">📚</div>
<div class="card-title">2. 권리분석 튜터</div>
<div class="card-desc">가장 위험하고 손실이 빈번한 말소기준권리 찾기, 임차인의 대항력 유무 판단 요건을 집중 학습합니다.</div>
</div>""", unsafe_allow_html=True)
        st.page_link("pages/rights_analysis.py", label="👉 권리분석 튜터봇 이동", use_container_width=True)

    with col3:
        st.markdown("""<div class="card-container">
<div class="card-icon">📝</div>
<div class="card-title">3. 사례 퀴즈 연습</div>
<div class="card-desc">가상 등기부와 임차인 명세서를 분석하고 직접 리스크 답안을 작성하여 AI 맞춤 채점 피드백을 받습니다.</div>
</div>""", unsafe_allow_html=True)
        st.page_link("pages/case_quiz.py", label="👉 사례 및 퀴즈 연습실 이동", use_container_width=True)

    # 3. 4단계 지능형 멀티 에이전트 워크플로우 (인포그래픽 스타일)
    st.divider()
    st.subheader("🤖 4단계 지능형 멀티 에이전트 워크플로우")
    st.caption("AuctionAgent AI는 4개의 특화된 AI 에이전트가 협업하여 고정밀 데이터 분석 및 의사결정을 자동 지원합니다.")
    st.markdown("""<div style="margin: 1.5rem 0 2.5rem 0;">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: stretch; gap: 1rem;">
<!-- Node 1 -->
<div style="flex: 1; min-width: 220px; background-color: #ffffff; border: 2px solid var(--primary); border-radius: 16px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 2.2rem; margin-bottom: 0.5rem;">👁️</div>
<div style="font-weight: 700; color: #1d4ed8; font-size: 1.1rem; margin-bottom: 0.25rem;">Eagle-Eye Explorer</div>
<div style="font-size: 0.85rem; color: #1e293b; font-weight: 600; margin-bottom: 0.5rem;">권리 분석 & OCR</div>
</div>
<div style="font-size: 0.78rem; color: #475569; line-height: 1.5; text-align: justify;">법원 경매지 및 등기부등본의 공적 장부 데이터를 텍스트로 판독하고 리스크 권리를 추출합니다.</div>
</div>
<!-- Arrow 1 -->
<div class="flow-arrow-horizontal" style="color: var(--primary); font-size: 1.5rem; font-weight: bold; min-width: 20px;">➡️</div>
<!-- Node 2 -->
<div style="flex: 1; min-width: 220px; background-color: #ffffff; border: 2px solid var(--secondary); border-radius: 16px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📡</div>
<div style="font-weight: 700; color: #0f766e; font-size: 1.1rem; margin-bottom: 0.25rem;">Virtual Reporter</div>
<div style="font-size: 0.85rem; color: #1e293b; font-weight: 600; margin-bottom: 0.5rem;">실시간 시세 & 그라운딩</div>
</div>
<div style="font-size: 0.78rem; color: #475569; line-height: 1.5; text-align: justify;">해당 물건지의 최근 매각 사례, 급매 시세 흐름 및 지역 호재 데이터를 실시간 수집 및 검증합니다.</div>
</div>
<!-- Arrow 2 -->
<div class="flow-arrow-horizontal" style="color: var(--secondary); font-size: 1.5rem; font-weight: bold; min-width: 20px;">➡️</div>
<!-- Node 3 -->
<div style="flex: 1; min-width: 220px; background-color: #ffffff; border: 2px solid var(--accent); border-radius: 16px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔮</div>
<div style="font-weight: 700; color: #be123c; font-size: 1.1rem; margin-bottom: 0.25rem;">Price Oracle</div>
<div style="font-size: 0.85rem; color: #1e293b; font-weight: 600; margin-bottom: 0.5rem;">AI 적정 낙찰가 예측</div>
</div>
<div style="font-size: 0.78rem; color: #475569; line-height: 1.5; text-align: justify;">인수금액 계산, 입찰 인원수 통계 모형을 연동하여 수익을 극대화하는 적정 비딩 가격 범위를 추천합니다.</div>
</div>
<!-- Arrow 3 -->
<div class="flow-arrow-horizontal" style="color: var(--accent); font-size: 1.5rem; font-weight: bold; min-width: 20px;">➡️</div>
<!-- Node 4 -->
<div style="flex: 1; min-width: 220px; background-color: #ffffff; border: 2px solid var(--warning); border-radius: 16px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🤝</div>
<div style="font-weight: 700; color: #b45309; font-size: 1.1rem; margin-bottom: 0.25rem;">Negotiation Sensei</div>
<div style="font-size: 0.85rem; color: #1e293b; font-weight: 600; margin-bottom: 0.5rem;">명도 전략 & 서식 자동화</div>
</div>
<div style="font-size: 0.78rem; color: #475569; line-height: 1.5; text-align: justify;">점유자 분석을 통해 최적의 인도/명도 협상 가이드를 도출하고 법원 내용증명 등 법률 서식을 자동 빌드합니다.</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    # 4. 실시간 경매 데이터 분석 & 시뮬레이터 (인포그래픽 연동)
    st.divider()
    st.subheader("📊 실시간 경매 데이터 분석 & ROI 시뮬레이션")
    st.caption("인공지능 분석 모델이 제공하는 최신 통계와 감정가 10억 기준 입찰 시나리오 시뮬레이션 결과입니다.")
    
    # HTML Chart Dashboard Code (Light Mode Version)
    chart_dashboard_html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');
            body {
                font-family: 'Noto Sans KR', 'Inter', sans-serif;
                background-color: #f8fafc;
                color: #0f172a;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            .chart-card {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            }
            .chart-title {
                font-size: 1rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 1.25rem;
                text-align: center;
            }
            .chart-container {
                position: relative;
                width: 100%;
                height: 250px;
            }
        </style>
    </head>
    <body>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <!-- Chart 1: Safety Distribution -->
            <div class="chart-card">
                <h3 class="chart-title">🛡️ 물건별 AI 안전 등급 비중 (%)</h3>
                <div class="chart-container">
                    <canvas id="safetyChart"></canvas>
                </div>
            </div>
            <!-- Chart 2: Success Factors -->
            <div class="chart-card">
                <h3 class="chart-title">🎯 낙찰 결과 결정 요인 분석 (중요도)</h3>
                <div class="chart-container">
                    <canvas id="successChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Chart 3: ROI Simulation -->
        <div class="chart-card">
            <h3 class="chart-title">💵 감정가 10억 기준 입찰가율 대비 예상 순수익 & 낙찰 확률</h3>
            <div id="roiChart" style="width: 100%; height: 320px;"></div>
        </div>

        <script>
            // Set Chart.js Defaults for Light Theme
            Chart.defaults.color = '#475569';
            Chart.defaults.borderColor = '#e2e8f0';
            
            // 1. Safety Distribution Chart (Doughnut)
            const ctx1 = document.getElementById('safetyChart').getContext('2d');
            new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['매우 안전 (즉시 입찰 가능)', '주의 필요 (인수 리스크 존재)', '위험 (전문가 상담 필요)', '부적합 (심각한 권리 하자)'],
                    datasets: [{
                        data: [15, 55, 20, 10],
                        backgroundColor: ['#0d9488', '#2563eb', '#f59e0b', '#fb7185'],
                        borderWidth: 1,
                        borderColor: '#ffffff',
                        hoverOffset: 10
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#0f172a',
                                font: { size: 10, family: 'Noto Sans KR' },
                                padding: 15,
                                boxWidth: 10
                            }
                        }
                    }
                }
            });

            // 2. Success Factors Chart (Bar)
            const ctx2 = document.getElementById('successChart').getContext('2d');
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['실시간 시세 대조', '예상 입찰 인원수', '권리관계 인수계산', '단지 회전율', '정책/대출 가용성'],
                    datasets: [{
                        label: '중요도 점수',
                        data: [92, 85, 78, 65, 58],
                        backgroundColor: '#2563eb',
                        hoverBackgroundColor: '#3b82f6',
                        borderRadius: 6,
                        borderWidth: 0
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: '#e2e8f0' },
                            ticks: { color: '#475569' }
                        },
                        y: {
                            grid: { display: false },
                            ticks: {
                                color: '#0f172a',
                                font: { size: 11, family: 'Noto Sans KR' }
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });

            // 3. ROI Simulation Chart (Plotly)
            const trace1 = {
                x: [80, 85, 90, 95, 100],
                y: [12000, 8000, 4500, 1200, -2500],
                name: '예상 순수익 (만원)',
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#0d9488', width: 3 },
                fill: 'tozeroy',
                fillcolor: 'rgba(13, 148, 136, 0.08)',
                marker: { size: 8 }
            };

            const trace2 = {
                x: [80, 85, 90, 95, 100],
                y: [15, 45, 75, 92, 98],
                name: '낙찰 확률 (%)',
                yaxis: 'y2',
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#fb7185', width: 2, dash: 'dot' },
                marker: { size: 6 }
            };

            const layout = {
                margin: { l: 60, r: 60, t: 40, b: 40 },
                xaxis: {
                    title: { text: '입찰가율 (%)', font: { color: '#475569', size: 11 } },
                    gridcolor: '#e2e8f0',
                    tickcolor: '#e2e8f0',
                    tickfont: { color: '#475569' }
                },
                yaxis: {
                    title: { text: '예상 수익 (만원)', font: { color: '#0d9488', size: 11 } },
                    gridcolor: '#e2e8f0',
                    tickcolor: '#e2e8f0',
                    tickfont: { color: '#475569' }
                },
                yaxis2: {
                    title: { text: '낙찰 확률 (%)', font: { color: '#fb7185', size: 11 } },
                    overlaying: 'y',
                    side: 'right',
                    range: [0, 100],
                    gridcolor: '#e2e8f0',
                    tickcolor: '#e2e8f0',
                    tickfont: { color: '#475569' }
                },
                plot_bgcolor: 'transparent',
                paper_bgcolor: 'transparent',
                legend: {
                    orientation: 'h',
                    y: -0.2,
                    x: 0.25,
                    font: { color: '#0f172a' }
                },
                hovermode: 'x unified'
            };

            Plotly.newPlot('roiChart', [trace1, trace2], layout, {responsive: true, displayModeBar: false});
        </script>
    </body>
    </html>
    """
    # components.html() 대신 st.iframe() 사용 (Streamlit 신 API)
    # HTML 문자열을 base64 인코딩 Data URI로 변환하여 전달합니다.
    encoded_html = base64.b64encode(chart_dashboard_html.encode("utf-8")).decode()
    data_uri = f"data:text/html;base64,{encoded_html}"
    st.iframe(data_uri, height=920)

    # 5. 경매 절차 9단계 일람
    st.divider()
    st.subheader("🛤️ 법원경매 핵심 9단계 프로세스")
    st.markdown("법원 경매는 민사집행법에 의거하여 아래의 9가지 핵심 단계를 거쳐 공정하게 진행됩니다.")
    
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
            st.markdown(f"""<div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 6px; text-align: center; min-height: 110px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 1.0rem;">
<span style="font-size: 0.9rem; font-weight: 700; color: #0f172a; display: block;">{title}</span>
<span style="font-size: 0.75rem; color: #475569; margin-top: 6px; display: block; line-height: 1.3;">{desc}</span>
</div>""", unsafe_allow_html=True)

    # 6. 플랫폼 발전 로드맵
    st.divider()
    st.subheader("🗺️ AuctionAgent AI 플랫폼 발전 로드맵")
    st.markdown("""<div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem;">
<!-- Phase 1 -->
<div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0;">
<div style="color: var(--accent); font-weight: 900; font-size: 1.2rem; margin-bottom: 0.5rem;">PHASE 1</div>
<h4 style="color: #0f172a; font-weight: 700; margin-bottom: 0.75rem; font-size: 1.05rem;">지식 베이스 & RAG 기초</h4>
<p style="font-size: 0.8rem; color: #475569; line-height: 1.6; margin: 0;">
전국 법원 경매 및 판례 DB 구축. 절차 안내 및 권리분석 개념에 대한 1:1 맞춤형 튜터봇 제공. 가상 등기부 기반 퀴즈 탑재.
</p>
</div>
<!-- Phase 2 -->
<div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0;">
<div style="color: var(--secondary); font-weight: 900; font-size: 1.2rem; margin-bottom: 0.5rem;">PHASE 2</div>
<h4 style="color: #0f172a; font-weight: 700; margin-bottom: 0.75rem; font-size: 1.05rem;">실시간 시세 & 낙찰 가격 예측</h4>
<p style="font-size: 0.8rem; color: #475569; line-height: 1.6; margin: 0;">
국토부 실거래가 및 KB 시세 실시간 연동. 머신러닝 경쟁률 및 적정 낙찰 가격 구간 예측 오라클 모델 적용.
</p>
</div>
<!-- Phase 3 -->
<div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0;">
<div style="color: #2563eb; font-weight: 900; font-size: 1.2rem; margin-bottom: 0.5rem;">PHASE 3</div>
<h4 style="color: #0f172a; font-weight: 700; margin-bottom: 0.75rem; font-size: 1.05rem;">종합 자산관리 & 명도 자동화</h4>
<p style="font-size: 0.8rem; color: #475569; line-height: 1.6; margin: 0;">
인도명령 및 강제집행 시나리오 AI 시뮬레이션. 부동산 특화 금융/세무 연계 및 개인 투자 포트폴리오 최적화.
</p>
</div>
</div>
</div>""", unsafe_allow_html=True)

    # 7. 시스템 정보 대시보드
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
