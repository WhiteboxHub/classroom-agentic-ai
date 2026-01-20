# claims , billing, appointment scheduling
# 
# 

from google.adk.agents import Agent
# from util.prompts import ORCHESTRATION_PROMPT
from .appointment_agent import get_appointment_agent
from .billing_agent import get_billing_agent
from .claims_agent import get_claims_agent
from .utils.prompts import ORCHESTRATION_PROMPT
def get_orchestrator_agent() -> Agent:
    """
    Creates the orchestration agent responsible only for routing user requests
    to the correct specialized agent.

    Args:
        claims_agent: Handles flight and hotel bookings
        billing_agent: Handles general information queries
        appointment_agent: Handles weather-related questions

    Returns:
        Agent: Configured orchestration agent
    """

    

    return Agent(
        name="Orchestrator",
        model="gemini-2.0-flash",
        instruction = ORCHESTRATION_PROMPT,
        description="Central routing agent that delegates requests to specialist agents.",
        sub_agents=[
            get_claims_agent(),
            get_billing_agent(),
            get_appointment_agent()
        ],
    )

root_agent = get_orchestrator_agent()