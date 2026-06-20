# -*- coding: utf-8 -*-
"""
src/price_oracle/engine.py — Price Oracle 계산 엔진

기획안 §2.3 세부 액션 구현:
  1. 목표 수익률 기준 최대 입찰 마지노선 역산
  2. 취득세·법무비·명도비·인테리어비·대출이자 항목별 비용 산출
  3. 낙찰 확률 구간 시뮬레이션 (통계 기반 추정)
  4. 예상 경쟁자 수 범위 안내
  5. AI 전략 코멘트 생성
"""

from __future__ import annotations

import math
import streamlit as st
import pandas as pd


# ──────────────────────────────────────────
# 물건 유형별 기본 낙찰가율 통계 (교육용 추정치)
# 실제 서비스에서는 Gemini + Google Search Grounding으로 실시간 조회
# ──────────────────────────────────────────
_BID_RATE_STATS: dict[str, dict] = {
    "아파트":         {"mean": 0.94, "std": 0.06, "competitors": (5, 15)},
    "다세대·빌라":    {"mean": 0.86, "std": 0.08, "competitors": (3, 8)},
    "오피스텔":       {"mean": 0.89, "std": 0.07, "competitors": (3, 10)},
    "상가":           {"mean": 0.76, "std": 0.10, "competitors": (2, 6)},
    "토지":           {"mean": 0.80, "std": 0.12, "competitors": (2, 5)},
    "단독·다가구주택": {"mean": 0.83, "std": 0.09, "competitors": (2, 7)},
}

# 유찰 횟수별 최저가 감액 비율 (민사집행법 기준: 1회 유찰당 20% 감액)
_FORECLOSURE_DISCOUNT = 0.80  # 1회당 80%


