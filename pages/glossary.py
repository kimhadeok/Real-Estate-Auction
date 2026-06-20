# -*- coding: utf-8 -*-
"""
pages/4_🔍_경매_용어_사전.py

Streamlit 멀티페이지 중 '경매 용어 사전' 진입점 파일입니다.
"""

import sys
import importlib
from pathlib import Path

# 프로젝트 루트 경로 추가 (모듈 검색 경로 확보)
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 캐시된 모듈 강제 리로드로 핫리로드 활성화
if "src.glossary.ui" in sys.modules:
    importlib.reload(sys.modules["src.glossary.ui"])

from src.glossary.ui import render_page

if __name__ == "__main__":
    render_page()

