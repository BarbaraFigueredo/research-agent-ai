from langchain_core.messages import SystemMessage, ToolMessage

from app.agent.llm import get_llm
from app.agent.state import AgentState
from app.prompts.agent_prompt import AGENT_SYSTEM_PROMPT
from app.tools.knowledge_base import search_knowledge_base

TOOLS = [search_knowledge_base]


def agent_node(state: AgentState) -> dict:
    llm_with_tools = get_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT), *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    result = search_knowledge_base.invoke(tool_call["args"])
    tool_message = ToolMessage(content=result, tool_call_id=tool_call["id"])

    return {
        "messages": [tool_message],
        "context": result,
        "used_tool": True,
    }
