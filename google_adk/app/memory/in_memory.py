from google.adk.runners import InMemoryRunner
from core.logging import get_logger

logger = get_logger(__name__, log_file="logs/app.log")

def memory_runner(agent):
    logger.info("Memory Runner Started")
    runner = InMemoryRunner(agent)
    return runner
