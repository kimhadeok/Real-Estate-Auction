"""
ingest.py — clause-aware 청킹 + ChromaDB 4개 컬렉션 구축

법령은 '## 제○○조' 단위, 절차는 '## N단계' 단위로 끊고,
용어/사례는 JSON 항목 단위로 청킹합니다.

사용법:
    python ingest.py            # 임베딩 + ChromaDB 구축 (키 필요)
    python ingest.py --dry-run  # 청킹만 검증 (키 불필요)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import config


# ────────────────────────────────────────────
# 청킹 함수들
# ────────────────────────────────────────────

def chunk_by_heading(text: str, heading_pattern: str = r"^## .+") -> list[dict]:
    """마크다운 ## 헤더 단위로 청킹합니다."""
    chunks = []
    current_heading = ""
    current_lines: list[str] = []

    for line in text.split("\n"):
        if re.match(heading_pattern, line.strip()):
            # 이전 청크 저장
            if current_heading and current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append({
                        "heading": current_heading,
                        "content": f"{current_heading}\n\n{content}",
                    })
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    # 마지막 청크
    if current_heading and current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            chunks.append({
                "heading": current_heading,
                "content": f"{current_heading}\n\n{content}",
            })

    return chunks


def chunk_long_text(text: str, max_chars: int = 2000, overlap: int = 200) -> list[str]:
    """긴 텍스트를 max_chars 단위로 오버랩 분할합니다."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


def chunk_laws(laws_dir: Path) -> list[dict]:
    """법령 마크다운 파일들을 조문 단위로 청킹합니다."""
    chunks = []
    for md_file in sorted(laws_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        source = md_file.stem
        heading_chunks = chunk_by_heading(text)

        for hc in heading_chunks:
            # 긴 조문은 추가 분할
            sub_chunks = chunk_long_text(hc["content"])
            for i, sc in enumerate(sub_chunks):
                chunk_id = f"{source}::{hc['heading']}"
                if len(sub_chunks) > 1:
                    chunk_id += f"::part{i+1}"
                chunks.append({
                    "id": chunk_id,
                    "content": sc,
                    "metadata": {
                        "source": source,
                        "heading": hc["heading"],
                        "type": "law",
                    },
                })

    return chunks


def chunk_procedures(procedures_dir: Path) -> list[dict]:
    """절차 해설 마크다운을 단계 단위로 청킹합니다."""
    chunks = []
    for md_file in sorted(procedures_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        source = md_file.stem
        heading_chunks = chunk_by_heading(text)

        for hc in heading_chunks:
            sub_chunks = chunk_long_text(hc["content"])
            for i, sc in enumerate(sub_chunks):
                chunk_id = f"{source}::{hc['heading']}"
                if len(sub_chunks) > 1:
                    chunk_id += f"::part{i+1}"
                chunks.append({
                    "id": chunk_id,
                    "content": sc,
                    "metadata": {
                        "source": source,
                        "heading": hc["heading"],
                        "type": "procedure",
                    },
                })

    return chunks


def chunk_glossary(glossary_path: Path) -> list[dict]:
    """용어집 JSON을 항목별 1청크로 변환합니다."""
    data = json.loads(glossary_path.read_text(encoding="utf-8"))
    chunks = []

    for item in data:
        term = item["term"]
        content = (
            f"용어: {term}\n"
            f"정의: {item['definition']}\n"
            f"관련 법령: {item.get('related_law', 'N/A')}"
        )
        chunks.append({
            "id": f"glossary::{term}",
            "content": content,
            "metadata": {
                "source": "glossary",
                "term": term,
                "type": "glossary",
            },
        })

    return chunks


def chunk_cases(cases_path: Path) -> list[dict]:
    """가상 사례 JSON을 항목별 1청크로 변환합니다 (정답 포함)."""
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    chunks = []

    for case in data:
        case_id = case["case_id"]
        # 전체 사례를 직렬화 (검색용 — 정답 포함)
        content = json.dumps(case, ensure_ascii=False, indent=2)
        chunks.append({
            "id": case_id,
            "content": content,
            "metadata": {
                "source": "cases",
                "case_id": case_id,
                "difficulty": case["difficulty"],
                "title": case["title"],
                "type": "case",
            },
        })

    return chunks


# ────────────────────────────────────────────
# ChromaDB 구축
# ────────────────────────────────────────────

def build_collection(collection_name: str, chunks: list[dict], chroma_client, embedding_fn):
    """ChromaDB 컬렉션을 (재)생성합니다."""
    # 기존 컬렉션 삭제 (재실행 시 중복 방지)
    try:
        chroma_client.delete_collection(collection_name)
        print(f"  ↳ 기존 컬렉션 '{collection_name}' 삭제")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    if not chunks:
        print(f"  ↳ '{collection_name}': 청크 없음, 빈 컬렉션 생성")
        return

    ids = [c["id"] for c in chunks]
    documents = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # 임베딩 생성
    print(f"  ↳ '{collection_name}': {len(chunks)}개 청크 임베딩 중...")
    embeddings = embedding_fn.embed_documents(documents)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    print(f"  ✓ '{collection_name}': {len(chunks)}개 청크 저장 완료")


def run_ingest(dry_run: bool = False):
    """메인 인제스트 프로세스."""
    print("=" * 50)
    print("부동산 경매 교육 RAG - 지식베이스 구축")
    print("=" * 50)

    # 1) 청킹
    print("\n[1/2] 청킹 중...")

    law_chunks = chunk_laws(config.LAWS_DIR)
    print(f"  법령: {len(law_chunks)}개 청크")

    proc_chunks = chunk_procedures(config.PROCEDURES_DIR)
    print(f"  절차: {len(proc_chunks)}개 청크")

    gloss_chunks = chunk_glossary(config.GLOSSARY_PATH)
    print(f"  용어: {len(gloss_chunks)}개 청크")

    case_chunks = chunk_cases(config.CASES_PATH)
    print(f"  사례: {len(case_chunks)}개 청크")

    total = len(law_chunks) + len(proc_chunks) + len(gloss_chunks) + len(case_chunks)
    print(f"\n  총 {total}개 청크 생성 완료")

    if dry_run:
        print("\n[DRY-RUN] 청킹 검증만 수행. 임베딩/DB 구축은 건너뜁니다.")
        # 샘플 출력
        print("\n── 법령 청크 샘플 ──")
        if law_chunks:
            print(f"  ID: {law_chunks[0]['id']}")
            print(f"  내용 (첫 100자): {law_chunks[0]['content'][:100]}...")
        print("\n── 사례 청크 샘플 ──")
        if case_chunks:
            print(f"  ID: {case_chunks[0]['id']}")
            # 정답이 포함되어 있는지 확인
            has_analysis = '"analysis"' in case_chunks[0]["content"]
            print(f"  정답 포함 여부: {has_analysis}")
        return

    # 2) ChromaDB 구축
    print("\n[2/2] ChromaDB 구축 중...")

    import chromadb
    from providers import get_embeddings

    embedding_fn = get_embeddings()
    chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))

    build_collection(config.COLLECTION_LAWS, law_chunks, chroma_client, embedding_fn)
    build_collection(config.COLLECTION_PROCEDURES, proc_chunks, chroma_client, embedding_fn)
    build_collection(config.COLLECTION_GLOSSARY, gloss_chunks, chroma_client, embedding_fn)
    build_collection(config.COLLECTION_CASES, case_chunks, chroma_client, embedding_fn)

    print(f"\n✅ 지식베이스 구축 완료! → {config.CHROMA_DB_DIR}")


# ────────────────────────────────────────────
# 엔트리포인트
# ────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="경매 교육 RAG 지식베이스 구축")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="청킹만 검증 (임베딩/DB 없이, 키 불필요)",
    )
    args = parser.parse_args()
    run_ingest(dry_run=args.dry_run)
