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

"""Tests du client Ollama, sans réseau."""

import pytest

from tools import llm_client


def test_parse_json_accepts_plain_object():
    assert llm_client.parse_json('{"domain": "jobs"}') == {"domain": "jobs"}


def test_parse_json_accepts_fenced_output():
    content = '```json\n{"domain": "jobs", "warn_threshold": 0.1}\n```'
    assert llm_client.parse_json(content)["domain"] == "jobs"


def test_parse_json_extracts_object_around_text():
    content = 'Voici la réponse : {"domain": "kpi"} — fin.'
    assert llm_client.parse_json(content) == {"domain": "kpi"}


def test_parse_json_rejects_invalid_content():
    with pytest.raises(llm_client.LlmResponseError):
        llm_client.parse_json("pas de json")


def test_chat_json_builds_ollama_payload(monkeypatch):
    captured = {}

    def fake_post(path, payload):
        captured["path"] = path
        captured["payload"] = payload
        return {"message": {"content": '{"domain": "jobs"}'}}

    monkeypatch.setattr(llm_client, "_post", fake_post)
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    result = llm_client.chat_json("system", "user", schema={"type": "object"})

    assert result == {"domain": "jobs"}
    assert captured["path"] == "/api/chat"
    payload = captured["payload"]
    assert payload["model"] == "qwen2.5-coder:7b"
    assert payload["stream"] is False
    assert payload["format"] == {"type": "object"}
    assert payload["options"]["temperature"] == 0
    assert payload["messages"][0]["role"] == "system"


def test_health_reports_unavailable(monkeypatch):
    def fail_request(path, payload=None):
        raise llm_client.LlmUnavailable("connexion refusée")

    monkeypatch.setattr(llm_client, "_request", fail_request)

    status = llm_client.health()
    assert status["available"] is False
    assert "connexion refusée" in status["error"]


def test_enabled_reads_environment(monkeypatch):
    monkeypatch.setenv("OKA_LLM", "ollama")
    assert llm_client.enabled() is True
    monkeypatch.setenv("OKA_LLM", "off")
    assert llm_client.enabled() is False


@pytest.fixture
def ollama_server(monkeypatch):
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            payload = {"models": [{"name": "qwen2.5-coder:7b"}]}
            self._reply(payload)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
            content = json.dumps({"model": request["model"], "ok": True})
            self._reply({"message": {"content": content}})

        def _reply(self, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("OLLAMA_HOST", f"http://127.0.0.1:{server.server_port}")
    yield server
    server.shutdown()
    thread.join(timeout=2)


def test_chat_json_over_http(ollama_server):
    result = llm_client.chat_json("system", "user")
    assert result == {"model": "qwen2.5-coder:7b", "ok": True}


def test_health_over_http(ollama_server):
    status = llm_client.health()
    assert status["available"] is True
    assert status["model_installed"] is True
