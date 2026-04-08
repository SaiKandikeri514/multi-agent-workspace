import operator
from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class AgentState(TypedDict):
    """
    State representing the multi-agent graph.
    - messages: conversational history
    - next_agent: the router output (which node to go to next)
    - active_context: shared context from tool outputs for the UI
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agent: str
    active_context: Annotated[List[str], operator.add]
    completed_workers: Annotated[List[str], operator.add]
