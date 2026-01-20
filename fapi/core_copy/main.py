
from google.adk.runners import InMemoryRunner
from .orch_agent import get_orchestrator_agent
from google.genai import types
from google.adk.events import Event
import uuid
import asyncio
def run_coordinator(runner: InMemoryRunner, request: str,session_id : str = None, user_id : str = 'abc_u1'):
    """Runs the coordinator agent with a given request and delegates."""
    print(f"\n--- Running Coordinator with request: '{request}' ---")
    final_result = ""
    try:
        user_id = "user_123"
        if not session_id:
            session_id = str(uuid.uuid4())
        print(session_id)
        try:
            asyncio.run(runner.session_service.create_session(
                app_name=runner.app_name, user_id=user_id, session_id=session_id
            ))
        except Exception as e:
            try: asyncio.run(runner.session_service.get_session(
                app_name=runner.app_name, user_id=user_id, session_id=session_id
            ))
            except Exception as e:
                print(f"An error occurred while getting session: {e}")
                return f"An error occurred while getting session: {e}"
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role='user',
                parts=[types.Part(text=request)]
            ),
        ):
            if event.is_final_response() and event.content:
                # Try to get text directly from event.content to avoid iterating parts
                if hasattr(event.content, 'text') and event.content.text:
                     final_result = event.content.text
                elif event.content.parts:
                    # Fallback: Iterate through parts and extract text (might trigger warning)
                    text_parts = [part.text for part in event.content.parts if part.text]
                    final_result = "".join(text_parts)
                # Assuming the loop should break after the final response
                break

        print(f"Coordinator Final Response: {final_result}")
        return final_result
    except Exception as e:
        print(f"An error occurred while processing your request: {e}")
        return f"An error occurred while processing your request: {e}"

def main(runner : InMemoryRunner,request : str,session_id : str = "12345", user_id : str = 'user_123'):
    """Main function to run the ADK example."""
    # print("--- Google ADK Routing Example (ADK Auto-Flow Style) ---")
    # print("Note: This requires Google ADK installed and authenticated.")

    # runner = InMemoryRunner(get_orchestrator_agent())
    # Example Usage
    result_a = run_coordinator(runner, request,session_id , user_id)
    return result_a

# main(input("Enter your request: "))