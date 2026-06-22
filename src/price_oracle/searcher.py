# -*- coding: utf-8 -*-
"""
src/price_oracle/searcher.py — 법원경매 물건 검색 엔진

Gemini + Google Search Grounding을 이용하여:
  1. 텍스트 키워드 기반 경매물건 검색
  2. 사건번호(경매물건번호) 기반 단건 조회

결과를 표준화된 dict 리스트로 반환합니다.
GEMINI_API_KEY 미설정 시 빈 결과를 반환하며 UI에서 수동 입력을 유도합니다.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import streamlit as st
import config as _cfg

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 사건번호 정규식 패턴
#
# 실제 법원 사건번호 예시:
#   2024타경139058   (6자리)
#   2024 타경 139058 (공백 포함)
#   2023타임54321    (5자리)
#   2025타경1234567  (7자리)
#   2024나12345      (민사항소)
#
# → 연도(4자리) + 사건종류(타경/타임/경/나 등) + 번호(3~8자리)
# ──────────────────────────────────────────────────────────────────────────────
_CASE_NUMBER_RE = re.compile(
    r"\d{4}\s*(?:타경|타임|타합|타기|나|가단|가합|카기|카단|카합)\s*\d{3,8}",
    re.IGNORECASE,
)

# 사건번호 정규화: 공백·특수문자 제거, 표준형으로 변환
# 예: "2024 타경 139058" → "2024타경139058"
_CASE_NORMALIZE_RE = re.compile(r"\s+")


def _normalize_case_number(raw: str) -> str:
    """사건번호에서 공백을 제거해 표준 형식으로 변환합니다."""
    return _CASE_NORMALIZE_RE.sub("", raw.strip())


# ──────────────────────────────────────────────────────────────────────────────
# Gemini 프롬프트 템플릿 (중괄호 이스케이프 주의)
# ──────────────────────────────────────────────────────────────────────────────

# 텍스트 검색 프롬프트
_TEXT_SEARCH_PROMPT = """\
당신은 대한민국 법원경매 정보 검색 전문 AI입니다.
Google 검색 도구를 사용하여 아래 검색어로 법원경매 물건을 찾으세요.

검색 대상 사이트 (우선순위):
1. 대법원 법원경매정보 (courtauction.go.kr)
2. 지지옥션 (ggi.co.kr)
3. 경공매데이터 (auction.co.kr)
4. 부동산태인 (taein.co.kr)

검색어: {QUERY}

다음 정보를 최대 5건 추출하세요:
- 사건번호, 소재 법원, 물건 유형, 소재지 주소
- 감정가(만원), 현재 최저입찰가(만원), 유찰 횟수, 매각기일(YYYY-MM-DD)
- 상세 페이지 URL

반드시 아래 JSON 형식으로만 응답하세요. 설명 텍스트 없이 JSON만 출력하세요:
{{"items":[{{"case_number":"","court":"","property_type":"","address":"","appraisal_price":0,"min_price":0,"foreclosure_count":0,"sale_date":"","detail_url":""}}],"total_count":0,"search_summary":""}}
""".strip()

# 사건번호 단건 조회 프롬프트 (중괄호를 {{}}로 이스케이프하고 사건번호는 치환)
_CASE_NUMBER_SEARCH_PROMPT = """\
당신은 대한민국 법원경매 정보 검색 전문 AI입니다.
Google 검색 도구를 사용하여 아래 사건번호로 경매물건을 반드시 찾으세요.

사건번호: {CASE_NUMBER}
(사건번호 표기 변형: {CASE_NUMBER_SPACED} 도 동일한 물건입니다)

검색 전략 (모두 시도):
1. Google에서 "site:courtauction.go.kr {CASE_NUMBER}" 검색
2. Google에서 "{CASE_NUMBER} 경매" 검색
3. Google에서 "{CASE_NUMBER} 법원경매 매각기일" 검색
4. Google에서 "대법원 경매 {CASE_NUMBER}" 검색
5. courtauction.go.kr 에서 {CASE_NUMBER} 직접 조회

