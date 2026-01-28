from fastapi import FastAPI,Response,Body,Depends
from core.main import main
from google.adk.runners import InMemoryRunner
from core.main import get_orchestrator_agent
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
from contextvars import ContextVar

current_user: ContextVar[dict | None] = ContextVar("current_user", default=None)

from fastapi import Header,HTTPException

def get_patient_id(patient_id : str = Header(...,alias="authtoken")) :

    print("PATIENT ID:", patient_id, flush=True)
    if not patient_id:
        raise HTTPException(status_code=401, detail="patient id missing in the header")
    current_user.set({"patient_id":patient_id})
    return {"patient_id": patient_id}

load_dotenv()
app = FastAPI()

runner = InMemoryRunner(get_orchestrator_agent())
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(patient_id= Depends(get_patient_id),request: str = Body(...)):
    try:
        print('/chat called')
        print(patient_id)
        session_id = "baace8a8-0970-4e42-a3cd-47650e6f0531"
        res = main(runner, request, session_id = session_id)
        # response.status_code = 200
        return {"response": res}
    except Exception as e:
        # response.status_code = 500
        return {"error": str(e)}


