#!/usr/bin/env python3
"""Ticket classifier — heuristique déterministe (fallback si LLM indisponible)."""

import json
import sys
from pathlib import Path

VALID_FAMILIES = [
    "configuration",
    "rule-not-firing",
    "false-positives",
    "custom-enhancer",
    "missing-data",
    "notification",
    "training",
]

KEYWORDS = {
    "configuration": ["quota", "paramétrer", "configurer", "seuil", "compte"],
    "rule-not-firing": ["ne se déclenche pas", "pas d'alerte", "silencieuse", "aucune alerte"],
    "false-positives": ["trop d'alertes", "bruit", "faux positif", "seuil trop bas"],
    "custom-enhancer": ["enhancer", "tarif", "personnalisé", "réduction", "étudiant"],
    "missing-data": ["vide", "manquant", "colonne absente", "dashboard vide", "CO2 vide"],
    "notification": ["slack", "webhook", "token", "bearer", "401", "email", "jira"],
    "training": ["formation", "former", "utilisateurs", "parcours", "module"],
}

SEVERITY_KEYWORDS = {
    "critical": ["bloquant", "urgent", "critique", "production"],
    "high": ["élevée", "important", "pas d'alerte", "vide"],
    "medium": ["moyenne", "bruit", "trop d'alertes", "personnalisé"],
    "low": ["formation", "demande", "planifiée", "basse"],
}

def classify(text: str) -> dict:
    text_lower = text.lower()
    scores = {fam: 0 for fam in VALID_FAMILIES}
    for fam, kws in KEYWORDS.items():
        for kw in kws:
            if kw in text_lower:
                scores[fam] += 1
    best_family = max(scores, key=scores.get) if any(scores.values()) else "configuration"
    confidence = min(95, 50 + scores[best_family] * 15) if scores[best_family] > 0 else 40

    sev = "medium"
    for level, kws in SEVERITY_KEYWORDS.items():
        if any(kw in text_lower for kw in kws):
            sev = level
            break

    comp = "HealthCheck"
    if any(kw in text_lower for kw in ["enhancer", "coût", "co2", "énergie"]):
        comp = "DataEnhancer"
    elif any(kw in text_lower for kw in ["slack", "webhook", "notification", "token"]):
        comp = "Webhook Bridge"
    elif any(kw in text_lower for kw in ["formation"]):
        comp = "Formation"

    reasoning = (
        f"Famille '{best_family}' détectée par mots-clés (score={scores[best_family]}). "
        f"Sévérité '{sev}' déduite du contexte. Composant '{comp}' identifié par domaine."
    )

    return {
        "family": best_family,
        "severity": sev,
        "component": comp,
        "confidence": confidence,
        "reasoning": reasoning,
    }

def main() -> None:
    import sys
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    result = classify(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
