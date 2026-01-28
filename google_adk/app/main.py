from core.logging import get_logger
from fastapi import FastAPI,Response,Body,Depends
from fastapi import Header,HTTPException
from memory.in_memory import memory_runner
from db.session import get_db
from agents.orch_agent import get_orchestrator_agent
from llm.client import run_client_coordiator
logger = get_logger(__name__, log_file="logs/app.log")
logger.info("App started")


from contextvars import ContextVar
current_user: ContextVar[dict | None] = ContextVar("current_user", default=None)

root_agent = get_orchestrator_agent()
runner = memory_runner(root_agent)
app = FastAPI()


def get_patient_id(patient_id : str = Header(...,alias="authtoken")) :

    print("PATIENT ID:", patient_id, flush=True)
    if not patient_id:
        raise HTTPException(status_code=401, detail="patient id missing in the header")
    current_user.set({"patient_id":patient_id})
    return {"patient_id": patient_id}

@app.get('/status_check')
async def health_check():
    status = {}
    try:
        status['in_memory_runner'] = runner
        status['db_status'] = get_db()
    except Exception as e:
        logger.error(f"{e}")
    return {'status' : status}


@app.post("/chat")
def chat(patient_id= Depends(get_patient_id),request: str = Body(...)):
    try:
        logger.info('/chat called')
        # print(patient_id)
        session_id = "baace8a8-0970-4e42-a3cd-47650e6f0531"
        request = request + f"patient_id = {patient_id}"
        res = run_client_coordiator(runner, request, session_id = session_id)
        # response.status_code = 200
        return {"response": res}
    except Exception as e:
        # response.status_code = 500
        return {"error": str(e)}