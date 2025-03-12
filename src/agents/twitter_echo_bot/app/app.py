from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from app.routers.tracked_accounts import tracked_accounts_router
from app.routers.user import user_router
from config.config import config
from agents_tools_logger.main import log


@asynccontextmanager
async def lifespan(application: FastAPI):
    log.info("Application startup")

    yield
    log.info("Application shutdown")


ROUTERS: List[APIRouter] = [user_router,
                            tracked_accounts_router]


app = FastAPI(
    lifespan=lifespan,
    title=config.app_title,
    description=config.app_description,
    version=config.app_version,
    docs_url=f"/{config.app_docs_url}/docs",
    redoc_url=f"/{config.app_docs_url}/redoc",
    openapi_url=f"/{config.app_docs_url}/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.fastapi.allowed_origins,
    allow_credentials=config.fastapi.allowed_credentials,
    allow_methods=config.fastapi.allowed_methods,
    allow_headers=config.fastapi.allowed_headers,
)
for router in ROUTERS:
    app.include_router(router)


@app.get("/ping")
async def ping():
    return {"status": "ok"}
