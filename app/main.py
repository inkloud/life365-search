from fastapi import FastAPI

from app.routers import admin, search
from app.settings import settings

app: FastAPI = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(search.router)
app.include_router(admin.router)
