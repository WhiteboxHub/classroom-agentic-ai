"""
Safety Sentinel Agent
Validates agent responses before returning to users.
Implements human-in-the-loop flagging.
"""
from typing import List
from pydantic import BaseModel
from app.state import GraphState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import logging

logger = logging.getLogger(__name__)


class SafetyCheck(BaseModel):
    """Result of safety validation"""
    requires_human_review: bool
    flags: List[str]
    risk_score: float  # 0.0 to 1.0


class SafetySentinel:
    """
    Safety Sentinel - validates all agent responses.
    Flags responses that require human review.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.0,  # Deterministic for safety
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Safety Sentinel for a customer service system.
Your job is to validate agent responses for:
1. Accuracy - Is the information correct?
2. Appropriateness - Is the tone and content appropriate?
3. Safety - Are there any security or compliance concerns?
4. Completeness - Is the response complete and helpful?

Flag responses that:
- Contain sensitive information that shouldn't be shared
- Have inappropriate tone or language
- Provide incorrect or misleading information
- Require human judgment or escalation
- Have high financial impact (large payments, claim approvals)
- Show signs of fraud or suspicious activity

Respond with:
- "SAFE" if the response is safe to return
- "FLAG:<reason>" if it needs human review, with the reason

Examples:
- "SAFE" - Normal response, no issues
- "FLAG:High financial impact - processing $10,000 payment"
- "FLAG:Inappropriate tone detected"
- "FLAG:Potential fraud indicators"
- "FLAG:Requires policy exception"""),
            ("user", """Agent: {agent_name}
User Query: {user_query}
Agent Response: {agent_response}

Evaluate this response and determine if it's safe to return to the user.""")
        ])
    
    def validate(self, state: GraphState) -> SafetyCheck:
        """
        Validate the agent response.
        Returns safety check result.
        """
        agent_response = state.get("agent_response", "")
        user_query = state.get("user_query", "")
        agent_name = state.get("agent_name", "unknown")
        
        if not agent_response:
            return SafetyCheck(
                requires_human_review=False,
                flags=[],
                risk_score=0.0
            )
        
        try:
            # Use LLM for safety validation
            chain = self.prompt | self.llm
            validation_result = chain.invoke({
                "agent_name": agent_name,
                "user_query": user_query,
                "agent_response": agent_response
            })
            
            validation_text = validation_result.content.strip()
            
            # Parse validation result
            requires_review = False
            flags = []
            risk_score = 0.0
            
            if validation_text.startswith("FLAG:"):
                requires_review = True
                flag_reason = validation_text.replace("FLAG:", "").strip()
                flags.append(flag_reason)
                risk_score = 0.7  # Medium-high risk
            
            # Additional rule-based checks
            rule_flags = self._rule_based_checks(agent_response, user_query)
            if rule_flags:
                requires_review = True
                flags.extend(rule_flags)
                risk_score = max(risk_score, 0.5)
            
            logger.info(f"Safety validation - Review required: {requires_review}, Flags: {flags}")
            
            return SafetyCheck(
                requires_human_review=requires_review,
                flags=flags,
                risk_score=risk_score
            )
        
        except Exception as e:
            logger.error(f"Error in safety validation: {e}", exc_info=True)
            # On error, flag for review to be safe
            return SafetyCheck(
                requires_human_review=True,
                flags=[f"Safety validation error: {str(e)}"],
                risk_score=0.5
            )
    
    def _rule_based_checks(self, response: str, query: str) -> List[str]:
        """Additional rule-based safety checks"""
        flags = []
        response_lower = response.lower()
        query_lower = query.lower()
        
        # Check for high-value transactions
        import re
        amount_matches = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', response)
        for amount_str in amount_matches:
            try:
                amount = float(amount_str.replace(",", ""))
                if amount > 5000:
                    flags.append(f"High-value transaction detected: ${amount:,.2f}")
            except:
                pass
        
        # Check for sensitive keywords
        sensitive_keywords = [
            "ssn", "social security", "credit card", "password", "pin",
            "full refund", "immediately approve", "bypass", "override"
        ]
        
        for keyword in sensitive_keywords:
            if keyword in response_lower:
                flags.append(f"Sensitive keyword detected: {keyword}")
        
        # Check for inappropriate language
        inappropriate_words = ["damn", "hell", "stupid", "idiot"]
        for word in inappropriate_words:
            if word in response_lower:
                flags.append(f"Inappropriate language detected")
                break
        
        return flags

