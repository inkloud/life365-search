from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import admin, search
from app.routers.errors import ApiError
from app.services.exceptions import InvalidSearchRequestError, SearchUnavailableError
from app.settings import Settings, get_settings

settings: Settings = get_settings()

app: FastAPI = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(search.router)
app.include_router(admin.router)


@app.exception_handler(SearchUnavailableError)
async def search_unavailable_handler(request: Request, exc: SearchUnavailableError):
    return JSONResponse(
        status_code=503,
        content=ApiError(
            error="search_unavailable", message="Search service temporarily unavailable"
        ).model_dump(),
    )


@app.exception_handler(InvalidSearchRequestError)
async def invalid_search_handler(request: Request, exc: InvalidSearchRequestError):
    return JSONResponse(
        status_code=400,
        content=ApiError(error="invalid_request", message=str(exc)).model_dump(),
    )
