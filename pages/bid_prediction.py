# -*- coding: utf-8 -*-
"""
pages/bid_prediction.py

Streamlit 멀티페이지 중 'AI 입찰가 예측 (Price Oracle)' 진입점 파일입니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가 (모듈 검색 경로 확보)
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src" / "core"))

from src.price_oracle.ui import render_page

if __name__ == "__main__":
    render_page()
