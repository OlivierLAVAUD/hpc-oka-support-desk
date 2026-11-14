#!/usr/bin/env python3
"""Rule generator — génère une règle HealthCheck conforme au contrat OKA."""

import sys


def _hitl_warning() -> None:
    print(
        "\n╔═══════════════════════════════════════════════════════════════╗\n"
        "║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║\\n"
        "║  Le code généré est une proposition. Vérifier les 5 patterns ║\\n"
        "║  ci-dessous avant publication sur la plateforme OKA.          ║\\n"
        "╚═══════════════════════════════════════════════════════════════╝\\n",
        file=sys.stderr,
    )

PATTERNS_CHECKLIST = [
    "[ ] params_model Pydantic avec valeurs default pour tous les champs",
    "[ ] evaluate(self) -> list[Alert] (jamais None)",
    "[ ] _no_data_alert quand le provider échoue ou données vides",
    "[ ] CRITICAL vérifié avant HIGH dans _resolve_alert_level",
    "[ ] min_jobs guard si la règle scanne des jobs",
]

def generate(rule_name: str, description: str, domain: str, example_file: str) -> dict:
    import json
    rule_class = "".join(word.capitalize() for word in rule_name.split("_")) + "Rule"
    return {
        "rule_name": rule_name,
        "description": description,
        "domain": domain,
        "example_file": example_file,
        "rule_class": rule_class,
        "patterns_checklist": PATTERNS_CHECKLIST,
    }

def main() -> None:
    import sys
    _hitl_warning()
    print("Checklist des 5 patterns à vérifier avant publication :\\n")
    for item in PATTERNS_CHECKLIST:
        print(item)
    print("\\nExemple de règle générée :\\n")
    print(json.dumps(generate("my_custom_rule", "Ma règle personnalisée", "load", "core_load_rule.py"), indent=2))

if __name__ == "__main__":
    main()
