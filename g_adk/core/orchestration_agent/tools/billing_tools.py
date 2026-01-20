from google.adk.tools import FunctionTool

class billing_tools:
    @staticmethod
    def billing_inquiry(bill_number: str) -> str:
        """Handles billing inquiries.
        
        Args:
            bill_number: The bill number.
        
        Returns:
            The status of the bill.
        """
        return f"Billing inquiry for bill number {bill_number}"
    @staticmethod
    def payment_processing(bill_number: str, amount: float) -> str:
        """Processes payments.
        
        Args:
            bill_number: The bill number.
            amount: The amount to be paid.
            
        Returns:
            The status of the payment.
        """
        return f"Payment processed for bill number {bill_number} with amount {amount}"

    @staticmethod
    def billing_dispute(bill_number: str, reason: str) -> str:
        """Disputes a bill.
        
        Args:
            bill_number: The bill number.
            reason: The reason for the dispute.
            
        Returns:
            The status of the dispute.
        """
        return f"Billing dispute for bill number {bill_number} with reason {reason}"

    @staticmethod
    def billing_history(customer_id: str) -> str:
        """Retrieves billing history.
        
        Args:
            customer_id: The customer ID.
            
        Returns:
            The billing history for the customer.
        """
        return f"aka is asking for the billing history Billing history for customer {customer_id}"

    @staticmethod
    def billing_summary(customer_id: str) -> str:
        """Retrieves billing summary.
        
        Args:
            customer_id: The customer ID.
            
        Returns:
            The billing summary for the customer.
        """
        return f"test case billing summary is success sucess scucess Billing summary for customer {customer_id}"
    
    def get_tools(self):
        return [
            FunctionTool(self.billing_inquiry),
            FunctionTool(self.payment_processing),
            FunctionTool(self.billing_dispute),
            FunctionTool(self.billing_history),
            FunctionTool(self.billing_summary),
        ]