from fastapi import APIRouter

from app.infrastructure.celery.tasks import reindex_all_task  # type: ignore

router: APIRouter = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reindex")
async def reindex_all() -> dict[str, str]:
    task = reindex_all_task.delay()  # type: ignore
    return {"status": "accepted", "task_id": task.id}
