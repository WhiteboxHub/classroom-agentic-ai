from google.adk.agents import Agent
from .util.prompts import APPOINTMENT_PROMPT
from tools.appointment_tools import appointment_tools

def get_appointment_agent() -> Agent:
    tools = appointment_tools().get_tools()
    return Agent(
        name="AppointmentAgent",
        model="gemini-2.0-flash",
        instruction=APPOINTMENT_PROMPT,
        description="Appointment agent that handles appointment-related queries.",
        tools=tools
    )