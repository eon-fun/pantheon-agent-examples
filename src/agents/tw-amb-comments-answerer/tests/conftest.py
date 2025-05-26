from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True, scope="session")
def patch_send_openai_request():
    with patch("tw_amb_comments_answerer.commands.send_openai_request", new_callable=AsyncMock) as mock_send:
        # You can set a default return_value if you like:
        mock_send.return_value = "Mocked openai reply"
        yield mock_send
