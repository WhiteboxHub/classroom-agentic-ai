
from google.genai import types
from google.adk.runners import InMemoryRunner
from core.logging import get_logger
import uuid
import asyncio
logger = get_logger(__name__, log_file="logs/app.log")



def run_client_coordiator(
    runner: InMemoryRunner,
    request: str,
    session_id: str,
    user_id: str = "user_123",
):
    if not session_id:
        session_id = str(uuid.uuid4())

    try: 
        asyncio.run(runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        ))
    except Exception as e:
        logger.info('trying to find session')

        asyncio.run(runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        ))

    final_result = ""

    # events = await run_in_threadpool(
    #     runner.run,
    #     user_id=user_id,
    #     session_id=session_id,
    #     new_message=types.Content(
    #         role="user",
    #         parts=[types.Part(text=request)],
    #     ),
    # )

    # for event in events:
    for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role='user',
                parts=[types.Part(text=request)]
            ),
        ):
        logger.info("inside the for loop for event")
        if event.is_final_response() and event.content:
            if getattr(event.content, "text", None):
                final_result = event.content.text
            elif event.content.parts:
                final_result = "".join(
                    part.text for part in event.content.parts if part.text
                )
            break

    return final_result

# async def run_client_coordiator(
#     runner: InMemoryRunner,
#     request: str,
#     session_id: str,
#     user_id: str = 'abc_u1'
# ):
#     final_result = ""

#     try:
#         user_id = "user_123"
#         if not session_id:
#             logger.debug("new session id generated")
#             session_id = str(uuid.uuid4())

#         try:
#             await runner.session_service.get_session(
#                 app_name=runner.app_name,
#                 user_id=user_id,
#                 session_id=session_id
#             )

#         except Exception as e:
#             try:
#                 await runner.session_service.create_session(
#                     app_name=runner.app_name,
#                     user_id=user_id,
#                     session_id=session_id
#                 )
#             except Exception as e:
#                 logger.error(f"An error occurred while getting session: {e}")
#                 return f"An error occurred while getting session: {e}"
#         events = runner.run(
#             user_id=user_id,
#             session_id=session_id,
#             new_message=types.Content(
#                 role='user',
#                 parts=[types.Part(text=request)]
#             ),
#         )
#         for event in events:
#             logger.info('aka here')
            
#             if event.is_final_response() and event.content:
#                 if hasattr(event.content, 'text') and event.content.text:
#                     final_result = event.content.text
#                 elif event.content.parts:
#                     text_parts = [
#                         part.text for part in event.content.parts if part.text
#                     ]
#                     final_result = "".join(text_parts)
#                 break

#         logger.info(f"Coordinator Final Response: {final_result}")
#         return final_result

#     except Exception as e:
#         logger.error(f"An error occurred while processing your request: {e}")
#         return f"An error occurred while processing your request: {e}"


# async def run_client_coordiator(runner:InMemoryRunner, request : str, session_id : str, user_id:str = 'abc_u1' ):

#     final_result = ""
#     try:
        
#         if not session_id:
#             logger.debug(f"new session id generated")
#             session_id = str(uuid.uuid4())

#         try:
#             asyncio.run(runner.session_service.get_session(
#                 app_name=runner.app_name,
#                 user_id= user_id,
#                 session_id= session_id
#             ))
            
#         except Exception as e:
#             try: 
#                 asyncio.run(runner.session_service.get_session(
#                 app_name=runner.app_name,
#                     user_id=user_id,
#                     session_id=session_id
#                     ))
#             except Exception as e:
#                 logger.error(f"An error occurred while getting session: {e}")
#                 return f"An error occurred while getting session: {e}"
        
#         for event in runner.run(
#                         user_id=user_id,
#                         session_id=session_id,
#                         new_message=types.Content(
#                             role='user',
#                             parts=[types.Part(text=request)]
#                         ),
#                     ):
            
#             if event.is_final_response() and event.content:
#             # Try to get text directly from event.content to avoid iterating parts
#                 if hasattr(event.content, 'text') and event.content.text:
#                     final_result = event.content.text
#                 elif event.content.parts:
#                     # Fallback: Iterate through parts and extract text (might trigger warning)
#                     text_parts = [part.text for part in event.content.parts if part.text]
#                     final_result = "".join(text_parts)
#             # Assuming the loop should break after the final response
#                 break

#         logger.info(f"Coordinator Final Response: {final_result}")
#         return final_result
#     except Exception as e:
#         logger.error(f"An error occurred while processing your request: {e}")
#         return f"An error occurred while processing your request: {e}"