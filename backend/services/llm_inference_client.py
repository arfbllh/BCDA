"""HTTP client for OpenAI-compatible chat completions (GPU/LLM inference service)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from core.config import get_config


class LLMInferenceError(Exception):
    """Raised when the remote inference service returns an error or invalid payload."""


def chat_completion(messages: list[dict], *, max_tokens: int | None = None) -> str:
    """
    POST /chat/completions to LLM_API_BASE_URL (e.g. https://api.openai.com/v1 or http://ollama:11434/v1).
    """
    cfg = get_config()
    base = (cfg.LLM_API_BASE_URL or "").strip().rstrip("/")
    if not base:
        raise LLMInferenceError("LLM_API_BASE_URL is not set")

    url = f"{base}/chat/completions"
    body = {
        "model": cfg.LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens if max_tokens is not None else cfg.LLM_MAX_TOKENS,
    }
    headers = {"Content-Type": "application/json"}
    if cfg.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {cfg.LLM_API_KEY}"

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=cfg.LLM_TIMEOUT_SECONDS) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise LLMInferenceError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise LLMInferenceError(str(exc.reason)) from exc

    choices = raw.get("choices") or []
    if not choices:
        raise LLMInferenceError("empty choices in LLM response")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if content is None:
        raise LLMInferenceError("missing assistant content")
    return str(content).strip()