class PriceOracleEngine:
    """
    AI 입찰가 예측 핵심 계산 엔진.

    현재는 통계 기반 로컬 계산 엔진을 사용합니다.
    Phase 2에서 Gemini API + Google Search Grounding 연동으로 고도화 예정.
    """

    def analyze(self, inputs: dict) -> dict:
        """
        입력값을 받아 입찰 분석 결과 딕셔너리를 반환합니다.

        Args:
            inputs: UI 폼에서 전달된 입력값 딕셔너리

        Returns:
            result: 최대 입찰가·비용역산·확률분포·AI코멘트 포함 결과 딕셔너리
        """
        appraisal   = inputs["appraisal_price"]       # 만원
        min_price   = inputs["min_price"]              # 만원
        target_p    = inputs["target_profit"]          # 만원
        loan_ratio  = inputs["loan_ratio"]             # 소수
        int_rate    = inputs["interest_rate"]          # 연이율 소수
        months      = inputs["holding_months"]
        legal       = inputs["legal_cost"]             # 만원
        eviction    = inputs["eviction_cost"]          # 만원
        renovation  = inputs["renovation_cost"]        # 만원
        prop_type   = inputs["property_type"]
        foreclosure = inputs["foreclosure_count"]

        # ── 1. 취득세 계산 (아파트 기준 1~3% 구간, 교육용 단순화)
        acquisition_tax_rate = self._get_acquisition_tax_rate(prop_type, appraisal)
        # 취득세는 낙찰가 기준이나, 역산 전 감정가 기준으로 추정
        acq_tax_estimated = appraisal * acquisition_tax_rate

        # ── 2. 대출 이자 계산 (단리 기준)
        # 대출 원금 = 낙찰가 × 대출비율 (낙찰가를 max_bid로 추정하므로 순환 → 감정가 기준 1차 추정)
        loan_amount_est = appraisal * loan_ratio
        interest_cost = loan_amount_est * int_rate * (months / 12)

        # ── 3. 총 부대비용 합산
        total_cost = acq_tax_estimated + legal + eviction + renovation + interest_cost

        # ── 4. 최대 입찰 마지노선 역산
        # 낙찰가 = 예상 매도가 - 총비용 - 목표순수익
        # 예상 매도가 ≈ 감정가 (KB시세 유사 가정, 교육용 단순화)
        max_bid = appraisal - total_cost - target_p

        # 최저가 미만으로 내려가는 경우 최저가로 하한 설정
        max_bid = max(max_bid, min_price)

        # 최대 입찰가율 (감정가 대비 %)
        bid_ratio = (max_bid / appraisal) * 100

        # ── 5. 낙찰 확률 분포 시뮬레이션
        stats = _BID_RATE_STATS.get(prop_type, _BID_RATE_STATS["아파트"])
        prob_chart_data = self._simulate_prob_distribution(
            appraisal=appraisal,
            mean_rate=stats["mean"],
            std=stats["std"],
            foreclosure=foreclosure,
        )

        # ── 6. 마지노선 기준 낙찰 성공 확률 (정규분포 CDF 근사)
        z_score = (bid_ratio / 100 - stats["mean"]) / stats["std"]
        success_prob = self._normal_cdf(z_score) * 100

        # ── 7. 예상 경쟁자 수
        comp_min, comp_max = stats["competitors"]
        # 유찰 횟수가 많을수록 경쟁자 감소
        comp_adj = max(0, foreclosure * 1)
        comp_min = max(1, comp_min - comp_adj)
        comp_max = max(1, comp_max - comp_adj)

        # ── 8. AI 전략 코멘트 생성
        ai_comment = self._generate_comment(
            prop_type=prop_type,
            max_bid=max_bid,
            appraisal=appraisal,
            bid_ratio=bid_ratio,
            success_prob=success_prob,
            foreclosure=foreclosure,
            comp_min=comp_min,
            comp_max=comp_max,
            total_cost=total_cost,
            target_p=target_p,
        )

        # ── 취득세 재계산 (실제 max_bid 기준으로 업데이트)
        acq_tax_final = max_bid * acquisition_tax_rate
        total_cost_final = acq_tax_final + legal + eviction + renovation + interest_cost

        return {
            "max_bid": max_bid,
            "bid_ratio": bid_ratio,
            "success_prob": success_prob,
            "competitor_min": comp_min,
            "competitor_max": comp_max,
            "cost_breakdown": {
                "acquisition_tax": acq_tax_final,
                "acquisition_tax_note": f"낙찰가 × {acquisition_tax_rate*100:.1f}% (취득세+농특세+지방교육세)",
                "legal_cost": legal,
                "eviction_cost": eviction,
                "renovation_cost": renovation,
                "interest_cost": interest_cost,
                "interest_note": f"대출 {loan_ratio*100:.0f}% × 연 {int_rate*100:.1f}% × {months}개월",
                "total_cost": total_cost_final,
                "target_profit": target_p,
            },
            "prob_chart_data": prob_chart_data,
            "ai_comment": ai_comment,
        }

    # ──────────────────────────────────────
    # 내부 헬퍼 메서드
    # ──────────────────────────────────────

    @staticmethod
    def _get_acquisition_tax_rate(prop_type: str, appraisal_man: int) -> float:
        """
        물건 유형과 금액에 따른 취득세율을 반환합니다 (교육용 단순화).
        아파트 기준: 6억↓=1.1%, 6~9억=2.2%, 9억↑=3.3%
        """
        appraisal_ok = appraisal_man * 10_000  # 원 단위 변환
        if prop_type in ("아파트", "다세대·빌라", "단독·다가구주택"):
            if appraisal_ok <= 600_000_000:
                return 0.011  # 1% + 농특세 0.1%
            elif appraisal_ok <= 900_000_000:
                return 0.022
            else:
                return 0.033
        elif prop_type in ("상가", "토지"):
            return 0.044  # 상가·토지 기본 취득세 4%+
        else:
            return 0.033  # 오피스텔 등 기타

    @staticmethod
    @st.cache_data
    def _simulate_prob_distribution(
        appraisal: int,
        mean_rate: float,
        std: float,
        foreclosure: int,
    ) -> pd.DataFrame:
        """
        입찰가 구간별 낙찰 확률 분포 DataFrame을 반환합니다.
        정규분포 기반 교육용 시뮬레이션 데이터입니다.
        동일 파라미터 호출은 캐시에서 즉시 반환합니다.
        """
        # 유찰 횟수에 따라 낙찰가율 평균 소폭 하향
        adj_mean = mean_rate - foreclosure * 0.02
        adj_mean = max(0.50, adj_mean)

        rows = []
        for rate_pct in range(60, 105, 5):
            rate = rate_pct / 100
            z = (rate - adj_mean) / std
            # 단순 정규분포 확률밀도 기반 상대 확률 (0~100 스케일)
            prob = math.exp(-0.5 * z**2) / (std * math.sqrt(2 * math.pi))
            bid_amount = int(appraisal * rate)
            rows.append({
                "입찰가 구간 (만원)": f"{bid_amount:,}",
                "낙찰 확률 (%)": round(prob * 100, 1),
            })

        return pd.DataFrame(rows)

    @staticmethod
    def _normal_cdf(z: float) -> float:
        """표준 정규분포 CDF 근사 (에러 함수 활용)."""
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    @staticmethod
    def _generate_comment(
        prop_type: str,
        max_bid: float,
        appraisal: float,
        bid_ratio: float,
        success_prob: float,
        foreclosure: int,
        comp_min: int,
        comp_max: int,
        total_cost: float,
        target_p: float,
    ) -> str:
        """입력값과 결과를 종합하여 AI 전략 코멘트를 생성합니다."""

        foreclosure_comment = (
            f"{foreclosure}회 유찰된 물건으로 경쟁이 다소 낮을 수 있습니다. "
            "단, 유찰에 숨은 이유(권리 하자, 입지 문제 등)를 반드시 확인하세요."
            if foreclosure >= 2
            else "신건 또는 1회 유찰 물건으로 경쟁이 치열할 수 있습니다."
        )

        success_str = (
            "낙찰 가능성이 높은 구간입니다." if success_prob >= 55
            else "낙찰 가능성이 낮은 구간입니다. 조금 더 높은 금액을 검토해보세요."
        )

        return (
            f"🏠 <strong>{prop_type}</strong> 물건 분석 결과, "
            f"목표 세후 수익 <strong>{target_p:,.0f}만원</strong> 달성을 위한 "
            f"최대 입찰 마지노선은 <strong>{max_bid:,.0f}만원 (감정가 대비 {bid_ratio:.1f}%)</strong>입니다. "
            f"이 금액으로 입찰 시 통계 기반 낙찰 성공 확률은 약 <strong>{success_prob:.0f}%</strong>로 추정됩니다. "
            f"{success_str}<br><br>"
            f"📊 예상 경쟁자는 <strong>{comp_min}~{comp_max}명</strong> 수준입니다. "
            f"{foreclosure_comment}<br><br>"
            f"💡 총 부대비용(취득세·법무비·명도비·인테리어비·이자)은 약 <strong>{total_cost:,.0f}만원</strong>으로 "
            f"산출되었으며, 실제 명도 난이도·인테리어 범위·금리 변동에 따라 달라질 수 있습니다. "
            f"입찰 전 현장 임장 및 등기부등본 권리분석을 병행하시기 바랍니다."
        )
