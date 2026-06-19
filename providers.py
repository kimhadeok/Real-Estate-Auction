"""
providers.py — LLM · 임베딩 객체 팩토리
모든 모듈이 여기서 LLM/임베딩 인스턴스를 가져다 씁니다.
.env 의 LLM_PROVIDER / EMBEDDING_PROVIDER 값에 따라 자동 전환.
"""

from __future__ import annotations

import config


def get_llm(temperature: float = 0.3):
    """LLM 인스턴스를 반환합니다."""
    if config.LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=2048,
        )
    else:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            openai_api_key=config.OPENAI_API_KEY,
            temperature=temperature,
            max_tokens=2048,
        )


def get_embeddings():
    """임베딩 인스턴스를 반환합니다."""
    if config.EMBEDDING_PROVIDER == "huggingface":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=config.HF_EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    else:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=config.OPENAI_EMBEDDING_MODEL,
            openai_api_key=config.OPENAI_API_KEY,
        )
