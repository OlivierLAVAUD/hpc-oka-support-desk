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

"""Smoke tests for the support tools."""

import subprocess
import sys
from pathlib import Path

import pytest

from tools.rule_generator import DOMAIN_SPECS

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

STANDALONE_TOOLS = [
    "automation_identifier",
    "rnd_feedback_analyzer",
    "rule_generator",
    "ticket_prioritizer",
    "training_generator",
]


def _run(tool: str, *args: str, stdin_text: str | None = ""):
    return subprocess.run(
        [sys.executable, str(TOOLS / f"{tool}.py"), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
        check=False,
    )


@pytest.mark.parametrize("tool", STANDALONE_TOOLS)
def test_tool_runs_without_traceback(tool: str):
    proc = _run(tool)
    assert proc.returncode == 0, proc.stderr
    assert "Traceback" not in proc.stderr


def test_diagnostic_helper_outputs_markdown():
    proc = _run(
        "diagnostic_helper",
        "--family",
        "notification",
        "--component",
        "Webhook Bridge",
    )
    assert proc.returncode == 0, proc.stderr
    assert "# Checklist de diagnostic" in proc.stdout
    assert "## Vérifications générales" in proc.stdout
    assert chr(92) + "n" not in proc.stdout


def test_response_generator_extracts_cause(tmp_path: Path):
    diagnosis = tmp_path / "diagnosis.md"
    diagnosis.write_text(
        "# Diagnostic — TEST\n\n"
        "## Cause racine\n"
        "Le token Bearer ne correspond pas.\n\n"
        "## Preuves observées\n"
        "401 dans les logs.\n",
        encoding="utf-8",
    )

    proc = _run("response_generator", str(diagnosis))
    assert proc.returncode == 0, proc.stderr

    draft = (tmp_path / "response.md").read_text(encoding="utf-8")
    assert "Le token Bearer ne correspond pas." in draft
    assert "### Cause identifiée" in draft
    assert "À compléter à partir du diagnostic" not in draft.split("### Solution apportée")[0]
    assert "HITL" in proc.stderr


def test_classifier_shows_hitl():
    proc = _run("ticket_classifier", stdin_text="Je veux former 150 utilisateurs")
    assert proc.returncode == 0, proc.stderr
    assert "HITL" in proc.stderr


def test_diagnostic_helper_shows_hitl():
    proc = _run(
        "diagnostic_helper",
        "--family",
        "notification",
        "--component",
        "Webhook Bridge",
    )
    assert proc.returncode == 0, proc.stderr
    assert "HITL" in proc.stderr


def test_rule_generator_outputs_contract():
    proc = _run(
        "rule_generator",
        "Alerter si le taux d'échec des jobs dépasse 10 %",
    )
    assert proc.returncode == 0, proc.stderr
    assert "HITL" in proc.stderr

    marker = proc.stdout.find('"""Rule:')
    assert marker >= 0
    source = proc.stdout[marker:]
    compile(source, "<generated-rule>", "exec")
    assert "params_model = Params" in source
    assert "_no_data_alert" in source
    assert "AlertLevel.CRITICAL" in source
    assert "AlertLevel.HIGH" in source
    assert source.index("AlertLevel.CRITICAL") < source.index("AlertLevel.HIGH")


def test_rule_generator_keeps_dollar_and_sanitizes_name():
    proc = _run(
        "rule_generator",
        "Alerter si le coût dépasse 50 $ par job à 90 %",
        "--name",
        "my-custom-rule",
    )
    assert proc.returncode == 0, proc.stderr

    marker = proc.stdout.find('"""Rule:')
    assert marker >= 0
    source = proc.stdout[marker:]
    compile(source, "<generated-rule>", "exec")
    assert "class MyCustomRule(" in source
    assert "50 $ par job" in source


def test_rule_generator_single_threshold_stays_ordered():
    proc = _run("rule_generator", "Alerter si le taux d'échec des jobs dépasse 99 %")
    assert proc.returncode == 0, proc.stderr

    marker = proc.stdout.find('"""Rule:')
    source = proc.stdout[marker:]
    compile(source, "<generated-rule>", "exec")
    assert "default=0.89" in source
    assert "default=0.99" in source


@pytest.mark.parametrize(
    ("text", "provider_call"),
    [
        ("Alerter si le taux d'échec des jobs dépasse 10 %", "self.jobs.scan_jobs("),
        ("Alerter si le coût dépasse 25 000 €", "self.kpi.get_cost_metrics()"),
        ("Alerter si la charge CPU du cluster est trop élevée", "self.cluster_load.get_core_load()"),
        (
            "Alerter si le quota de core-hours du compte atteint 80 %",
            "self.cores.get_grouped_distribution(",
        ),
        (
            "Alerter si la congestion dépasse 80 %",
            "self.congestion.get_congestion_metrics(",
        ),
        (
            "Alerter sur le statut des jobs avec trop d'échecs",
            "self.state.get_jobs_status(",
        ),
        (
            "Alerter si le slowdown médian dépasse 3",
            "self.slowdown.get_slowdown_stats()",
        ),
        (
            "Alerter si la consommation d'un groupe domine à 60 %",
            "self.consumers.get_group_aggregation(",
        ),
        (
            "Alerter si les utilisateurs simultanés dépassent 100",
            "self.concurrent_users.get_running_and_waiting_users(",
        ),
    ],
)
def test_rule_generator_uses_real_provider(text: str, provider_call: str):
    proc = _run("rule_generator", text)
    assert proc.returncode == 0, proc.stderr

    marker = proc.stdout.find('"""Rule:')
    source = proc.stdout[marker:]
    compile(source, "<generated-rule>", "exec")
    assert provider_call in source
    for fake_method in ("get_failure_rate", "get_cluster_load", "get_waiting_time"):
        assert fake_method not in source


@pytest.mark.parametrize("domain", sorted(DOMAIN_SPECS))
def test_rule_generator_covers_every_documented_domain(domain: str):
    proc = _run("rule_generator", "Alerter sur ce domaine", "--domain", domain)
    assert proc.returncode == 0, proc.stderr

    marker = proc.stdout.find('"""Rule:')
    source = proc.stdout[marker:]
    compile(source, "<generated-rule>", "exec")
    assert f"Domain: {domain}." in source


def test_training_generator_uses_profile():
    proc = _run(
        "training_generator",
        "--users",
        "42",
        "--level",
        "avancé",
        "--needs",
        "GPU",
    )
    assert proc.returncode == 0, proc.stderr
    assert "42 utilisateurs" in proc.stdout
    assert "avancé" in proc.stdout
    assert "GPU" in proc.stdout


def test_prioritizer_has_expected_columns():
    proc = _run("ticket_prioritizer", "--tickets", "tickets")
    assert proc.returncode == 0, proc.stderr
    for column in ["Impact", "Ancienneté", "Similarité", "Famille"]:
        assert column in proc.stdout
    assert "TICKET-001" in proc.stdout
