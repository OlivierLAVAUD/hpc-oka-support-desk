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
"""Tests de l'interface Gradio."""

import pytest

from app import DOMAINS, TICKET_NAMES, auth_config, build_app, profile_markdown, ticket_markdown
from tools.rule_generator import DOMAIN_SPECS


def test_app_builds_without_launching():
    demo = build_app()
    assert demo is not None


def test_domain_dropdown_covers_rule_generator():
    assert set(DOMAIN_SPECS) <= set(DOMAINS)


def test_ticket_markdown_contains_deliverables():
    assert TICKET_NAMES
    content = ticket_markdown("TICKET-001-quota-account")
    assert "request.md" in content
    assert "qualification.md" in content
    assert "diagnosis.md" in content
    assert "resolution/" in content
    assert "response.md" in content
    assert "lessons.md" in content


def test_ticket_markdown_handles_unknown_ticket():
    assert "introuvable" in ticket_markdown("TICKET-999-inconnu")


def test_profile_tab_exposes_ucit_coverage():
    content = profile_markdown()
    assert "TICKET-008" in content
    assert "visualisation" in content.lower()
    assert "CCME" in content


def test_ticket_markdown_fences_support_scripts():
    content = ticket_markdown("TICKET-008-visualization-portal")
    assert "```bash" in content
    assert "```powershell" in content
    assert "```nginx" in content


def test_auth_config_is_optional(monkeypatch):
    monkeypatch.delenv("GRADIO_AUTH", raising=False)
    assert auth_config() is None


def test_auth_config_reads_credentials(monkeypatch):
    monkeypatch.setenv("GRADIO_AUTH", "support:secret")
    assert auth_config() == ("support", "secret")


def test_auth_config_rejects_malformed_value(monkeypatch):
    monkeypatch.setenv("GRADIO_AUTH", "support")
    with pytest.raises(ValueError):
        auth_config()
