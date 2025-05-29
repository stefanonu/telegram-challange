from fastapi import Depends, BackgroundTasks, HTTPException, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
from app.db import get_db
from app.model import JobRecord

app = FastAPI()
worker_locks = [asyncio.Lock() for _ in range(3)]

class JobRequestIn(BaseModel):
    request_id: str
    payload: Dict[str, Any]

class JobResponseOut(BaseModel):
    status: str
    worker_id: int | None = None
    result: str | None = None

@app.post("/process-request", response_model=JobResponseOut)
async def process_request(
    request: JobRequestIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> JobResponseOut:
    record = JobRecord(
        request_id=request.request_id,
        payload=request.payload,
        status="in_progress"
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(JobRecord).filter_by(request_id=request.request_id).first()
        return JobResponseOut(
            status="duplicate",
            worker_id=existing.worker_id,
            result=existing.result
        )

    for i, lock in enumerate(worker_locks):
        if not lock.locked():
            await lock.acquire()
            background_tasks.add_task(run_worker, i, request.request_id, db)
            return JobResponseOut(
                status="accepted",
                worker_id=i,
                result=None
            )

    raise HTTPException(status_code=429, detail="All workers are busy")

async def run_worker(worker_id: int, request_id: str, db: Session) -> None:
    try:
        await asyncio.sleep(5)  # simulate work
        result = f"Processed by worker {worker_id}"

        job = db.query(JobRecord).filter_by(request_id=request_id).first()
        job.worker_id = worker_id
        job.result = result
        job.status = "done"
        db.commit()
    finally:
        worker_locks[worker_id].release()
