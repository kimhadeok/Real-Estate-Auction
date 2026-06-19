"""
config.py — 중앙 설정
LLM / 임베딩 / ChromaDB 경로 / 컬렉션명 등 프로젝트 전역 설정.
.env 파일에서 환경변수를 읽어옵니다.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── 프로젝트 경로 ───
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
PROMPTS_DIR = BASE_DIR / "prompts"

# ─── ChromaDB 컬렉션명 ───
COLLECTION_LAWS = "auction_laws"
COLLECTION_PROCEDURES = "auction_procedures"
COLLECTION_GLOSSARY = "auction_glossary"
COLLECTION_CASES = "auction_cases"

ALL_COLLECTIONS = [
    COLLECTION_LAWS,
    COLLECTION_PROCEDURES,
    COLLECTION_GLOSSARY,
    COLLECTION_CASES,
]

# ─── 데이터 파일 경로 ───
LAWS_DIR = DATA_DIR / "laws"
PROCEDURES_DIR = DATA_DIR / "procedures"
GLOSSARY_PATH = DATA_DIR / "glossary" / "glossary.json"
CASES_PATH = DATA_DIR / "cases" / "sample_cases.json"

# ─── 프롬프트 로더 ───
def load_prompt(filename: str) -> str:
    """prompts 폴더에서 프롬프트 텍스트 파일을 읽어옵니다."""
    prompt_path = PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8")

# ─── LLM 설정 ───
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

# ─── 임베딩 설정 ───
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")

# ─── 청킹 설정 ───
CHUNK_MAX_TOKENS = 800       # 조문 1개가 이보다 길면 추가 분할
CHUNK_OVERLAP_TOKENS = 100   # 추가 분할 시 오버랩

# ─── RAG 검색 설정 ───
RAG_TOP_K = 5                # 컬렉션당 검색 결과 수
RAG_SCORE_THRESHOLD = 1.5    # 거리 임계값 (이상이면 제외)
