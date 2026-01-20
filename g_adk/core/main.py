from google.adk.runners import InMemoryRunner
from orchestration_agent.agents import get_orchestrator_agent

def run_coordinator(runner: InMemoryRunner, request: str,session_id : str = "12345", user_id : str = 'abc_u1'):
    """Runs the coordinator agent with a given request and delegates."""
    print(f"\n--- Running Coordinator with request: '{request}' ---")
    final_result = ""
    try:
        # user_id = "user_123"
        # session_id = str(uuid.uuid4())
        runner.session_service.create_session(
            app_name=runner.app_name, user_id=user_id, session_id=session_id
        )

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

def main(request : str,session_id : str = "12345", user_id : str = 'abc_u1'):
    """Main function to run the ADK example."""
    print("--- Google ADK Routing Example (ADK Auto-Flow Style) ---")
    print("Note: This requires Google ADK installed and authenticated.")

    runner = InMemoryRunner(get_orchestrator_agent())
    # Example Usage
    result_a = run_coordinator(runner, request,session_id , user_id)
    return result_a

main(input("Enter your request: "))