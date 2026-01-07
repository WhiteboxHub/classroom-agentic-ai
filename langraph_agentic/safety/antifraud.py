"""
Anti-Fraud Module
Detects potential fraud patterns in user queries and agent interactions.
"""
from typing import Dict, Any, List
from app.state import GraphState
import logging
import re

logger = logging.getLogger(__name__)


class AntiFraud:
    """
    Anti-fraud detection system.
    Analyzes queries and agent responses for fraud indicators.
    """
    
    def __init__(self):
        self.fraud_patterns = [
            r"urgent.*payment",
            r"wire.*transfer",
            r"gift.*card",
            r"bitcoin|crypto",
            r"immediately.*refund",
            r"account.*hacked",
            r"suspended.*account",
            r"verify.*identity.*now"
        ]
        self.suspicious_keywords = [
            "urgent", "immediately", "verify now", "account locked",
            "suspended", "hacked", "fraudulent", "unauthorized"
        ]
    
    def analyze(self, state: GraphState) -> Dict[str, Any]:
        """
        Analyze the state for fraud indicators.
        
        Returns:
            Dict with fraud analysis results
        """
        user_query = state.get("user_query", "").lower()
        agent_response = state.get("agent_response", "").lower()
        
        fraud_score = 0.0
        indicators = []
        
        # Check query for fraud patterns
        for pattern in self.fraud_patterns:
            if re.search(pattern, user_query, re.IGNORECASE):
                fraud_score += 0.2
                indicators.append(f"Fraud pattern detected: {pattern}")
        
        # Check for suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword in user_query:
                fraud_score += 0.1
                indicators.append(f"Suspicious keyword: {keyword}")
        
        # Check for multiple urgent requests
        urgent_count = user_query.count("urgent") + user_query.count("immediately")
        if urgent_count > 2:
            fraud_score += 0.2
            indicators.append("Multiple urgent requests detected")
        
        # Check for unusual payment methods
        unusual_payment = any(term in user_query for term in ["wire", "gift card", "bitcoin", "crypto"])
        if unusual_payment:
            fraud_score += 0.3
            indicators.append("Unusual payment method requested")
        
        # Normalize fraud score to 0-1
        fraud_score = min(fraud_score, 1.0)
        
        is_suspicious = fraud_score > 0.5
        
        logger.info(f"Anti-fraud analysis - Score: {fraud_score}, Suspicious: {is_suspicious}")
        
        return {
            "fraud_score": fraud_score,
            "is_suspicious": is_suspicious,
            "indicators": indicators,
            "requires_review": is_suspicious
        }
    
    def should_flag(self, state: GraphState) -> bool:
        """Quick check if state should be flagged for fraud review"""
        analysis = self.analyze(state)
        return analysis["is_suspicious"]

