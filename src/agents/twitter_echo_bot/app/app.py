from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from app.routers.tracked_accounts import tracked_accounts_router
from app.routers.user import user_router
from config.config import config
from custom_logs.custom_logs import log


@asynccontextmanager
async def lifespan(application: FastAPI):
    log.info("Application startup")

    yield
    log.info("Application shutdown")


ROUTERS: List[APIRouter] = [user_router,
                            tracked_accounts_router]


app = FastAPI(
    lifespan=lifespan,
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    docs_url=f"/{config.APP_DOCS_URL}/docs",
    redoc_url=f"/{config.APP_DOCS_URL}/redoc",
    openapi_url=f"/{config.APP_DOCS_URL}/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FASTAPI.ALLOWED_ORIGINS,
    allow_credentials=config.FASTAPI.ALLOWED_CREDENTIALS,
    allow_methods=config.FASTAPI.ALLOWED_METHODS,
    allow_headers=config.FASTAPI.ALLOWED_HEADERS,
)
for router in ROUTERS:
    app.include_router(router)


@app.get("/ping")
async def ping():
    return {"status": "ok"}
