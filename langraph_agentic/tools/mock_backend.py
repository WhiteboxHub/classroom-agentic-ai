"""
Mock Backend
Provides mock implementations of backend services.
No real external APIs are called.
"""
from typing import Dict, Any, Optional
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MockBackend:
    """
    Mock backend services.
    Provides deterministic mock responses for testing.
    """
    
    @staticmethod
    def mock_claims_api(claim_number: str) -> Dict[str, Any]:
        """Mock claims API response"""
        mock_data = {
            "CLM-12345": {"status": "approved", "amount": 5000.00},
            "CLM-67890": {"status": "pending", "amount": 2500.00},
            "CLM-11111": {"status": "denied", "amount": 1000.00}
        }
        return mock_data.get(claim_number, {"status": "not_found"})
    
    @staticmethod
    def mock_billing_api(account_id: str) -> Dict[str, Any]:
        """Mock billing API response"""
        mock_data = {
            "ACC-12345": {"balance": 250.00, "status": "current"},
            "ACC-67890": {"balance": 0.00, "status": "paid"}
        }
        return mock_data.get(account_id, {"balance": 0.00, "status": "not_found"})
    
    @staticmethod
    def mock_scheduling_api(date: str) -> Dict[str, Any]:
        """Mock scheduling API response"""
        return {
            "date": date,
            "available_slots": ["09:00", "10:30", "14:00", "15:30"],
            "status": "available"
        }
    
    @staticmethod
    def mock_payment_processor(
        account_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Mock payment processor"""
        transaction_id = f"TXN-{random.randint(100000, 999999)}"
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "status": "processed",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def mock_identity_verification(customer_id: str) -> Dict[str, Any]:
        """Mock identity verification"""
        return {
            "verified": True,
            "customer_id": customer_id,
            "verification_level": "standard",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def mock_policy_lookup(policy_number: str) -> Dict[str, Any]:
        """Mock policy lookup"""
        return {
            "policy_number": policy_number,
            "status": "active",
            "coverage": {
                "medical": True,
                "dental": True,
                "vision": True
            },
            "effective_date": "2024-01-01",
            "expiration_date": "2024-12-31"
        }

