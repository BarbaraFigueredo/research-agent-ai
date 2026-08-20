from langgraph.graph import END, START, StateGraph

from app.agent.nodes import agent_node, tool_node
from app.agent.state import AgentState


def should_use_tool(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool"
    return "end"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tool", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_use_tool, {"tool": "tool", "end": END})
    graph.add_edge("tool", "agent")

    return graph.compile()
