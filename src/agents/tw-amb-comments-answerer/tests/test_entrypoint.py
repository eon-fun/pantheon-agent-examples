import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

fake_ray = ModuleType("ray")
fake_serve = ModuleType("ray.serve")
fake_deployment = ModuleType("ray.serve.deployment")


# Mock the decorators
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


# Mock classes needed by your code
class FakeDeployment:
    pass


class FakeApplication:
    pass


fake_deployment.Deployment = FakeDeployment
fake_deployment.Application = FakeApplication

# Patch ray.serve
fake_serve.deployment = deployment_decorator_factory
fake_serve.ingress = ingress_decorator_factory
fake_serve.get_replica_context = MagicMock(return_value=MagicMock(replica_tag="test-replica"))
fake_serve.get_request_context = MagicMock(return_value=MagicMock(request_id="test-req-id"))

# Connect the modules
fake_ray.serve = fake_serve

sys.modules["ray"] = fake_ray
sys.modules["ray.serve"] = fake_serve
sys.modules["ray.serve.deployment"] = fake_deployment

# ---- Imports after patching ray.serve ----
from tw_amb_comments_answerer.entrypoint import (
    TwitterAmbassadorCommentsAnswerer,
    app,
)

# --- Fixtures ---


@pytest.fixture
def test_app():
    """Fixture for FastAPI test client."""
    client = TestClient(app)
    yield client


@pytest.fixture
def agent():
    """Fixture for direct agent class (no Ray Serve)."""
    return TwitterAmbassadorCommentsAnswerer()


# --- Tests ---


@pytest.mark.asyncio
async def test_handle_post(monkeypatch):
    """
    Test the POST /{goal} endpoint.
    Mocks all dependencies so no network calls are made.
    """
    # --- Patch all I/O dependencies ---
    with patch(
        "tw_amb_comments_answerer.entrypoint.TwitterAmbassadorCommentsAnswerer.answer_on_project_tweets_comments",
        new_callable=AsyncMock,
    ) as answer_mock:
        answer_mock.return_value = True

        # Patch FastAPI test client after all mocks
        from fastapi.testclient import TestClient

        client = TestClient(app)
        resp = client.post("/myuser.project.keywords.themes", json={})
        assert resp.status_code == 200
        # The FastAPI route returns None, as in the actual method
        # You can add assertions here for your expected API contract

        # Ensure the mock was called
        answer_mock.assert_called_once_with("myuser.project.keywords.themes")


@pytest.mark.asyncio
async def test_answer_on_project_tweets_comments_logic(monkeypatch, agent):
    """
    Directly test the agent's main method with all network/db dependencies mocked.
    """
    # Patch all external dependencies the method calls
    monkeypatch.setattr("tw_amb_comments_answerer.entrypoint.get_redis_db", MagicMock())
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.TwitterAuthClient.get_access_token", AsyncMock(return_value="token")
    )
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.search_tweets",
        AsyncMock(
            return_value=[
                MagicMock(id_str="123", full_text="Some tweet text"),
            ]
        ),
    )
    monkeypatch.setattr("tw_amb_comments_answerer.entrypoint.check_answer_is_needed", AsyncMock(return_value=True))
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.get_conversation_from_tweet",
        AsyncMock(return_value=["message1", "message2"]),
    )
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.create_conversation_string",
        MagicMock(return_value="Formatted conversation"),
    )
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.create_comment_to_comment", AsyncMock(return_value="Reply text")
    )
    monkeypatch.setattr("tw_amb_comments_answerer.entrypoint.ensure_delay_between_posts", AsyncMock())
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.create_post", AsyncMock(return_value={"data": {"id": "555"}})
    )

    # Patch the fake Redis DB object
    fake_db = MagicMock()
    fake_db.get_set.return_value = set()
    monkeypatch.setattr("tw_amb_comments_answerer.entrypoint.get_redis_db", MagicMock(return_value=fake_db))

    # Call method
    result = await agent.answer_on_project_tweets_comments("myuser.project.keyword1,keyword2.theme1,theme2")
    assert result is True


@pytest.mark.asyncio
async def test_answer_on_project_tweets_comments_no_tweets(monkeypatch, agent):
    """
    Test the 'no tweets to comment' branch.
    """
    monkeypatch.setattr("tw_amb_comments_answerer.entrypoint.get_redis_db", MagicMock())
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.TwitterAuthClient.get_access_token", AsyncMock(return_value="token")
    )
    monkeypatch.setattr(
        "tw_amb_comments_answerer.entrypoint.search_tweets", AsyncMock(return_value=[])
    )  # No comments found

    fake_db = MagicMock()
    fake_db.get_set.return_value = set()
    monkeypatch.setattr("tw_amb_comments_answerer.entrypoint.get_redis_db", MagicMock(return_value=fake_db))

    result = await agent.answer_on_project_tweets_comments("myuser.project.keywords.themes")
    assert result is False
