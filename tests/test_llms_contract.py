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

"""Tests de cohérence avec les contrats publics llms.txt."""

import pytest

from tools import contract_context as contracts
from tools.rule_generator import DOMAIN_SPECS, build_rule_source

SOURCE_ROOT = contracts.source_root()
SOURCES_AVAILABLE = contracts.available()
requires_sources = pytest.mark.skipif(
    not SOURCES_AVAILABLE,
    reason="dépôts oka_* absents (définir OKA_SOURCE_ROOT)",
)

FIXTURE = """# Fixture

## Data providers

- `self.jobs` — job records
- `self.cluster_load` — load metrics

## Rules

- [jobs/a.py](jobs/a.py): exemple
"""


def test_parser_reads_sections_providers_and_rules(tmp_path):
    repo = tmp_path / "oka_healthchecks"
    repo.mkdir()
    (repo / "llms.txt").write_text(FIXTURE, encoding="utf-8")

    parsed = contracts.sections("healthchecks", tmp_path)
    assert "Data providers" in parsed
    assert contracts.provider_names("healthchecks", tmp_path) == frozenset(
        {"jobs", "cluster_load"}
    )
    assert contracts.documented_rules("healthchecks", tmp_path) == ("jobs/a.py",)


def test_report_flags_missing_rule_links(tmp_path):
    repo = tmp_path / "oka_healthchecks"
    repo.mkdir()
    (repo / "llms.txt").write_text(FIXTURE, encoding="utf-8")

    summary = contracts.report(tmp_path)
    assert summary["healthchecks"]["present"] is True
    assert summary["healthchecks"]["missing_rules"] == ("jobs/a.py",)
    assert summary["webhooks"]["present"] is False


@requires_sources
@pytest.mark.parametrize("domain", sorted(DOMAIN_SPECS))
def test_generator_provider_and_method_match_sources(domain):
    spec = DOMAIN_SPECS[domain]
    provider = spec["provider"].removeprefix("self.")

    assert provider in contracts.provider_names("healthchecks")
    source = SOURCE_ROOT / "oka_healthchecks" / spec["source"]
    assert source.is_file(), source
    assert spec["method"] in source.read_text(encoding="utf-8")


@requires_sources
def test_real_contract_report_has_no_new_broken_links():
    summary = contracts.report()
    known = {
        "load/high_core_utilization_rule.py",
        "scheduler_config/partition_scheduler_limits_rule.py",
    }
    assert set(summary["healthchecks"]["missing_rules"]) <= known
    assert summary["dataenhancers"]["missing_rules"] == ()
    assert summary["webhooks"]["missing_rules"] == ()


def test_generated_rule_uses_example_import_paths():
    source = build_rule_source("Alerter sur les jobs", domain="jobs")

    assert "from applications.healthcheck.core import Alert, HealthcheckRule" in source
    assert "from applications.ait.enums import ResultStatus" in source
    assert "applications.healthcheck.core.base" not in source
