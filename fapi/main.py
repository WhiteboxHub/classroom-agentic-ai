from fastapi import FastAPI,Response,Body
from core_copy.main import main
from google.adk.runners import InMemoryRunner
from core_copy.main import get_orchestrator_agent
app = FastAPI()

runner = InMemoryRunner(get_orchestrator_agent())
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(request: str = Body(...)):
    try:
        session_id = "baace8a8-0970-4e42-a3cd-47650e6f0531"
        res = main(runner, request, session_id = session_id)
        # response.status_code = 200
        return {"response": res}
    except Exception as e:
        # response.status_code = 500
        return {"error": str(e)}


