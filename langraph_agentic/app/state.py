"""
Blackboard Schema - Shared Graph State
All agents read from and write to this state.
"""
from typing import TypedDict, List, Optional, Dict, Any, Literal
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class GraphState(TypedDict):
    """
    Shared blackboard state for the agentic system.
    All agents interact with this state.
    """
    # User input
    messages: List[BaseMessage]
    user_query: str
    
    # Orchestrator decisions
    next_agent: Optional[str]  # Which agent to route to
    routing_confidence: float
    routing_reasoning: str
    
    # Agent outputs
    agent_response: Optional[str]
    agent_name: Optional[str]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    
    # Safety flags
    requires_human_review: bool
    safety_flags: List[str]
    risk_score: float
    
    # Memory/Context
    conversation_history: List[Dict[str, str]]
    retrieved_context: List[str]
    
    # Metadata
    session_id: str
    turn_count: int
    error: Optional[str]


class AgentResponse(BaseModel):
    """Structured response from domain agents"""
    response: str = Field(description="Agent's response to the user")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the response")
    requires_tools: bool = Field(description="Whether tools need to be called")
    tool_requests: List[Dict[str, Any]] = Field(default_factory=list, description="Requested tool calls")
    next_action: Optional[str] = Field(description="Suggested next action")


class RoutingDecision(BaseModel):
    """Orchestrator's routing decision"""
    target_agent: Literal["claims", "billing", "scheduling", "sentinel", "end"] = Field(
        description="Target agent to route to"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in routing decision")
    reasoning: str = Field(description="Explanation for routing decision")
    requires_sentinel: bool = Field(default=True, description="Whether to route through safety sentinel")