주의:
- 사건번호가 실제 존재하는 것이 확인되었습니다. 반드시 찾아내세요.
- 결과를 못 찾더라도 items 배열에 해당 사건번호를 case_number로 포함하고,
  찾은 정보를 최대한 채우세요.

찾아야 할 정보:
- 소재 법원명 (예: 서울중앙지법, 수원지법 등)
- 물건 유형 (아파트/다세대·빌라/오피스텔/상가/토지/단독·다가구주택 중 하나)
- 물건 소재지 전체 주소
- 감정가 (만원 단위 정수, 모르면 0)
- 현재 최저입찰가 (만원 단위 정수, 모르면 0)
- 유찰 횟수 (정수, 모르면 0)
- 매각기일 (YYYY-MM-DD 형식, 모르면 "")
- 대법원 상세 페이지 URL

반드시 아래 JSON 형식으로만 응답하세요. 설명 텍스트 없이 JSON만 출력하세요:
{{"items":[{{"case_number":"{CASE_NUMBER}","court":"","property_type":"","address":"","appraisal_price":0,"min_price":0,"foreclosure_count":0,"sale_date":"","detail_url":""}}],"total_count":1,"search_summary":""}}
""".strip()


# ──────────────────────────────────────────────────────────────────────────────
# 공용 Gemini 호출 헬퍼
# ──────────────────────────────────────────────────────────────────────────────

def _call_gemini_grounding(prompt: str) -> dict | None:
    """
    Gemini + Google Search Grounding으로 프롬프트를 실행하고
    JSON 응답을 파싱하여 반환합니다.
    실패 시 None 반환.
    """
    api_key = getattr(_cfg, "GEMINI_API_KEY", "") or ""
    if not api_key:
        logger.info("[Searcher] GEMINI_API_KEY 미설정 → 검색 불가")
        return None

    try:
        from google import genai
        from google.genai import types as gtypes

        client = genai.Client(api_key=api_key)
        grounding_tool = gtypes.Tool(google_search=gtypes.GoogleSearch())
        gen_config = gtypes.GenerateContentConfig(
            tools=[grounding_tool],
            temperature=0.0,   # 통계·검색 결과는 결정론적으로
        )
        model_id = getattr(_cfg, "GEMINI_MODEL", "gemini-2.0-flash")
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=gen_config,
        )
        raw = response.text.strip()
        logger.info("[Searcher] Gemini 원문 (%d chars): %s", len(raw), raw[:800])

        # ── 1단계: 마크다운 코드펜스 제거 (```json ... ``` 형태 대응)
        clean = re.sub(r"```(?:json)?\s*", "", raw)
        clean = re.sub(r"```", "", clean).strip()

        # ── 2단계: "items" 키를 포함하는 가장 큰 JSON 블록 탐색 (non-greedy → greedy 순)
        # non-greedy 후보 (짧은 것들)
        candidates = re.findall(r"\{[\s\S]+?\}", clean, re.DOTALL)
        # greedy 후보도 추가 (가장 바깥 전체)
        greedy_match = re.search(r"\{[\s\S]+\}", clean)
        if greedy_match:
            candidates.append(greedy_match.group())

        # 가장 긴 블록부터 시도
        for candidate in sorted(candidates, key=len, reverse=True):
            try:
                parsed = json.loads(candidate)
                if "items" in parsed:
                    logger.info("[Searcher] JSON 파싱 성공: items=%d건", len(parsed.get("items", [])))
                    return parsed
            except json.JSONDecodeError:
                continue

        logger.warning("[Searcher] JSON 파싱 실패 — 응답 원문:\n%s", raw[:800])
        return None

    except ImportError:
        logger.error("[Searcher] google-genai 미설치")
        return None
    except Exception as exc:
        logger.error("[Searcher] Gemini 호출 오류: %s", exc, exc_info=True)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# 결과 정규화 헬퍼
# ──────────────────────────────────────────────────────────────────────────────

_VALID_PROP_TYPES = {
    "아파트", "다세대·빌라", "오피스텔", "상가", "토지", "단독·다가구주택",
}
_PROP_TYPE_MAP = {
    "다세대": "다세대·빌라",
    "빌라": "다세대·빌라",
    "연립": "다세대·빌라",
    "단독주택": "단독·다가구주택",
    "다가구주택": "단독·다가구주택",
    "다가구": "단독·다가구주택",
    "근린상가": "상가",
    "근린생활": "상가",
    "대지": "토지",
    "임야": "토지",
    "전": "토지",
    "답": "토지",
}

_VALID_COURTS = {
    "서울중앙지법", "서울동부지법", "서울서부지법", "서울남부지법", "서울북부지법",
    "수원지법", "인천지법", "의정부지법", "춘천지법", "대전지법",
    "청주지법", "대구지법", "부산지법", "울산지법", "창원지법",
    "광주지법", "전주지법", "제주지법",
}


def _normalize_item(raw_item: dict) -> dict:
    """Gemini 반환 물건 dict를 표준화합니다."""
    prop_type = str(raw_item.get("property_type") or "아파트").strip()
    prop_type = _PROP_TYPE_MAP.get(prop_type, prop_type)
    if prop_type not in _VALID_PROP_TYPES:
        prop_type = "아파트"

    court = str(raw_item.get("court") or "서울중앙지법").strip()
    if court not in _VALID_COURTS:
        matched = next((c for c in _VALID_COURTS if c in court or court in c), "")
        court = matched or court  # 매칭 안 되면 원본 유지

    appraisal = int(raw_item.get("appraisal_price") or 0)
    min_price = int(raw_item.get("min_price") or 0)
    foreclosure = int(raw_item.get("foreclosure_count") or 0)

    # 방어: min_price가 appraisal보다 크면 스왑
    if appraisal > 0 and min_price > appraisal:
        appraisal, min_price = min_price, appraisal

    return {
        "case_number": str(raw_item.get("case_number") or "").strip(),
        "court": court,
        "property_type": prop_type,
        "address": str(raw_item.get("address") or "").strip(),
        "appraisal_price": appraisal,
        "min_price": min_price,
        "foreclosure_count": max(0, foreclosure),
        "sale_date": str(raw_item.get("sale_date") or "").strip(),
        "detail_url": str(raw_item.get("detail_url") or "").strip(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 메인 검색 클래스
# ──────────────────────────────────────────────────────────────────────────────

class AuctionSearcher:
    """
    법원경매 물건 검색기.

    Gemini + Google Search Grounding을 활용하여
    텍스트 키워드 또는 사건번호로 경매물건 정보를 조회합니다.
    """

    @staticmethod
    def is_case_number(query: str) -> bool:
        """
        입력값이 사건번호 패턴인지 판별합니다.
        공백 포함 형식 "2024 타경 139058"도 정상 인식합니다.
        """
        return bool(_CASE_NUMBER_RE.search(query.strip()))

    @staticmethod
    def normalize_case_number(query: str) -> str:
        """공백을 제거하여 표준 사건번호 형식으로 변환합니다."""
        return _normalize_case_number(query)

    # NOTE: @st.cache_data는 인스턴스 메서드에 직접 적용 불가이므로
    # module-level 캐시 함수를 사용합니다.
    def search(self, query: str) -> dict[str, Any]:
        """
        검색어를 분석하여 텍스트 검색 또는 사건번호 검색을 자동 선택합니다.

        Args:
            query: 검색어 (자유 텍스트 또는 사건번호)

        Returns:
            {"items": [...], "total_count": int, "search_summary": str,
             "is_live": bool, "search_type": str, "error": str|None}
        """
        query = query.strip()
        if not query:
            return _empty_result("검색어를 입력해 주세요.")

        api_key = getattr(_cfg, "GEMINI_API_KEY", "") or ""
        if not api_key:
            return _empty_result(
                "⚠️ GEMINI_API_KEY가 설정되지 않아 실시간 검색을 사용할 수 없습니다. "
                ".env 파일에 키를 등록하거나, 아래 '입찰가 예측' 탭에서 수동으로 분석하세요."
            )

        if AuctionSearcher.is_case_number(query):
            return _cached_search_by_case(query)
        else:
            return _cached_search_by_text(query)


# ──────────────────────────────────────────────────────────────────────────────
# 캐싱된 검색 함수 (module-level로 @st.cache_data 적용)
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def _cached_search_by_text(query: str) -> dict[str, Any]:
    """텍스트 키워드로 경매물건을 검색합니다. (30분 캐시)"""
    prompt = _TEXT_SEARCH_PROMPT.replace("{QUERY}", query)
    data = _call_gemini_grounding(prompt)

    if not data:
        return _empty_result(
            f"'{query}' 검색 결과를 가져오지 못했습니다. "
            "검색어를 바꾸거나 사건번호 형식(예: 2024타경12345)으로 시도해 보세요."
        )

    items = [_normalize_item(it) for it in (data.get("items") or [])]
    return {
        "items": items,
        "total_count": len(items),
        "search_summary": data.get("search_summary") or f"'{query}' 검색 결과",
        "is_live": True,
        "search_type": "text",
        "error": None,
    }


def _search_by_case_impl(raw_query: str) -> dict[str, Any]:
    """
    사건번호로 경매물건을 단건 조회합니다. (내부 구현 — 캐시 없음)

    공백 포함 입력("2024 타경 139058")을 자동으로 정규화합니다.
    """
    # 공백 제거 → 표준 사건번호
    case_number = _normalize_case_number(raw_query)
    # 공백 포함 표기 (프롬프트에 제공용)
    case_number_spaced = re.sub(
        r"(\d{4})(타경|타임|타합|타기|나|가단|가합|카기|카단|카합)(\d+)",
        r"\1 \2 \3",
        case_number,
        flags=re.IGNORECASE,
    )
    logger.info("[Searcher] 사건번호 정규화: '%s' → '%s'", raw_query, case_number)

    prompt = (
        _CASE_NUMBER_SEARCH_PROMPT
        .replace("{CASE_NUMBER}", case_number)
        .replace("{CASE_NUMBER_SPACED}", case_number_spaced)
    )
    data = _call_gemini_grounding(prompt)

    if not data:
        # 1차 실패 시 텍스트 검색으로 폴백 시도
        logger.info("[Searcher] 사건번호 직접 조회 실패 → 텍스트 검색 폴백: %s", case_number)
        fallback_prompt = _TEXT_SEARCH_PROMPT.replace("{QUERY}", f"{case_number} 법원경매")
        data = _call_gemini_grounding(fallback_prompt)

    if not data:
        return _empty_result(
            f"사건번호 '{case_number}'를 조회하지 못했습니다. "
            "번호를 다시 확인하거나 대법원 경매정보(courtauction.go.kr)에서 직접 검색해 보세요."
        )

    items = [_normalize_item(it) for it in (data.get("items") or [])]

    # 사건번호로 조회했는데 items가 비어 있으면 에러 처리
    if not items:
        return _empty_result(
            f"사건번호 '{case_number}'에 해당하는 물건 정보를 찾지 못했습니다. "
            "사건번호를 확인하거나 대법원 경매정보(courtauction.go.kr)에서 직접 검색해 보세요."
        )

    return {
        "items": items,
        "total_count": len(items),
        "search_summary": data.get("search_summary") or f"사건번호 {case_number} 조회 결과",
        "is_live": True,
        "search_type": "case_number",
        "normalized_case_number": case_number,
        "error": None,
    }


@st.cache_data(ttl=1800, show_spinner=False)
def _cached_search_by_case(raw_query: str) -> dict[str, Any]:
    """
    사건번호로 경매물건을 단건 조회합니다. (30분 캐시)
    단, 오류(빈 결과)는 캐시하지 않아 재시도 시 재검색합니다.
    """
    result = _search_by_case_impl(raw_query)
    # 오류 결과는 캐시에서 즉시 제거 (다음 호출 시 재검색)
    if result.get("error"):
        _cached_search_by_case.clear()
    return result


# ──────────────────────────────────────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────────────────────────────────────

def _empty_result(error_msg: str = "") -> dict[str, Any]:
    return {
        "items": [],
        "total_count": 0,
        "search_summary": "",
        "is_live": False,
        "search_type": "none",
        "error": error_msg,
    }


@st.cache_resource
def get_searcher() -> AuctionSearcher:
    """AuctionSearcher 인스턴스를 세션 전체에서 1회만 생성합니다."""
    return AuctionSearcher()
