"""
Orchestrator Agent
Routes user queries to appropriate domain agents.
NEVER calls tools directly - only routes.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.state import GraphState, RoutingDecision
import os
import logging

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrator agent that routes queries to domain agents.
    Uses LLM for intent classification.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.1,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent orchestrator for a customer service call center.
Your job is to classify user queries and route them to the appropriate domain agent.

Available agents:
- claims: Handles insurance claims, claim status, claim submissions, claim denials
- billing: Handles billing questions, invoices, payments, account balances, payment plans
- scheduling: Handles appointment scheduling, rescheduling, cancellations, availability

Analyze the user query and determine:
1. Which agent should handle this query
2. Your confidence level (0.0 to 1.0)
3. Brief reasoning for your decision

Respond with ONLY the agent name: "claims", "billing", "scheduling", or "end" if unclear."""),
            ("user", "{query}")
        ])
    
    def route(self, state: GraphState) -> RoutingDecision:
        """
        Route the query to appropriate domain agent.
        Returns routing decision.
        """
        query = state.get("user_query", "")
        
        if not query:
            return RoutingDecision(
                target_agent="end",
                confidence=0.0,
                reasoning="Empty query"
            )
        
        try:
            # Use LLM for routing
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            agent_name = response.content.strip().lower()
            
            # Validate agent name
            valid_agents = ["claims", "billing", "scheduling", "end"]
            if agent_name not in valid_agents:
                # Fallback to keyword-based routing
                agent_name = self._keyword_routing(query)
            
            # Calculate confidence based on agent match
            confidence = 0.9 if agent_name != "end" else 0.3
            reasoning = f"LLM routed to {agent_name} based on query intent"
            
            logger.info(f"Orchestrator routing: {agent_name} (confidence: {confidence})")
            
            return RoutingDecision(
                target_agent=agent_name,
                confidence=confidence,
                reasoning=reasoning,
                requires_sentinel=True
            )
        
        except Exception as e:
            logger.error(f"Error in orchestrator routing: {e}")
            # Fallback to keyword-based routing
            agent_name = self._keyword_routing(query)
            return RoutingDecision(
                target_agent=agent_name,
                confidence=0.6,
                reasoning=f"Fallback routing due to error: {str(e)}",
                requires_sentinel=True
            )
    
    def _keyword_routing(self, query: str) -> str:
        """Fallback keyword-based routing"""
        query_lower = query.lower()
        
        # Claims keywords
        if any(kw in query_lower for kw in ["claim", "denial", "coverage", "policy", "benefit"]):
            return "claims"
        
        # Billing keywords
        if any(kw in query_lower for kw in ["bill", "invoice", "payment", "balance", "charge", "fee"]):
            return "billing"
        
        # Scheduling keywords
        if any(kw in query_lower for kw in ["schedule", "appointment", "book", "cancel", "reschedule", "available"]):
            return "scheduling"
        
        return "end"

