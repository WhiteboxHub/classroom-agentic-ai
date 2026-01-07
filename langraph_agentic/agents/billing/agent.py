"""
Billing Agent
Handles billing, payments, and account questions.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.state import GraphState, AgentResponse
from agents.billing.tools import BillingTools
from agents.billing.prompt import BILLING_AGENT_SYSTEM_PROMPT
import os
import logging
import json
import re

logger = logging.getLogger(__name__)


class BillingAgent:
    """
    Billing domain agent.
    Handles all billing-related queries.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.2,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools = BillingTools()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", BILLING_AGENT_SYSTEM_PROMPT),
            ("user", "{query}")
        ])
    
    def process(self, state: GraphState) -> AgentResponse:
        """Process the user query related to billing"""
        query = state.get("user_query", "")
        
        try:
            # Analyze tool needs
            tool_analysis = self._analyze_tool_needs(query)
            
            # Execute tools if needed
            tool_results = []
            if tool_analysis["needs_tools"]:
                tool_results = self._execute_tools(tool_analysis["tool_calls"])
            
            # Build context
            context = self._build_context(tool_results)
            
            # Generate response
            response_prompt = f"{query}\n\nContext from tools:\n{context}" if context else query
            chain = self.prompt | self.llm
            llm_response = chain.invoke({"query": response_prompt})
            
            return AgentResponse(
                response=llm_response.content,
                confidence=0.9 if tool_results else 0.7,
                requires_tools=len(tool_results) > 0,
                tool_requests=tool_analysis["tool_calls"],
                next_action=None
            )
        
        except Exception as e:
            logger.error(f"Error in BillingAgent: {e}", exc_info=True)
            return AgentResponse(
                response=f"I apologize, but I encountered an error processing your billing request: {str(e)}",
                confidence=0.0,
                requires_tools=False,
                tool_requests=[],
                next_action=None
            )
    
    def _analyze_tool_needs(self, query: str) -> dict:
        """Analyze if tools are needed"""
        query_lower = query.lower()
        tool_calls = []
        
        # Extract account ID if present
        account_match = re.search(r'ACC-?\d+', query, re.IGNORECASE)
        account_id = account_match.group(0).replace("-", "") if account_match else "ACC-12345"
        
        # Check for balance inquiry
        if any(kw in query_lower for kw in ["balance", "owe", "outstanding"]):
            tool_calls.append({
                "tool": "get_account_balance",
                "args": {"account_id": account_id}
            })
        
        # Check for payment processing
        if any(kw in query_lower for kw in ["pay", "payment", "make payment"]):
            # Extract amount if present
            amount_match = re.search(r'\$?(\d+\.?\d*)', query)
            amount = float(amount_match.group(1)) if amount_match else 100.0
            
            tool_calls.append({
                "tool": "process_payment",
                "args": {
                    "account_id": account_id,
                    "amount": amount,
                    "payment_method": "credit_card"
                }
            })
        
        # Check for billing history
        if any(kw in query_lower for kw in ["history", "past bills", "previous"]):
            tool_calls.append({
                "tool": "get_billing_history",
                "args": {"account_id": account_id, "months": 6}
            })
        
        # Check for payment plan
        if "payment plan" in query_lower or "installment" in query_lower:
            tool_calls.append({
                "tool": "setup_payment_plan",
                "args": {
                    "account_id": account_id,
                    "monthly_amount": 100.0,
                    "duration_months": 6
                }
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
                if tool_name == "get_account_balance":
                    result = self.tools.get_account_balance(**args)
                elif tool_name == "get_billing_history":
                    result = self.tools.get_billing_history(**args)
                elif tool_name == "process_payment":
                    result = self.tools.process_payment(**args)
                elif tool_name == "setup_payment_plan":
                    result = self.tools.setup_payment_plan(**args)
                elif tool_name == "explain_charge":
                    result = self.tools.explain_charge(**args)
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

