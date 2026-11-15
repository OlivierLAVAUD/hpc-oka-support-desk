#!/usr/bin/env python3
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

"""Ticket classifier — heuristique déterministe (fallback si LLM indisponible)."""

import json
import sys
from pathlib import Path

HITL_BANNER = """╔═══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Cette classification est une proposition, pas une décision.  ║
║  L'ingénieur valide la famille, la sévérité et le composant.  ║
╚═══════════════════════════════════════════════════════════════╝"""

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

KEYWORDS = {
    "configuration": ["quota", "paramétrer", "configurer", "seuil", "compte"],
    "rule-not-firing": ["ne se déclenche pas", "pas d'alerte", "silencieuse", "aucune alerte"],
    "false-positives": ["trop d'alertes", "bruit", "faux positif", "seuil trop bas"],
    "custom-enhancer": ["enhancer", "tarif", "personnalisé", "réduction", "étudiant"],
    "missing-data": ["vide", "manquant", "colonne absente", "dashboard vide", "CO2 vide"],
    "notification": ["slack", "webhook", "token", "bearer", "401", "email", "jira"],
    "training": ["formation", "former", "utilisateurs", "parcours", "module"],
    "remote-visualization": [
        "visualisation",
        "3d",
        "vnc",
        "virtualgl",
        "opengl",
        "webgl",
        "gpu",
        "écran noir",
        "session graphique",
        "portail",
    ],
    "ccme": ["ccme", "ldap", "sso", "authentification", "licence", "connecteur"],
}

SEVERITY_KEYWORDS = {
    "critical": ["bloquant", "urgent", "critique", "production"],
    "high": ["élevée", "important", "pas d'alerte", "vide", "écran noir", "déconnect"],
    "medium": ["moyenne", "bruit", "trop d'alertes", "personnalisé"],
    "low": ["formation", "demande", "planifiée", "basse"],
}


def classify(text: str) -> dict:
    text_lower = text.lower()
    scores = {family: 0 for family in VALID_FAMILIES}
    for family, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[family] += 1

    best_family = max(scores, key=scores.get) if any(scores.values()) else "configuration"
    confidence = min(95, 50 + scores[best_family] * 15) if scores[best_family] > 0 else 40

    severity = "medium"
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            severity = level
            break

    component = "HealthCheck"
    if "ccme" in text_lower:
        component = "CCME"
    elif any(
        keyword in text_lower
        for keyword in ["visualisation", "3d", "vnc", "virtualgl", "opengl", "webgl", "gpu", "portail"]
    ):
        component = "Portail & Visualisation"
    elif any(keyword in text_lower for keyword in ["enhancer", "coût", "co2", "énergie"]):
        component = "DataEnhancer"
    elif any(keyword in text_lower for keyword in ["slack", "webhook", "notification", "token"]):
        component = "Webhook Bridge"
    elif "formation" in text_lower:
        component = "Formation"

    reasoning = (
        f"Famille '{best_family}' détectée par mots-clés (score={scores[best_family]}). "
        f"Sévérité '{severity}' déduite du contexte. Composant '{component}' identifié par domaine."
    )

    return {
        "family": best_family,
        "severity": severity,
        "component": component,
        "confidence": confidence,
        "reasoning": reasoning,
    }


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER, file=sys.stderr)
    print(file=sys.stderr)


def main() -> None:
    _hitl_warning()
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    result = classify(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
