import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from services.llm_inference_client import LLMInferenceError, chat_completion


@patch("services.llm_inference_client.get_config")
@patch("services.llm_inference_client.urllib.request.urlopen")
def test_chat_completion_returns_assistant_text(mock_urlopen, mock_get_config):
    mock_get_config.return_value = SimpleNamespace(
        LLM_API_BASE_URL="http://infer.example/v1",
        LLM_MODEL="test-model",
        LLM_API_KEY="secret",
        LLM_TIMEOUT_SECONDS=30,
        LLM_MAX_TOKENS=256,
    )
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(
        {"choices": [{"message": {"content": "  summarized  "}}]}
    ).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    out = chat_completion([{"role": "user", "content": "hi"}], max_tokens=10)

    assert out == "summarized"
    req = mock_urlopen.call_args[0][0]
    assert req.full_url == "http://infer.example/v1/chat/completions"


@patch("services.llm_inference_client.get_config")
@patch("services.llm_inference_client.urllib.request.urlopen")
def test_chat_completion_empty_choices_raises(mock_urlopen, mock_get_config):
    mock_get_config.return_value = SimpleNamespace(
        LLM_API_BASE_URL="http://infer.example/v1",
        LLM_MODEL="m",
        LLM_API_KEY="",
        LLM_TIMEOUT_SECONDS=5,
        LLM_MAX_TOKENS=10,
    )
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"choices": []}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    try:
        chat_completion([{"role": "user", "content": "x"}])
    except LLMInferenceError as exc:
        assert "empty choices" in str(exc).lower()
    else:
        raise AssertionError("expected LLMInferenceError")
