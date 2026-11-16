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

"""Tests de l'intégration Ollama au générateur de règle."""

from tools import llm_client
from tools.rule_generator import analyze, build_rule_source


def _suggestion(**overrides):
    base = {
        "domain": "congestion",
        "rule_name": "my qwen rule",
        "warn_threshold": 80,
        "critical_threshold": 95,
        "reason": "Congestion élevée détectée dans la demande.",
    }
    base.update(overrides)
    return base


def test_analyze_uses_llm_suggestion(monkeypatch):
    monkeypatch.setattr(
        llm_client, "chat_json", lambda *args, **kwargs: _suggestion()
    )

    info = analyze("Alerter si la congestion est élevée", use_llm=True)

    assert info["llm_used"] is True
    assert info["domain"] == "congestion"
    assert info["warn_threshold"] == 80.0
    assert info["critical_threshold"] == 95.0
    assert info["rule_name"] == "my_qwen_rule"


def test_invalid_llm_thresholds_fall_back_to_heuristic(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="jobs", warn_threshold=0.9, critical_threshold=0.5
        ),
    )

    info = analyze("Alerter si trop de jobs échouent", use_llm=True)

    assert info["domain"] == "jobs"
    assert info["warn_threshold"] == 0.1
    assert info["critical_threshold"] == 0.3


def test_llm_unavailable_falls_back_with_error(monkeypatch):
    def fail(*args, **kwargs):
        raise llm_client.LlmUnavailable("Ollama absent")

    monkeypatch.setattr(llm_client, "chat_json", fail)

    info = analyze("Alerter si le taux d'échec des jobs dépasse 10 %", use_llm=True)

    assert info["llm_used"] is False
    assert "Ollama absent" in info["llm_error"]
    assert info["domain"] == "jobs"


def test_explicit_domain_overrides_llm(monkeypatch):
    monkeypatch.setattr(
        llm_client, "chat_json", lambda *args, **kwargs: _suggestion(domain="kpi")
    )

    info = analyze("Alerter si le quota est dépassé", domain="resources", use_llm=True)

    assert info["domain"] == "resources"
    assert info["llm_used"] is False


def test_generated_source_uses_llm_thresholds(monkeypatch):
    monkeypatch.setattr(
        llm_client, "chat_json", lambda *args, **kwargs: _suggestion()
    )

    source = build_rule_source(
        "Alerter si la congestion est élevée", use_llm=True
    )

    assert "Domain: congestion." in source
    assert "default=80.0" in source
    assert "default=95.0" in source


def test_percent_llm_thresholds_are_normalized(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="congestion", warn_threshold=0.75, critical_threshold=0.8
        ),
    )

    info = analyze("Alerter si la congestion est trop élevée", use_llm=True)

    assert info["domain"] == "congestion"
    assert info["warn_threshold"] == 75.0
    assert info["critical_threshold"] == 80.0


def test_ratio_llm_thresholds_are_normalized(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="jobs", warn_threshold=20, critical_threshold=40
        ),
    )

    info = analyze("Alerter si trop de jobs échouent", use_llm=True)

    assert info["domain"] == "jobs"
    assert info["warn_threshold"] == 0.2
    assert info["critical_threshold"] == 0.4


def test_explicit_threshold_wins_over_llm(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="jobs", warn_threshold=0.95, critical_threshold=1
        ),
    )

    info = analyze(
        "Alerter si le taux d'échec des jobs dépasse 10 %", use_llm=True
    )

    assert info["domain"] == "jobs"
    assert info["warn_threshold"] == 0.1
    assert info["critical_threshold"] == 0.3


def test_keyword_domain_overrides_wrong_llm(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="load", warn_threshold=0.85, critical_threshold=0.9
        ),
    )

    info = analyze("Alerter si la file d'attente est trop longue", use_llm=True)

    assert info["domain"] == "congestion"
    assert info["llm_used"] is False
    assert info["warn_threshold"] == 70.0
    assert info["critical_threshold"] == 90.0


def test_llm_domain_used_when_no_keyword_matches(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="concurrent_users", warn_threshold=85, critical_threshold=95
        ),
    )

    info = analyze(
        "Alerter si quelque chose d'inhabituel se produit", use_llm=True
    )

    assert info["domain"] == "concurrent_users"
    assert info["llm_used"] is True


def test_implausible_llm_thresholds_fall_back_to_domain_defaults(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="jobs", warn_threshold=0.85, critical_threshold=0.9
        ),
    )

    info = analyze("Alerter si trop de jobs échouent", use_llm=True)

    assert info["domain"] == "jobs"
    assert info["warn_threshold"] == 0.1
    assert info["critical_threshold"] == 0.3


def test_plausible_llm_thresholds_are_kept(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "chat_json",
        lambda *args, **kwargs: _suggestion(
            domain="load", warn_threshold=0.85, critical_threshold=0.9
        ),
    )

    info = analyze("Alerter si la charge est trop élevée", use_llm=True)

    assert info["domain"] == "load"
    assert info["warn_threshold"] == 0.85
    assert info["critical_threshold"] == 0.9
