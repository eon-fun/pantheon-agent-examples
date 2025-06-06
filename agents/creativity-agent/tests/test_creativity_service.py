import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock environment variables before importing
os.environ.setdefault("CREATIVITY_API_ID", "test-id")
os.environ.setdefault("CREATIVITY_API_KEY", "test-key")


def ingress_decorator_factory(app):
    def _decorator(cls):
        return cls

    return _decorator


def deployment_decorator_factory(*args, **kwargs):
    def _decorator(cls):
        return cls

    if args and callable(args[0]):
        return args[0]
    return _decorator


serve_mock = MagicMock()
serve_mock.get_replica_context.return_value.replica_tag = "test-replica"
serve_mock.get_request_context.return_value.request_id = "test-req-id"
serve_mock.deployment = deployment_decorator_factory
serve_mock.ingress = ingress_decorator_factory

sys.modules["ray"] = MagicMock(serve=serve_mock)
sys.modules["ray.serve"] = serve_mock

# ---- Don't change! The mocks should come first ----
from src.creativity_agent.entrypoint import (  # noqa: E402
    AIShortRequest,
    CreativityService,
    LipsyncPreviewRequest,
    LipsyncRequest,
    LipsyncV2Request,
)


@pytest.fixture
def creativity_service():
    with patch("src.creativity_agent.entrypoint.httpx.AsyncClient") as mock_httpx_client:
        mock_client = AsyncMock()
        mock_httpx_client.return_value = mock_client
        service = CreativityService()
        service.http_client = mock_client
        yield service


# ---- Tests ----


class TestCreativityService:
    @pytest.mark.asyncio
    async def test_construct_url(self, creativity_service):
        url = creativity_service._construct_url("/some_endpoint/")
        assert url.endswith("/some_endpoint/")

    @pytest.mark.asyncio
    async def test_send_request_success(self, creativity_service):
        response_mock = MagicMock()
        response_mock.json.return_value = {"status": "ok"}
        response_mock.status_code = 200
        response_mock.raise_for_status = lambda: None

        creativity_service.http_client.request = AsyncMock(return_value=response_mock)
        response = await creativity_service._send_request("POST", "/foo", {"a": 1}, {"b": 2})
        assert response == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_send_request_http_error(self, creativity_service):
        import httpx

        response = httpx.Response(400, text="bad request")
        error = httpx.HTTPStatusError("error", request=None, response=response)
        creativity_service.http_client.request = AsyncMock(side_effect=error)
        with pytest.raises(Exception) as e:
            await creativity_service._send_request("POST", "/foo", {"a": 1}, {"b": 2})
        assert "Error from Creatify API" in str(e.value.detail) or "error" in str(e.value.detail).lower()

    @pytest.mark.asyncio
    async def test_send_request_network_error(self, creativity_service):
        import httpx

        creativity_service.http_client.request = AsyncMock(side_effect=httpx.RequestError("fail", request=None))
        with pytest.raises(Exception) as e:
            await creativity_service._send_request("POST", "/foo", {"a": 1}, {"b": 2})
        assert "Could not connect" in str(e.value.detail)

    @pytest.mark.asyncio
    async def test_handle_create_ai_short(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "foo", "status": "ok"})
        req = AIShortRequest(avatar_id="a", script="b")
        resp = await creativity_service.handle_create_ai_short(req)
        assert resp["status"] == "ok"

    @pytest.mark.asyncio
    async def test_handle_create_lipsync_task(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "lip", "status": "ok"})
        req = LipsyncRequest(text="hi", avatar_id="ava")
        resp = await creativity_service.handle_create_lipsync_task(req)
        assert resp["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_check(self, creativity_service):
        resp = await creativity_service.health_check()
        assert resp == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_handle_generate_ai_short_preview(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "foo", "status": "previewed"})
        req = AIShortRequest(avatar_id="a", script="b")
        resp = await creativity_service.handle_generate_ai_short_preview(req)
        assert resp["status"] == "previewed"

    @pytest.mark.asyncio
    async def test_handle_render_ai_short(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "foo", "status": "rendered"})
        resp = await creativity_service.handle_render_ai_short("foo")
        assert resp["status"] == "rendered"

    @pytest.mark.asyncio
    async def test_handle_get_ai_short_by_id(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "foo", "status": "ok"})
        resp = await creativity_service.handle_get_ai_short_by_id("foo")
        assert resp["status"] == "ok"

    @pytest.mark.asyncio
    async def test_handle_generate_lipsync_preview(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"output": "preview.mp4"})
        req = LipsyncPreviewRequest(text="hi", avatar_id="ava")
        resp = await creativity_service.handle_generate_lipsync_preview(req)
        assert resp["output"] == "preview.mp4"

    @pytest.mark.asyncio
    async def test_handle_render_lipsync_task(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"status": "rendered"})
        resp = await creativity_service.handle_render_lipsync_task("lipid")
        assert resp["status"] == "rendered"

    @pytest.mark.asyncio
    async def test_handle_get_lipsync_by_id(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "lipid", "status": "ok"})
        resp = await creativity_service.handle_get_lipsync_by_id("lipid")
        assert resp["status"] == "ok"

    @pytest.mark.asyncio
    async def test_handle_create_lipsync_v2_task(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "v2id", "status": "created"})
        req = LipsyncV2Request(text="hi", video_id="vid")
        resp = await creativity_service.handle_create_lipsync_v2_task(req)
        assert resp["status"] == "created"

    @pytest.mark.asyncio
    async def test_handle_generate_lipsync_v2_preview(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "v2id", "status": "previewed"})
        req = LipsyncV2Request(text="hi", video_id="vid")
        resp = await creativity_service.handle_generate_lipsync_v2_preview(req)
        assert resp["status"] == "previewed"

    @pytest.mark.asyncio
    async def test_handle_render_lipsync_v2_task(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "v2id", "status": "rendered"})
        resp = await creativity_service.handle_render_lipsync_v2_task("v2id")
        assert resp["status"] == "rendered"

    @pytest.mark.asyncio
    async def test_handle_get_lipsync_v2_by_id(self, creativity_service):
        creativity_service._send_request = AsyncMock(return_value={"id": "v2id", "status": "ok"})
        resp = await creativity_service.handle_get_lipsync_v2_by_id("v2id")
        assert resp["status"] == "ok"
