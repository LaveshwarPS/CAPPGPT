"""Unified LLM helper with Ollama + Gemini support.

This module keeps the legacy `query_ollama(...)` API so existing code does not
change, but routes requests based on `LLM_PROVIDER`.

Supported providers:
1. `gemini` (recommended default): Google Gemini API over HTTPS
2. `ollama`: local/cloud Ollama over HTTP with CLI fallback

Environment variables (provider selection):
- LLM_PROVIDER: `ollama` or `gemini` (default: `gemini`)
- LLM_MODEL: Generic model override for either provider

Ollama environment variables:
- OLLAMA_MODEL (default: from cloud config or `phi`)
- OLLAMA_ENDPOINT (default: http://localhost:11434/api/generate)
- OLLAMA_TIMEOUT (default: from cloud config or 180)
- OLLAMA_MAX_RETRIES (default: from cloud config or 3)
- OLLAMA_USE_CLOUD (`true`/`false`)

Gemini environment variables:
- GEMINI_API_KEY: Required when LLM_PROVIDER=gemini
- GEMINI_MODEL (default: gemini-2.5-flash)
- GEMINI_API_BASE (default: https://generativelanguage.googleapis.com/v1beta)
- GEMINI_MAX_RETRIES (default: 3)
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Optional

# Try to load cloud config first
try:
    from ollama_cloud_config import OLLAMA_CLOUD_CONFIG
    _CLOUD_CONFIG = OLLAMA_CLOUD_CONFIG
except ImportError:
    _CLOUD_CONFIG = {"endpoint": "", "use_cloud": False, "model": "phi"}

# Ollama config
_USE_CLOUD = _CLOUD_CONFIG.get("use_cloud", False) or os.getenv(
    "OLLAMA_USE_CLOUD", ""
).lower() == "true"

if _USE_CLOUD and _CLOUD_CONFIG.get("endpoint"):
    _CLOUD_ENDPOINT = _CLOUD_CONFIG["endpoint"]
    if not _CLOUD_ENDPOINT.endswith("/api/generate"):
        _CLOUD_ENDPOINT = _CLOUD_ENDPOINT.rstrip("/") + "/api/generate"
    _HTTP_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", _CLOUD_ENDPOINT)
else:
    _HTTP_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")

_DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", _CLOUD_CONFIG.get("model", "phi"))
_DEFAULT_OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", _CLOUD_CONFIG.get("timeout", "180")))
_OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", _CLOUD_CONFIG.get("max_retries", "3")))

# Gemini config
_GEMINI_API_BASE = os.getenv(
    "GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta"
).rstrip("/")
_DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))

# Provider config
_RAW_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()
if _RAW_PROVIDER in {"gemini", "ollama"}:
    _LLM_PROVIDER = _RAW_PROVIDER
else:
    # Prefer Gemini when provider is not explicitly configured.
    _LLM_PROVIDER = "gemini"

# Generic defaults (LLM_MODEL overrides provider-specific model)
_DEFAULT_MODEL = os.getenv(
    "LLM_MODEL",
    _DEFAULT_GEMINI_MODEL if _LLM_PROVIDER == "gemini" else _DEFAULT_OLLAMA_MODEL,
)
_DEFAULT_TIMEOUT = _DEFAULT_OLLAMA_TIMEOUT


class OllamaError(RuntimeError):
    """Base exception for LLM-related errors (legacy name preserved)."""


class OllamaConnectionError(OllamaError):
    """Service is not reachable."""


class OllamaTimeoutError(OllamaError):
    """Request timed out."""


class OllamaModelError(OllamaError):
    """Model not found or model-related issue."""


def set_model(model: str) -> None:
    """Set default model for this process."""
    global _DEFAULT_MODEL
    _DEFAULT_MODEL = model


def set_provider(provider: str) -> None:
    """Set active provider for this process (`ollama` or `gemini`)."""
    global _LLM_PROVIDER
    value = provider.strip().lower()
    if value not in {"ollama", "gemini"}:
        raise OllamaError(f"Unsupported LLM provider '{provider}'. Use 'ollama' or 'gemini'.")
    _LLM_PROVIDER = value


def get_provider() -> str:
    """Return active provider name."""
    return _LLM_PROVIDER


def _normalize_timeout(timeout: int | tuple) -> tuple:
    if isinstance(timeout, int):
        return (max(timeout * 0.2, 1), timeout)
    return timeout


def _gemini_model_url(model: str, api_key: str) -> str:
    return f"{_GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"


def _gemini_models_url(api_key: str) -> str:
    return f"{_GEMINI_API_BASE}/models?key={api_key}"


def _resolve_gemini_model(model: str | None) -> str:
    """Return a valid Gemini model name.

    The app UI still exposes Ollama model names (e.g. `phi`, `llama2`,
    `neural-chat`). If one of those is passed while using Gemini provider,
    fall back to GEMINI_MODEL/default instead of failing.
    """
    if not model:
        return _DEFAULT_GEMINI_MODEL
    value = model.strip()
    if value.startswith("gemini-"):
        return value
    return _DEFAULT_GEMINI_MODEL


def ollama_health_check(endpoint: Optional[str] = None, timeout: int = 5) -> bool:
    """Health check for current provider.

    This keeps the legacy function name for compatibility.
    """
    if _LLM_PROVIDER == "gemini":
        return _gemini_health_check(timeout=timeout)
    return _ollama_health_check(endpoint=endpoint, timeout=timeout)


def _ollama_health_check(endpoint: Optional[str] = None, timeout: int = 5) -> bool:
    if endpoint is None:
        endpoint = _HTTP_ENDPOINT.rsplit("/api/", 1)[0] if "/api/" in _HTTP_ENDPOINT else _HTTP_ENDPOINT
    health_url = f"{endpoint}/api/version"
    try:
        import requests

        resp = requests.get(health_url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def _gemini_health_check(timeout: int = 5) -> bool:
    if not _GEMINI_API_KEY:
        return False
    try:
        import requests

        resp = requests.get(_gemini_models_url(_GEMINI_API_KEY), timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def get_available_models(endpoint: Optional[str] = None, timeout: int = 5) -> list:
    """List available models for current provider."""
    if _LLM_PROVIDER == "gemini":
        return _get_gemini_models(timeout=timeout)
    return _get_ollama_models(endpoint=endpoint, timeout=timeout)


def _get_ollama_models(endpoint: Optional[str] = None, timeout: int = 5) -> list:
    if endpoint is None:
        endpoint = _HTTP_ENDPOINT.rsplit("/api/", 1)[0] if "/api/" in _HTTP_ENDPOINT else _HTTP_ENDPOINT
    models_url = f"{endpoint}/api/tags"
    try:
        import requests

        resp = requests.get(models_url, timeout=timeout)
        data = resp.json()
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


def _get_gemini_models(timeout: int = 5) -> list:
    if not _GEMINI_API_KEY:
        return []
    try:
        import requests

        resp = requests.get(_gemini_models_url(_GEMINI_API_KEY), timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        names = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
        return [n for n in names if n]
    except Exception:
        return []


def query_ollama_http(
    prompt: str,
    model: str | None = None,
    timeout: int | tuple = 60,
    stream: bool = False,
    max_retries: int = 3,
    endpoint: str | None = None,
) -> str:
    """Query Ollama via HTTP API with retry and optional streaming."""
    if model is None:
        model = _DEFAULT_MODEL
    if endpoint is None:
        endpoint = _HTTP_ENDPOINT

    try:
        import requests
    except ImportError as exc:
        raise OllamaError("Install requests: pip install requests") from exc

    payload = {"model": model, "prompt": prompt, "stream": stream}
    timeout = _normalize_timeout(timeout)
    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            resp = requests.post(endpoint, json=payload, timeout=timeout)
            if resp.status_code == 404:
                raise OllamaModelError(
                    f"Model '{model}' not found on Ollama. "
                    f"Available models: {get_available_models()}. Pull with: ollama pull {model}"
                )
            if resp.status_code >= 500:
                raise OllamaError(f"Ollama server error ({resp.status_code}): {resp.text}")
            resp.raise_for_status()
            if stream:
                return _aggregate_streaming_response(resp)
            return resp.json().get("response", "")
        except requests.exceptions.ConnectionError:
            last_error = OllamaConnectionError(
                f"Could not connect to Ollama at {endpoint}. "
                "Ensure Ollama is running and endpoint is correct."
            )
        except requests.exceptions.Timeout:
            last_error = OllamaTimeoutError(
                f"Ollama request timed out. Try increasing OLLAMA_TIMEOUT (current {_DEFAULT_OLLAMA_TIMEOUT}s)."
            )
        except (KeyError, json.JSONDecodeError) as exc:
            raise OllamaError(f"Unexpected Ollama response format: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            last_error = OllamaError(f"Ollama HTTP error: {exc}")

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    if last_error:
        raise last_error
    raise OllamaError("Ollama HTTP query failed.")


def _aggregate_streaming_response(resp) -> str:
    full_response = []
    try:
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line)
                text = data.get("response")
                if text:
                    full_response.append(text)
            except json.JSONDecodeError:
                continue
        return "".join(full_response)
    except Exception as exc:
        raise OllamaError(f"Error aggregating stream response: {exc}") from exc


def query_ollama_cli(prompt: str, model: str | None = None, timeout: int = 60) -> str:
    """Query Ollama via CLI fallback."""
    if model is None:
        model = _DEFAULT_MODEL
    cmd = ["ollama", "run", model]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise OllamaConnectionError(
            "The `ollama` CLI was not found on PATH. Install Ollama and restart terminal."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise OllamaTimeoutError(f"Ollama CLI timed out after {timeout} seconds.") from exc

    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace")
        if "not found" in stderr.lower():
            raise OllamaModelError(f"Model '{model}' not found. Pull with: ollama pull {model}")
        raise OllamaError(f"Ollama CLI failed (exit {proc.returncode}): {stderr}")

    return proc.stdout.decode("utf-8", errors="replace")


def query_gemini_http(
    prompt: str,
    model: str | None = None,
    timeout: int | tuple = 60,
    max_retries: int | None = None,
    api_key: str | None = None,
) -> str:
    """Query Gemini generateContent endpoint."""
    model = _resolve_gemini_model(model if model is not None else _DEFAULT_MODEL)
    if api_key is None:
        api_key = _GEMINI_API_KEY
    if not api_key:
        raise OllamaConnectionError(
            "GEMINI_API_KEY is missing. Set GEMINI_API_KEY when LLM_PROVIDER=gemini."
        )
    if max_retries is None:
        max_retries = _GEMINI_MAX_RETRIES

    try:
        import requests
    except ImportError as exc:
        raise OllamaError("Install requests: pip install requests") from exc

    url = _gemini_model_url(model, api_key)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    timeout = _normalize_timeout(timeout)
    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 404:
                raise OllamaModelError(f"Gemini model '{model}' not found or not enabled.")
            if resp.status_code in {401, 403}:
                raise OllamaConnectionError(
                    "Gemini authentication failed. Check GEMINI_API_KEY and API permissions."
                )
            if resp.status_code == 429:
                raise OllamaTimeoutError("Gemini rate limit reached (429). Retry later.")
            if resp.status_code >= 500:
                raise OllamaError(f"Gemini server error ({resp.status_code}): {resp.text}")

            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                prompt_feedback = data.get("promptFeedback", {})
                raise OllamaError(f"Gemini returned no candidates. Feedback: {prompt_feedback}")

            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
            return text.strip()
        except requests.exceptions.ConnectionError:
            last_error = OllamaConnectionError("Could not connect to Gemini API endpoint.")
        except requests.exceptions.Timeout:
            last_error = OllamaTimeoutError("Gemini request timed out.")
        except requests.exceptions.RequestException as exc:
            last_error = OllamaError(f"Gemini HTTP error: {exc}")

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    if last_error:
        raise last_error
    raise OllamaError("Gemini query failed.")


def query_ollama(
    prompt: str,
    model: str | None = None,
    timeout: int | tuple | None = None,
    prefer_http: bool = True,
    stream: bool = False,
) -> str:
    """Unified query entry point (legacy name preserved).

    Provider routing:
    - `LLM_PROVIDER=ollama`: Ollama HTTP/CLI fallback behavior
    - `LLM_PROVIDER=gemini`: Gemini HTTP request
    """
    if model is None:
        model = _DEFAULT_MODEL
    if timeout is None:
        timeout = _DEFAULT_TIMEOUT

    if _LLM_PROVIDER == "gemini":
        if stream:
            raise OllamaError("stream=True is not supported in Gemini mode.")
        return query_gemini_http(prompt=prompt, model=model, timeout=timeout)

    if _LLM_PROVIDER != "ollama":
        raise OllamaError(
            f"Unsupported LLM_PROVIDER '{_LLM_PROVIDER}'. Use 'ollama' or 'gemini'."
        )

    methods = [query_ollama_http, query_ollama_cli] if prefer_http else [query_ollama_cli, query_ollama_http]
    last_error: Optional[Exception] = None

    for method in methods:
        try:
            if method == query_ollama_http:
                return query_ollama_http(
                    prompt=prompt,
                    model=model,
                    timeout=timeout,
                    stream=stream,
                    max_retries=_OLLAMA_MAX_RETRIES,
                )
            return query_ollama_cli(prompt=prompt, model=model, timeout=int(timeout) if isinstance(timeout, int) else int(timeout[-1]))
        except OllamaError as exc:
            last_error = exc

    if last_error:
        raise last_error
    raise OllamaError("LLM query failed (unknown error).")


if __name__ == "__main__":
    print("LLM Integration Test")
    print("=" * 60)
    print(f"Provider: {_LLM_PROVIDER}")
    print(f"Model: {_DEFAULT_MODEL}")
    if _LLM_PROVIDER == "ollama":
        print(f"Ollama endpoint: {_HTTP_ENDPOINT}")
        print(f"Timeout: {_DEFAULT_OLLAMA_TIMEOUT}s")
        print(f"Max retries: {_OLLAMA_MAX_RETRIES}")
    else:
        print(f"Gemini API base: {_GEMINI_API_BASE}")
        print(f"Timeout: {_DEFAULT_TIMEOUT}s")
        print(f"Max retries: {_GEMINI_MAX_RETRIES}")
    print()

    print("Health check...")
    if ollama_health_check():
        print("  OK")
    else:
        print("  FAILED")

    example_prompt = "Say hello and tell me your name in one sentence."
    print()
    print(f"Prompt: {example_prompt}")
    try:
        response = query_ollama(example_prompt, timeout=60)
        print("Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)
    except OllamaError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
