from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app

client = TestClient(app)


def test_chat_endpoint_with_tool(monkeypatch, fake_llm):
    responses = [
        AIMessage(
            content="",
            tool_calls=[
                {"name": "search_knowledge_base", "args": {"query": "FastAPI"}, "id": "call_1"}
            ],
        ),
        AIMessage(content="FastAPI é um framework web moderno para Python."),
    ]
    monkeypatch.setattr("app.agent.nodes.get_llm", lambda: fake_llm(responses))

    response = client.post("/chat", json={"message": "O que é FastAPI?"})

    assert response.status_code == 200
    body = response.json()
    assert body["used_tool"] is True
    assert body["answer"] == "FastAPI é um framework web moderno para Python."


def test_chat_endpoint_without_tool(monkeypatch, fake_llm):
    responses = [AIMessage(content="2 + 2 = 4.")]
    monkeypatch.setattr("app.agent.nodes.get_llm", lambda: fake_llm(responses))

    response = client.post("/chat", json={"message": "Quanto é 2 + 2?"})

    assert response.status_code == 200
    body = response.json()
    assert body["used_tool"] is False
    assert body["answer"] == "2 + 2 = 4."
