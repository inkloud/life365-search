from fastapi import APIRouter

router: APIRouter = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reindex")
def reindex_all() -> dict[str, str]:
    return {"status": "accepted"}
