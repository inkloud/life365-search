from fastapi import APIRouter

router: APIRouter = APIRouter(tags=["search"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
