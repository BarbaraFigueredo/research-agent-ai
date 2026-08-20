import pytest


class FakeLLMWithTools:
    def __init__(self, responses):
        self.responses = responses

    def invoke(self, messages):
        return self.responses.pop(0)


class FakeLLM:
    def __init__(self, responses):
        self.responses = responses

    def bind_tools(self, tools):
        return FakeLLMWithTools(self.responses)


@pytest.fixture
def fake_llm():
    """Fábrica de um LLM dublê: recebe uma lista de AIMessage e as devolve
    em sequência a cada chamada, simulando decisões do modelo sem rede."""
    return FakeLLM
