import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.logging import configure_logging
from app.routers import admin, search
from app.routers.errors import ApiError
from app.services.exceptions import InvalidSearchRequestError, SearchUnavailableError
from app.settings import Settings, get_settings

settings: Settings = get_settings()
configure_logging(settings.debug)

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


@app.middleware("http")
async def add_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
