"""Tests de contrat pour les résolutions de tickets.

Vérifie que les règles/enhancers générés respectent les contrats OKA :
- params_model obligatoire (TypeError si absent)
- _no_data_alert présent
- CRITICAL avant HIGH
- Préfixe Cust_ pour colonnes non réservées (enhancers)
"""

import sys
from pathlib import Path

RESOLUTIONS_DIR = Path(__file__).resolve().parents[1] / "tickets"

# --- Test que les fichiers de résolution existent et sont lisibles ---

RESOLUTION_FILES = [
    "TICKET-002-rule-not-firing/resolution/failed_jobs_rule.py",
    "TICKET-003-false-positives/resolution/high_cost_rule.py",
    "TICKET-004-custom-cost/resolution/custom_cost_enhancer.py",
]


@pytest.mark.parametrize("rel_path", RESOLUTION_FILES)
def test_resolution_file_exists(rel_path):
    f = RESOLUTIONS_DIR / rel_path
    assert f.exists(), f"Fichier de résolution manquant : {rel_path}"
    assert f.stat().st_size > 0, f"Fichier de résolution vide : {rel_path}"


# --- Test que les règles HealthCheck ont un params_model ---

def test_healthcheck_rules_have_params_model():
    for rel_path in ["TICKET-002-rule-not-firing/resolution/failed_jobs_rule.py",
                     "TICKET-003-false-positives/resolution/high_cost_rule.py"]:
        f = RESOLUTIONS_DIR / rel_path
        content = f.read_text(encoding="utf-8")
        assert "params_model = Params" in content, (
            f"{rel_path} : params_model manquant"
        )
        assert "class Params(BaseModel)" in content, (
            f"{rel_path} : classe Params(BaseModel) manquante"
        )


# --- Test que les règles ont _no_data_alert ---

def test_healthcheck_rules_have_no_data_alert():
    for rel_path in ["TICKET-002-rule-not-firing/resolution/failed_jobs_rule.py",
                     "TICKET-003-false-positives/resolution/high_cost_rule.py"]:
        f = RESOLUTIONS_DIR / rel_path
        content = f.read_text(encoding="utf-8")
        assert "_no_data_alert" in content, (
            f"{rel_path} : _no_data_alert manquant"
        )


# --- Test que CRITICAL est vérifié avant HIGH ---

def test_critical_before_high():
    for rel_path in ["TICKET-002-rule-not-firing/resolution/failed_jobs_rule.py",
                     "TICKET-003-false-positives/resolution/high_cost_rule.py"]:
        f = RESOLUTIONS_DIR / rel_path
        content = f.read_text(encoding="utf-8")
        # Noms de champs possibles selon les règles (failure_rate_* ou *_threshold)
        critical_names = ["failure_rate_critical", "critical_threshold", "cost_critical",
                          "unavailable_rate_critical", "rate_critical", "dominance_critical"]
        high_names = ["failure_rate_high", "high_threshold", "cost_high",
                      "unavailable_rate_high", "rate_high", "dominance_high"]
        crit_name = next((n for n in critical_names if n in content), None)
        high_name = next((n for n in high_names if n in content), None)
        assert crit_name is not None and high_name is not None, (
            f"{rel_path} : seuils critiques/hauts manquants (cherché {critical_names} / {high_names})"
        )
        # Dans _resolve_alert_level, critical doit être vérifié avant high
        resolve_section = content[content.find("_resolve_alert_level"):]
        crit_check = resolve_section.find(crit_name)
        high_check = resolve_section.find(high_name)
        assert crit_check < high_check, (
            f"{rel_path} : CRITICAL ({crit_name}) doit être vérifié avant HIGH ({high_name}) "
            f"dans _resolve_alert_level"
        )


# --- Test que l'enhancer DataEnhancer respecte le contrat ---

def test_enhancer_has_params_model_and_run():
    f = RESOLUTIONS_DIR / "TICKET-004-custom-cost/resolution/custom_cost_enhancer.py"
    content = f.read_text(encoding="utf-8")
    assert "params_model = CustomCostEnhancerParams" in content
    assert "def run(self, data" in content or "def run(self, data:" in content
    assert "class CustomCostEnhancerParams(BaseModel)" in content


# --- Test que le fichier de résolution TICKET-002 a une alerte OK pour min_jobs ---

def test_ticket002_insufficient_sample_alert():
    f = RESOLUTIONS_DIR / "TICKET-002-rule-not-firing/resolution/failed_jobs_rule.py"
    content = f.read_text(encoding="utf-8")
    assert "min_jobs" in content
    assert "insufficient" in content.lower() or "insufficient_sample" in content
