"""
LangGraph Execution Graph
Defines the agentic workflow: Orchestrator → Domain Agent → Sentinel → END
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from app.state import GraphState
from agents.orchestrator import OrchestratorAgent
from agents.claims.agent import ClaimsAgent
from agents.billing.agent import BillingAgent
from agents.scheduling.agent import SchedulingAgent
from safety.sentinel import SafetySentinel


class AgenticCallCenterGraph:
    """
    Main LangGraph definition for the agentic call center.
    Flow: Orchestrator → Domain Agent → Sentinel → END
    """
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.claims_agent = ClaimsAgent()
        self.billing_agent = BillingAgent()
        self.scheduling_agent = SchedulingAgent()
        self.sentinel = SafetySentinel()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("claims", self._claims_node)
        workflow.add_node("billing", self._billing_node)
        workflow.add_node("scheduling", self._scheduling_node)
        workflow.add_node("sentinel", self._sentinel_node)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Add conditional edges from orchestrator
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_after_orchestrator,
            {
                "claims": "claims",
                "billing": "billing",
                "scheduling": "scheduling",
                "sentinel": "sentinel",
                "end": END
            }
        )
        
        # All domain agents route to sentinel
        workflow.add_edge("claims", "sentinel")
        workflow.add_edge("billing", "sentinel")
        workflow.add_edge("scheduling", "sentinel")
        
        # Sentinel routes to END
        workflow.add_conditional_edges(
            "sentinel",
            self._route_after_sentinel,
            {
                "end": END,
                "human_review": END  # In production, this would route to human queue
            }
        )
        
        return workflow.compile()
    
    def _orchestrator_node(self, state: GraphState) -> GraphState:
        """Orchestrator node - routes to appropriate domain agent"""
        routing_decision = self.orchestrator.route(state)
        
        return {
            **state,
            "next_agent": routing_decision.target_agent,
            "routing_confidence": routing_decision.confidence,
            "routing_reasoning": routing_decision.reasoning
        }
    
    def _claims_node(self, state: GraphState) -> GraphState:
        """Claims agent node"""
        response = self.claims_agent.process(state)
        return {
            **state,
            "agent_response": response.response,
            "agent_name": "claims",
            "tool_calls": response.tool_requests,
            "tool_results": []  # Tools executed by agent
        }
    
    def _billing_node(self, state: GraphState) -> GraphState:
        """Billing agent node"""
        response = self.billing_agent.process(state)
        return {
            **state,
            "agent_response": response.response,
            "agent_name": "billing",
            "tool_calls": response.tool_requests,
            "tool_results": []
        }
    
    def _scheduling_node(self, state: GraphState) -> GraphState:
        """Scheduling agent node"""
        response = self.scheduling_agent.process(state)
        return {
            **state,
            "agent_response": response.response,
            "agent_name": "scheduling",
            "tool_calls": response.tool_requests,
            "tool_results": []
        }
    
    def _sentinel_node(self, state: GraphState) -> GraphState:
        """Safety sentinel node - validates response before returning"""
        safety_check = self.sentinel.validate(state)
        
        return {
            **state,
            "requires_human_review": safety_check.requires_human_review,
            "safety_flags": safety_check.flags,
            "risk_score": safety_check.risk_score
        }
    
    def _route_after_orchestrator(self, state: GraphState) -> Literal["claims", "billing", "scheduling", "sentinel", "end"]:
        """Route after orchestrator makes decision"""
        next_agent = state.get("next_agent")
        
        if next_agent == "claims":
            return "claims"
        elif next_agent == "billing":
            return "billing"
        elif next_agent == "scheduling":
            return "scheduling"
        elif next_agent == "sentinel":
            return "sentinel"
        else:
            return "end"
    
    def _route_after_sentinel(self, state: GraphState) -> Literal["end", "human_review"]:
        """Route after sentinel validation"""
        if state.get("requires_human_review", False):
            return "human_review"
        return "end"
    
    def invoke(self, user_query: str, session_id: str = "default") -> GraphState:
        """Invoke the graph with a user query"""
        initial_state: GraphState = {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "next_agent": None,
            "routing_confidence": 0.0,
            "routing_reasoning": "",
            "agent_response": None,
            "agent_name": None,
            "tool_calls": [],
            "tool_results": [],
            "requires_human_review": False,
            "safety_flags": [],
            "risk_score": 0.0,
            "conversation_history": [],
            "retrieved_context": [],
            "session_id": session_id,
            "turn_count": 0,
            "error": None
        }
        
        result = self.graph.invoke(initial_state)
        return result

