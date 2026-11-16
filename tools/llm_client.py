#!/usr/bin/env python3
# Copyright 2026 UCit
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Client Ollama local, optionnel, pour les outils du POC."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_TIMEOUT = 60.0


class LlmError(RuntimeError):
    """Erreur générique du client LLM."""


class LlmUnavailable(LlmError):
    """Ollama n'est pas joignable."""


class LlmResponseError(LlmError):
    """La réponse d'Ollama est invalide."""


def enabled() -> bool:
    """Vrai si l'utilisateur a activé le mode LLM."""
    value = os.environ.get("OKA_LLM", "").strip().lower()
    return value in {"1", "true", "yes", "on", "ollama", "auto"}


def host() -> str:
    """URL d'Ollama, avec http:// ajouté si nécessaire."""
    value = os.environ.get("OLLAMA_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
    if not value.startswith(("http://", "https://")):
        value = f"http://{value}"
    return value.rstrip("/")


def model() -> str:
    """Modèle Ollama utilisé."""
    return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def timeout() -> float:
    """Timeout HTTP en secondes."""
    raw = os.environ.get("OKA_LLM_TIMEOUT", str(DEFAULT_TIMEOUT))
    try:
        return max(1.0, float(raw))
    except ValueError:
        return DEFAULT_TIMEOUT


def _request(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{host()}{path}"
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout()) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise LlmUnavailable(f"Ollama injoignable sur {url} : {exc}") from exc
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise LlmResponseError(f"Réponse Ollama non JSON : {body[:200]}") from exc
    if not isinstance(parsed, dict):
        raise LlmResponseError("Réponse Ollama inattendue.")
    return parsed


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return _request(path, payload)


def parse_json(content: str) -> dict[str, Any]:
    """Extraire un objet JSON d'une réponse, même entourée de fences Markdown."""
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LlmResponseError(f"Contenu LLM non JSON : {content[:200]}") from exc
    if not isinstance(parsed, dict):
        raise LlmResponseError("Le LLM doit retourner un objet JSON.")
    return parsed


def chat_json(
    system: str,
    user: str,
    *,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Appeler /api/chat et retourner un objet JSON validé par le parseur."""
    payload: dict[str, Any] = {
        "model": model(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "format": schema or "json",
        "options": {"temperature": 0, "seed": 0},
    }
    response = _post("/api/chat", payload)
    message = response.get("message")
    if not isinstance(message, dict):
        raise LlmResponseError("Réponse Ollama sans champ message.")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise LlmResponseError("Réponse Ollama vide.")
    return parse_json(content)


def list_models() -> list[str]:
    """Noms des modèles installés localement."""
    response = _request("/api/tags")
    models = response.get("models", [])
    names = []
    for item in models:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            names.append(item["name"])
    return names


def health() -> dict[str, Any]:
    """État du client et présence du modèle configuré."""
    status: dict[str, Any] = {
        "enabled": enabled(),
        "host": host(),
        "model": model(),
        "available": False,
        "model_installed": False,
        "models": [],
    }
    try:
        models = list_models()
    except LlmError as exc:
        status["error"] = str(exc)
        return status
    status["available"] = True
    status["models"] = models
    status["model_installed"] = any(
        name == model() or name.startswith(f"{model()}:") for name in models
    )
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description="Check local Ollama availability")
    parser.add_argument("--check", action="store_true", help="Afficher l'état d'Ollama")
    args = parser.parse_args()
    if not args.check:
        parser.print_help()
        return
    print(json.dumps(health(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
