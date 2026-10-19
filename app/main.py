import logging
import time

from fastapi import FastAPI, Request

from app.routers import tasks, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.requests")

app = FastAPI(title="Task Manager")


@app.middleware("http")
async def process_time_middleware(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - started
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    logger.info(
        "%s %s %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed * 1000,
    )
    return response


app.include_router(users.router)
app.include_router(tasks.router)
