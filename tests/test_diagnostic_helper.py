"""Tests pour diagnostic_helper.py — vérifie le retour d'une checklist non vide."""

import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "diagnostic_helper.py"

VALID_FAMILIES = [
    "configuration",
    "rule-not-firing",
    "false-positives",
    "custom-enhancer",
    "missing-data",
    "notification",
    "training",
]

VALID_COMPONENTS = ["HealthCheck", "DataEnhancer", "Webhook Bridge", "Formation"]


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
