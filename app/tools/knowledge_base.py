import json
import re
from functools import lru_cache
from pathlib import Path

from langchain_core.tools import tool

KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base.json"

STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "e", "ou", "que", "quem", "qual", "quais",
    "é", "são", "foi", "ser", "está", "como", "sobre", "isso", "essa", "esse",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"\w+", text.lower())
    return {word for word in words if word not in STOPWORDS}


@lru_cache
def _load_documents() -> list[dict]:
    with open(KNOWLEDGE_BASE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _score(query_tokens: set[str], document: dict) -> int:
    title_tokens = _tokenize(document["title"])
    content_tokens = _tokenize(document["content"])
    return 2 * len(query_tokens & title_tokens) + len(query_tokens & content_tokens)


@tool
def search_knowledge_base(query: str) -> str:
    """Busca documentos relevantes sobre tecnologia (Python, Django, FastAPI,
    PostgreSQL, Docker, LangChain, LangGraph) em uma base de conhecimento local.
    Use esta ferramenta quando precisar de informações factuais sobre esses temas."""
    query_tokens = _tokenize(query)
    documents = _load_documents()

    scored = [(_score(query_tokens, doc), doc) for doc in documents]
    relevant = sorted((s for s in scored if s[0] > 0), key=lambda s: s[0], reverse=True)

    if not relevant:
        return "Nenhum documento relevante foi encontrado na base de conhecimento."

    top_matches = [doc for _, doc in relevant[:2]]
    return "\n\n".join(f"{doc['title']}: {doc['content']}" for doc in top_matches)
