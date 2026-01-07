"""
Claims Agent
Handles insurance claims, claim status, and coverage questions.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from app.state import GraphState, AgentResponse
from agents.claims.tools import ClaimsTools
from agents.claims.prompt import CLAIMS_AGENT_SYSTEM_PROMPT
import os
import logging
import json

logger = logging.getLogger(__name__)


class ClaimsAgent:
    """
    Claims domain agent.
    Handles all claims-related queries.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.2,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools = ClaimsTools()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CLAIMS_AGENT_SYSTEM_PROMPT),
            ("user", "{query}")
        ])
    
    def process(self, state: GraphState) -> AgentResponse:
        """
        Process the user query related to claims.
        May call tools if needed.
        """
        query = state.get("user_query", "")
        
        try:
            # First, determine if tools are needed
            tool_analysis = self._analyze_tool_needs(query)
            
            # Execute tools if needed
            tool_results = []
            if tool_analysis["needs_tools"]:
                tool_results = self._execute_tools(tool_analysis["tool_calls"])
            
            # Build context with tool results
            context = self._build_context(tool_results)
            
            # Generate response with context
            response_prompt = f"{query}\n\nContext from tools:\n{context}" if context else query
            chain = self.prompt | self.llm
            llm_response = chain.invoke({"query": response_prompt})
            
            response_text = llm_response.content
            
            return AgentResponse(
                response=response_text,
                confidence=0.9 if tool_results else 0.7,
                requires_tools=len(tool_results) > 0,
                tool_requests=tool_analysis["tool_calls"],
                next_action=None
            )
        
        except Exception as e:
            logger.error(f"Error in ClaimsAgent: {e}", exc_info=True)
            return AgentResponse(
                response=f"I apologize, but I encountered an error processing your claims request: {str(e)}",
                confidence=0.0,
                requires_tools=False,
                tool_requests=[],
                next_action=None
            )
    
    def _analyze_tool_needs(self, query: str) -> dict:
        """Analyze if tools are needed and which ones"""
        query_lower = query.lower()
        tool_calls = []
        
        # Check for claim number lookup
        import re
        claim_number_match = re.search(r'CLM-?\d+', query, re.IGNORECASE)
        if claim_number_match or "status" in query_lower:
            claim_num = claim_number_match.group(0).replace("-", "") if claim_number_match else "CLM-12345"
            tool_calls.append({
                "tool": "lookup_claim_status",
                "args": {"claim_number": claim_num}
            })
        
        # Check for new claim submission
        if any(kw in query_lower for kw in ["submit", "file", "new claim"]):
            tool_calls.append({
                "tool": "submit_new_claim",
                "args": {
                    "policy_number": "POL-12345",  # Would extract from query
                    "claim_type": "medical",
                    "amount": 1000.0,
                    "description": "Extracted from query"
                }
            })
        
        # Check for coverage questions
        if "coverage" in query_lower or "covered" in query_lower:
            tool_calls.append({
                "tool": "check_coverage",
                "args": {"policy_number": "POL-12345"}
            })
        
        return {
            "needs_tools": len(tool_calls) > 0,
            "tool_calls": tool_calls
        }
    
    def _execute_tools(self, tool_calls: list) -> list:
        """Execute tool calls"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["tool"]
            args = tool_call["args"]
            
            try:
                if tool_name == "lookup_claim_status":
                    result = self.tools.lookup_claim_status(**args)
                elif tool_name == "submit_new_claim":
                    result = self.tools.submit_new_claim(**args)
                elif tool_name == "get_claim_details":
                    result = self.tools.get_claim_details(**args)
                elif tool_name == "check_coverage":
                    result = self.tools.check_coverage(**args)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                
                results.append({
                    "tool": tool_name,
                    "result": result
                })
            
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                results.append({
                    "tool": tool_name,
                    "result": {"success": False, "error": str(e)}
                })
        
        return results
    
    def _build_context(self, tool_results: list) -> str:
        """Build context string from tool results"""
        if not tool_results:
            return ""
        
        context_parts = []
        for tr in tool_results:
            context_parts.append(
                f"Tool: {tr['tool']}\nResult: {json.dumps(tr['result'], indent=2)}"
            )
        
        return "\n\n".join(context_parts)

