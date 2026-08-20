from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import build_graph


def test_agent_flow_uses_tool_when_question_requires_it(monkeypatch, fake_llm):
    responses = [
        AIMessage(
            content="",
            tool_calls=[
                {"name": "search_knowledge_base", "args": {"query": "Docker"}, "id": "call_1"}
            ],
        ),
        AIMessage(content="Docker é uma plataforma de containerização."),
    ]
    monkeypatch.setattr("app.agent.nodes.get_llm", lambda: fake_llm(responses))

    graph = build_graph()
    result = graph.invoke(
        {"messages": [HumanMessage("O que é Docker?")], "context": "", "used_tool": False}
    )

    assert result["used_tool"] is True
    assert "Docker" in result["context"]
    assert result["messages"][-1].text == "Docker é uma plataforma de containerização."


def test_agent_flow_skips_tool_when_question_does_not_require_it(monkeypatch, fake_llm):
    responses = [AIMessage(content="Oi! Tudo bem, e você?")]
    monkeypatch.setattr("app.agent.nodes.get_llm", lambda: fake_llm(responses))

    graph = build_graph()
    result = graph.invoke(
        {"messages": [HumanMessage("Oi, tudo bem?")], "context": "", "used_tool": False}
    )

    assert result["used_tool"] is False
    assert result["context"] == ""
    assert result["messages"][-1].text == "Oi! Tudo bem, e você?"
