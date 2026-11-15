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

"""Tests pour diagnostic_helper.py — vérifie le retour d'une checklist non vide."""

import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "diagnostic_helper.py"

VALID_FAMILIES = [
    "configuration",
    "rule-not-firing",
    "false-positives",
    "custom-enhancer",
    "missing-data",
    "notification",
    "training",
    "remote-visualization",
    "ccme",
]

VALID_COMPONENTS = [
    "HealthCheck",
    "DataEnhancer",
    "Webhook Bridge",
    "Formation",
    "Portail & Visualisation",
    "CCME",
]


def _run_helper(family: str, component: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--family", family, "--component", component],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Helper failed: {proc.stderr}"
    return proc.stdout


def test_diagnostic_returns_non_empty_checklist():
    for family in VALID_FAMILIES:
        for component in VALID_COMPONENTS:
            output = _run_helper(family, component)
            assert "[ ]" in output, f"Checklist vide pour {family}/{component}"
            assert "# Checklist de diagnostic" in output


def test_diagnostic_invalid_family():
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--family", "inconnu", "--component", "HealthCheck"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0  # Ne plante pas, retourne une checklist par défaut
