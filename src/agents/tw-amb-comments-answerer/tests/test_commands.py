import pytest
from tw_amb_comments_answerer import commands


@pytest.mark.asyncio
async def test_add_blank_lines(patch_send_openai_request):
    patch_send_openai_request.return_value = "Paragraph 1\n\nParagraph 2"
    result = await commands.add_blank_lines("Some input")
    assert "Paragraph" in result
    patch_send_openai_request.assert_awaited()


@pytest.mark.asyncio
async def test_check_answer_is_needed_true(patch_send_openai_request):
    patch_send_openai_request.return_value = "True"
    needed = await commands.check_answer_is_needed("hi", "myuser")
    assert needed is True


@pytest.mark.asyncio
async def test_check_answer_is_needed_false(patch_send_openai_request):
    patch_send_openai_request.return_value = "False"
    needed = await commands.check_answer_is_needed("hi", "myuser")
    assert needed is False


@pytest.mark.asyncio
async def test_create_comment_to_comment(patch_send_openai_request):
    # The side effect list simulates responses for each internal OpenAI call.
    patch_send_openai_request.side_effect = [
        "Raw result",  # For send_openai_request in create_comment_to_comment
        "Formatted result",  # For format_text's add_blank_lines
    ]
    result = await commands.create_comment_to_comment(
        comment_text="Test comment", keywords=["AI", "Tech"], themes=["Innovation"], my_username="bob"
    )
    assert "Formatted" in result or "Raw" in result
    assert patch_send_openai_request.await_count >= 2
