"""Groq API client wrapper for chat completions."""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

__all__ = ["GroqClient", "GroqClientError"]


class GroqClientError(RuntimeError):
    """Raised when the Groq API call fails or returns an unexpected payload."""


class GroqClient:
    """Thin wrapper around Groq's chat completions endpoint."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        default_temperature: float = 0.2,
        timeout_seconds: int = 45,
        max_retries: int = 2,
        retry_backoff_seconds: float = 2.0,
    ) -> None:
        load_dotenv()
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv(
            "GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"
        )
        self.default_temperature = default_temperature
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)

        if not self.api_key:
            raise GroqClientError(
                "Missing GROQ_API_KEY. Please set it in your environment or .env file."
            )

        if not self.model:
            raise GroqClientError(
                "Missing GROQ_MODEL. Please set it in your environment or .env file."
            )

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_format: Optional[Dict[str, Any]] = None,
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """Call Groq chat completions and return the assistant message text."""

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }

        env_timeout = os.getenv("GROQ_TIMEOUT_SECONDS")
        if env_timeout:
            try:
                timeout_seconds = int(env_timeout)
            except ValueError:
                logging.warning("Invalid GROQ_TIMEOUT_SECONDS value: %s", env_timeout)
        env_retries = os.getenv("GROQ_MAX_RETRIES")
        if env_retries:
            try:
                max_retries = int(env_retries)
            except ValueError:
                logging.warning("Invalid GROQ_MAX_RETRIES value: %s", env_retries)
        env_backoff = os.getenv("GROQ_RETRY_BACKOFF_SECONDS")
        if env_backoff:
            try:
                retry_backoff_seconds = float(env_backoff)
            except ValueError:
                logging.warning("Invalid GROQ_RETRY_BACKOFF_SECONDS value: %s", env_backoff)
        if max_output_tokens is not None:
            payload["max_output_tokens"] = max_output_tokens

        if response_format is not None:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        attempt = 0
        while True:
            try:
                response = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_seconds,
                )
            except requests.RequestException as exc:  # pragma: no cover - network failure
                logging.warning("Groq API request failure (attempt %s): %s", attempt + 1, exc)
                if attempt >= self.max_retries:
                    logging.exception("Groq API request failed after retries")
                    raise GroqClientError("Failed to reach Groq API") from exc
                time.sleep(self.retry_backoff_seconds * max(1, attempt + 1))
                attempt += 1
                continue

            if response.status_code == 200:
                break

            retriable_statuses = {408, 409, 425, 429, 500, 502, 503, 504}
            if attempt < self.max_retries and response.status_code in retriable_statuses:
                logging.warning(
                    "Groq API error %s (attempt %s): %s",
                    response.status_code,
                    attempt + 1,
                    response.text,
                )
                time.sleep(self.retry_backoff_seconds * max(1, attempt + 1))
                attempt += 1
                continue

            logging.error(
                "Groq API error %s: %s",
                response.status_code,
                response.text,
            )
            raise GroqClientError(
                f"Groq API error {response.status_code}: {response.text.strip()}"
            )

        data: Dict[str, Any] = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            logging.error("Unexpected Groq API response: %s", data)
            raise GroqClientError("Unexpected response structure from Groq API") from exc
