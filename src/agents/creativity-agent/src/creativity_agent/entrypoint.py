import logging
import traceback
from typing import Any, Dict, Optional

import httpx
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel
from ray import serve

from .config import Settings, get_settings


class StatusResponse(BaseModel):
    status: str
    id: Optional[str] = None
    output: Optional[str] = None
    cost: Optional[float] = None
    message: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

class LipsyncRequest(BaseModel):
    text: str
    avatar_id: str
    voice_id: Optional[str] = None
    webhook_url: Optional[str] = None
    response_format: Optional[str] = 'mp4'
    extra: Optional[Dict[str, Any]] = None

class LipsyncResponse(BaseModel):
    id: str
    status: str
    output: Optional[str] = None
    cost: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None

class LipsyncPreviewRequest(BaseModel):
    text: str
    avatar_id: str
    voice_id: Optional[str] = None

class LipsyncPreviewResponse(BaseModel):
    output: str
    cost: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None

class LipsyncV2Request(BaseModel):
    text: str
    video_id: str
    voice_id: Optional[str] = None
    webhook_url: Optional[str] = None
    response_format: Optional[str] = 'mp4'
    extra: Optional[Dict[str, Any]] = None

class LipsyncV2Response(BaseModel):
    id: str
    status: str
    output: Optional[str] = None
    cost: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None

class AIShortRequest(BaseModel):
    avatar_id: str
    script: str
    voice_id: Optional[str] = None
    music_id: Optional[str] = None
    template_id: Optional[str] = None
    webhook_url: Optional[str] = None
    response_format: Optional[str] = 'mp4'
    extra: Optional[Dict[str, Any]] = None

class AIShortResponse(BaseModel):
    id: str
    status: str
    output: Optional[str] = None
    cost: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None


settings_for_logging = get_settings()
log_level = getattr(logging, settings_for_logging.log_level.upper(), logging.INFO)
logger = logging.getLogger("ray.serve")
logger.setLevel(log_level)
if not logger.hasHandlers():
     handler = logging.StreamHandler()
     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     handler.setFormatter(formatter)
     logger.addHandler(handler)

logger.info(f"Logger configured with level: {settings_for_logging.log_level.upper()}")


app = FastAPI(
    title="Creativity Agent",
    description="HTTP interface for the Creatify API, running as a Ray Serve deployment.",

)

