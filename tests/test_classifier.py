"""Tests pour ticket_classifier.py — vérifie le retour d'une famille valide."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "ticket_classifier.py"

VALID_FAMILIES = [
    "configuration",
    "rule-not-firing",
    "false-positives",
    "custom-enhancer",
    "missing-data",
    "notification",
    "training",
]


def _run_classifier(text: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(TOOL)],
        input=text,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Classifier failed: {proc.stderr}"
    return json.loads(proc.stdout)


def test_classifier_returns_valid_family():
    result = _run_classifier("Je veux configurer un quota de core-hours pour mon compte")
    assert result["family"] in VALID_FAMILIES
    assert result["component"] in ["HealthCheck", "DataEnhancer", "Webhook Bridge", "Formation"]
    assert 0 <= result["confidence"] <= 100
    assert isinstance(result["reasoning"], str)


def test_classifier_rule_not_firing():
    result = _run_classifier("Ma règle ne se déclenche pas, pas d'alerte levée")
    assert result["family"] == "rule-not-firing"


def test_classifier_false_positives():
    result = _run_classifier("Trop d'alertes, devenues du bruit")
    assert result["family"] == "false-positives"


def test_classifier_custom_enhancer():
    result = _run_classifier("Je veux un enhancer de coût personnalisé avec réduction étudiante")
    assert result["family"] == "custom-enhancer"


def test_classifier_missing_data():
    result = _run_classifier("Mon dashboard CO2 est vide, colonne manquante")
    assert result["family"] == "missing-data"


def test_classifier_notification():
    result = _run_classifier("Les alertes Slack n'arrivent pas, token bearer 401")
    assert result["family"] == "notification"


def test_classifier_training():
    result = _run_classifier("Je veux former 150 utilisateurs à OKA")
    assert result["family"] == "training"
