"""
rag.py — RAG 백본 (Retrieval-Augmented Generation)

모든 에이전트가 공유하는 검색→생성 파이프라인.
RagAgent 클래스: 지정 컬렉션에서 검색 → 거리순 병합 → 출처와 함께 LLM 답변 생성.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RagAgent:
    """RAG 기반 에이전트."""

    name: str
    description: str  # 라우터가 에이전트를 고를 때 참조
    system_prompt: str
    collections: list[str] = field(default_factory=list)
    top_k: int = 5

    def query(self, question: str, llm=None, chroma_client=None, embedding_fn=None) -> dict:
        """
        질문에 대해 RAG 파이프라인을 실행합니다.

        Returns:
            {
                "agent": str,
                "answer": str,
                "sources": list[str],
                "contexts": list[dict],
            }
        """
        import config
        from providers import get_embeddings, get_llm

        if llm is None:
            llm = get_llm()
        if embedding_fn is None:
            embedding_fn = get_embeddings()
        if chroma_client is None:
            import chromadb
            chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))

        # 1) 다중 컬렉션 검색
        all_results = []
        query_embedding = embedding_fn.embed_query(question)

        for col_name in self.collections:
            try:
                collection = chroma_client.get_collection(col_name)
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=self.top_k,
                    include=["documents", "metadatas", "distances"],
                )

                if results and results["documents"]:
                    for doc, meta, dist in zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0],
                    ):
                        all_results.append({
                            "document": doc,
                            "metadata": meta,
                            "distance": dist,
                            "collection": col_name,
                        })
            except Exception as e:
                print(f"[경고] 컬렉션 '{col_name}' 검색 실패: {e}")

        # 2) 거리순 정렬 + 상위 결과 선택
        all_results.sort(key=lambda x: x["distance"])
        top_results = all_results[: self.top_k]

        # 3) 컨텍스트 구성
        context_parts = []
        sources = []
        for i, r in enumerate(top_results, 1):
            context_parts.append(f"[자료 {i}]\n{r['document']}")
            # 출처 추출
            meta = r["metadata"]
            source_label = _extract_source_label(meta)
            if source_label and source_label not in sources:
                sources.append(source_label)

        context_text = "\n\n---\n\n".join(context_parts) if context_parts else "(검색 결과 없음)"

        # 4) LLM 호출
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=(
                    f"다음 자료를 참고하여 질문에 답하세요.\n\n"
                    f"──── 참고 자료 ────\n{context_text}\n"
                    f"──── 질문 ────\n{question}"
                )
            ),
        ]

        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)

        return {
            "agent": self.name,
            "answer": answer,
            "sources": sources,
            "contexts": top_results,
        }


def _extract_source_label(metadata: dict) -> Optional[str]:
    """메타데이터에서 사람이 읽을 수 있는 출처 라벨을 추출합니다."""
    doc_type = metadata.get("type", "")

    if doc_type == "law":
        heading = metadata.get("heading", "")
        source = metadata.get("source", "")
        source_name = {
            "civil_execution_act": "민사집행법",
            "housing_lease_protection_act": "주택임대차보호법",
        }.get(source, source)
        return f"{source_name} {heading}" if heading else source_name

    elif doc_type == "procedure":
        heading = metadata.get("heading", "")
        return f"경매 절차 해설 — {heading}" if heading else "경매 절차 해설"

    elif doc_type == "glossary":
        term = metadata.get("term", "")
        return f"용어집: {term}" if term else "용어집"

    elif doc_type == "case":
        title = metadata.get("title", "")
        return f"사례: {title}" if title else "가상 사례"

    return metadata.get("source", "")