@serve.deployment()
@serve.ingress(app)
class CreativityService:
    def __init__(self):
        self.settings: Settings = get_settings()
        logger.info(f"Initializing CreativityService replica '{serve.get_replica_context().replica_tag}'...")
        logger.info(f"Creatify API Base URL: {self.settings.creativity_base_url}")
        self.headers = {
            "X-API-ID": self.settings.creativity_api_id,
            "X-API-KEY": self.settings.creativity_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.http_client = httpx.AsyncClient(
             headers=self.headers,
             timeout=60.0
        )
        logger.info(f"CreativityService replica '{serve.get_replica_context().replica_tag}' initialized.")

    async def __del__(self):
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()
        logger.info(f"CreativityService replica '{serve.get_replica_context().replica_tag}' shut down.")

    def _construct_url(self, endpoint: str) -> str:
        base = str(self.settings.creativity_base_url).rstrip('/')
        endpoint = endpoint if endpoint.startswith('/') else '/' + endpoint
        return f"{base}{endpoint}"

    async def _send_request(
        self, method: str, endpoint: str, json_data: Optional[dict] = None, params: Optional[dict] = None
    ) -> dict:
        url = self._construct_url(endpoint)
        request_id = serve.get_request_context().request_id
        logger.info(f"[Req ID: {request_id}] Sending {method} request to {url}")
        logger.debug(f"[Req ID: {request_id}] Params: {params}, JSON Body: {json_data}")

        try:
            response = await self.http_client.request(
                method, url, json=json_data, params=params
            )
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"[Req ID: {request_id}] Received successful response from {url}. Status: {response.status_code}")
            logger.debug(f"[Req ID: {request_id}] Response JSON: {response_json}")
            return response_json
        except httpx.HTTPStatusError as e:
            error_body = "<no response body>"
            try:
                 error_body = e.response.text
            except Exception:
                 pass
            logger.error(
                f"[Req ID: {request_id}] HTTP error from Creatify API ({url}): {e.response.status_code} - Body: {error_body}"
            )
            logger.debug(traceback.format_exc())
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error from Creatify API: {e.response.status_code}. Response: {error_body}"
            )
        except httpx.RequestError as e:
            logger.error(f"[Req ID: {request_id}] Network error connecting to Creatify API ({url}): {e}")
            logger.debug(traceback.format_exc())
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to Creatify API: {e}"
            )
        except Exception as e:
            logger.exception(f"[Req ID: {request_id}] Unexpected error during request to {url}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error processing Creatify request: {type(e).__name__}"
            )


    @app.post("/ai_shorts/", response_model=AIShortResponse, tags=["AI Shorts"], summary="Create AI Short Task")
    async def handle_create_ai_short(self, request_body: AIShortRequest = Body(...)) -> dict:
        return await self._send_request(
            "POST",
            endpoint="/ai_shorts/",
            json_data=request_body.model_dump(exclude_unset=True)
        )

    @app.post("/ai_shorts/preview/", response_model=AIShortResponse, tags=["AI Shorts"], summary="Generate AI Short Preview")
    async def handle_generate_ai_short_preview(self, request_body: AIShortRequest = Body(...)) -> dict:
        return await self._send_request(
            "POST",
            endpoint="/ai_shorts/preview/",
            json_data=request_body.model_dump(exclude_unset=True)
        )

    @app.post("/ai_shorts/{short_id}/render/", response_model=AIShortResponse, tags=["AI Shorts"], summary="Render AI Short Task")
    async def handle_render_ai_short(self, short_id: str) -> dict:
        return await self._send_request("POST", endpoint=f"/ai_shorts/{short_id}/render/")

    @app.get("/ai_shorts/{short_id}/", response_model=AIShortResponse, tags=["AI Shorts"], summary="Get AI Short Task Status")
    async def handle_get_ai_short_by_id(self, short_id: str) -> dict:
        return await self._send_request("GET", endpoint=f"/ai_shorts/{short_id}/")


    @app.post("/lipsyncs/", response_model=LipsyncResponse, tags=["Lipsync v1"], summary="Create Lipsync v1 Task")
    async def handle_create_lipsync_task(self, request_body: LipsyncRequest = Body(...)) -> dict:
        return await self._send_request(
            "POST",
            endpoint="/lipsyncs/",
            json_data=request_body.model_dump(exclude_unset=True)
        )

    @app.post("/lipsyncs/preview/", response_model=LipsyncPreviewResponse, tags=["Lipsync v1"], summary="Generate Lipsync v1 Preview")
    async def handle_generate_lipsync_preview(self, request_body: LipsyncPreviewRequest = Body(...)) -> dict:
        return await self._send_request(
            "POST",
            endpoint="/lipsyncs/preview/",
            json_data=request_body.model_dump(exclude_unset=True)
        )

    @app.post("/lipsyncs/{lipsync_id}/render/", response_model=StatusResponse, tags=["Lipsync v1"], summary="Render Lipsync v1 Task")
    async def handle_render_lipsync_task(self, lipsync_id: str) -> dict:
        return await self._send_request("POST", endpoint=f"/lipsyncs/{lipsync_id}/render/")

    @app.get("/lipsyncs/{lipsync_id}/", response_model=LipsyncResponse, tags=["Lipsync v1"], summary="Get Lipsync v1 Task Status")
    async def handle_get_lipsync_by_id(self, lipsync_id: str) -> dict:
        return await self._send_request("GET", endpoint=f"/lipsyncs/{lipsync_id}/")


    @app.post("/lipsyncs_v2/", response_model=LipsyncV2Response, tags=["Lipsync v2"], summary="Create Lipsync v2 Task")
    async def handle_create_lipsync_v2_task(self, request_body: LipsyncV2Request = Body(...)) -> dict:
        return await self._send_request(
            "POST",
            endpoint="/lipsyncs_v2/",
            json_data=request_body.model_dump(exclude_unset=True)
        )

    @app.post("/lipsyncs_v2/preview/", response_model=LipsyncV2Response, tags=["Lipsync v2"], summary="Generate Lipsync v2 Preview")
    async def handle_generate_lipsync_v2_preview(self, request_body: LipsyncV2Request = Body(...)) -> dict:
        return await self._send_request(
            "POST",
            endpoint="/lipsyncs_v2/preview/",
            json_data=request_body.model_dump(exclude_unset=True)
        )

    @app.post("/lipsyncs_v2/{lipsync_id}/render/", response_model=LipsyncV2Response, tags=["Lipsync v2"], summary="Render Lipsync v2 Task")
    async def handle_render_lipsync_v2_task(self, lipsync_id: str) -> dict:
        return await self._send_request("POST", endpoint=f"/lipsyncs_v2/{lipsync_id}/render/")

    @app.get("/lipsyncs_v2/{lipsync_id}/", response_model=LipsyncV2Response, tags=["Lipsync v2"], summary="Get Lipsync v2 Task Status")
    async def handle_get_lipsync_v2_by_id(self, lipsync_id: str) -> dict:
        return await self._send_request("GET", endpoint=f"/lipsyncs_v2/{lipsync_id}/")


    @app.get("/_health/", tags=["Health"], summary="Health Check")
    async def health_check(self) -> Dict[str, str]:
        logger.debug("Health check endpoint called.")
        return {"status": "ok"}


def agent_builder(args: Optional[Dict[str, Any]] = None) -> serve.handle.DeploymentHandle:
    runtime_args = args or {}
    logger.info(f"Building CreativityService deployment with runtime args: {runtime_args}")


    logger.info("Binding deployment 'CreativityService'...")

    return CreativityService.bind()
