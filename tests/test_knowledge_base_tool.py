from app.tools.knowledge_base import search_knowledge_base


def test_search_knowledge_base_finds_relevant_document():
    result = search_knowledge_base.invoke({"query": "O que é PostgreSQL?"})

    assert "PostgreSQL" in result


def test_search_knowledge_base_returns_no_match_message_for_unrelated_query():
    result = search_knowledge_base.invoke({"query": "Qual a capital da França?"})

    assert "Nenhum documento relevante" in result
