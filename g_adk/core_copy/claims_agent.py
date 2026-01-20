from google.adk.agents import Agent
from utils.prompts import CLAIMS_PROMPT
from tools.claims_tools import claims_tools


def get_claims_agent() -> Agent:
    tools = claims_tools().get_tools()
    return Agent(
        name="ClaimsAgent",
        model="gemini-2.0-flash",
        description=CLAIMS_PROMPT,
        tools=tools,
    )