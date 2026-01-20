from google.adk.agents import Agent
from utils.prompts import BILLING_PROMPT
from tools.billing_tools import billing_tools

def get_billing_agent() -> Agent:
    tools = billing_tools().get_tools()
    return Agent(
        name="BillingAgent",
        model="gemini-2.0-flash",
        description= BILLING_PROMPT,
        tools=tools,
    )