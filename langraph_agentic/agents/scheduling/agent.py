"""
Scheduling Agent
Handles appointment scheduling, rescheduling, and cancellations.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.state import GraphState, AgentResponse
from agents.scheduling.tools import SchedulingTools
from agents.scheduling.prompt import SCHEDULING_AGENT_SYSTEM_PROMPT
import os
import logging
import json
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SchedulingAgent:
    """
    Scheduling domain agent.
    Handles all scheduling-related queries.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.2,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools = SchedulingTools()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SCHEDULING_AGENT_SYSTEM_PROMPT),
            ("user", "{query}")
        ])
    
    def process(self, state: GraphState) -> AgentResponse:
        """Process the user query related to scheduling"""
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
            logger.error(f"Error in SchedulingAgent: {e}", exc_info=True)
            return AgentResponse(
                response=f"I apologize, but I encountered an error processing your scheduling request: {str(e)}",
                confidence=0.0,
                requires_tools=False,
                tool_requests=[],
                next_action=None
            )
    
    def _analyze_tool_needs(self, query: str) -> dict:
        """Analyze if tools are needed"""
        query_lower = query.lower()
        tool_calls = []
        
        # Extract appointment ID if present
        apt_match = re.search(r'APT-?\d+', query, re.IGNORECASE)
        appointment_id = apt_match.group(0).replace("-", "") if apt_match else None
        
        # Check for availability
        if any(kw in query_lower for kw in ["available", "availability", "when can", "open slots"]):
            # Extract date if present
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', query)
            date = date_match.group(0) if date_match else None
            
            tool_calls.append({
                "tool": "check_availability",
                "args": {
                    "date": date,
                    "service_type": "general"
                }
            })
        
        # Check for scheduling
        if any(kw in query_lower for kw in ["schedule", "book", "make appointment", "set up"]):
            # Extract date and time if present
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', query)
            time_match = re.search(r'\d{1,2}:\d{2}', query)
            
            date = date_match.group(0) if date_match else (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            time = time_match.group(0) if time_match else "10:00"
            
            tool_calls.append({
                "tool": "schedule_appointment",
                "args": {
                    "customer_id": "CUST-001",
                    "date": date,
                    "time": time,
                    "service_type": "general"
                }
            })
        
        # Check for rescheduling
        if any(kw in query_lower for kw in ["reschedule", "change appointment", "move appointment"]):
            if appointment_id:
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', query)
                time_match = re.search(r'\d{1,2}:\d{2}', query)
                
                new_date = date_match.group(0) if date_match else (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                new_time = time_match.group(0) if time_match else "10:00"
                
                tool_calls.append({
                    "tool": "reschedule_appointment",
                    "args": {
                        "appointment_id": appointment_id,
                        "new_date": new_date,
                        "new_time": new_time
                    }
                })
        
        # Check for cancellation
        if any(kw in query_lower for kw in ["cancel", "cancel appointment"]):
            if appointment_id:
                tool_calls.append({
                    "tool": "cancel_appointment",
                    "args": {"appointment_id": appointment_id}
                })
        
        # Check for appointment details
        if any(kw in query_lower for kw in ["details", "information", "status"]) and appointment_id:
            tool_calls.append({
                "tool": "get_appointment_details",
                "args": {"appointment_id": appointment_id}
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
                if tool_name == "check_availability":
                    result = self.tools.check_availability(**args)
                elif tool_name == "schedule_appointment":
                    result = self.tools.schedule_appointment(**args)
                elif tool_name == "reschedule_appointment":
                    result = self.tools.reschedule_appointment(**args)
                elif tool_name == "cancel_appointment":
                    result = self.tools.cancel_appointment(**args)
                elif tool_name == "get_appointment_details":
                    result = self.tools.get_appointment_details(**args)
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

