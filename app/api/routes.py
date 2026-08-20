from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.agent.graph import build_graph
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

_graph = build_graph()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = _graph.invoke(
        {
            "messages": [HumanMessage(content=request.message)],
            "context": "",
            "used_tool": False,
        }
    )
    return ChatResponse(
        answer=result["messages"][-1].content,
        used_tool=result["used_tool"],
    )
