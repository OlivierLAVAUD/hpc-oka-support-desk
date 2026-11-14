#!/usr/bin/env python3
"""Automation identifier — propose des automatisations classées par ROI."""

import sys
from pathlib import Path


def _hitl_warning() -> None:
    print(
        "\n╔═══════════════════════════════════════════════════════════════╗\\n"
        "║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║\\n"
        "║  Chaque automatisation est proposée, pas imposée. L'ingénieur ║\\n"
        "║  décide de l'implémenter ou non après analyse du ROI.         ║\\n"
        "╚═══════════════════════════════════════════════════════════════╝\\n"
    )

AUTOMATIONS = [
    {
        "id": "AUTO-01",
        "title": "Assistant de calibration des seuils",
        "roi": "Élevé",
        "effort": "Moyen",
        "description": "Analyser l'historique des coûts pour proposer des seuils HIGH/CRITICAL adaptés par client.",
        "source_ticket": "TICKET-003",
    },
    {
        "id": "AUTO-02",
        "title": "Validateur d'ordre d'exécution des enhancers",
        "roi": "Élevé",
        "effort": "Élevé",
        "description": "Vérifier automatiquement que les colonnes requises (ex: ENERGY) sont présentes avant d'exécuter un enhancer dépendant.",
        "source_ticket": "TICKET-005",
    },
    {
        "id": "AUTO-03",
        "title": "Vérification de token Bearer",
        "roi": "Moyen",
        "effort": "Faible",
        "description": "Détecter automatiquement un mismatch de token Bearer entre OKA et les bridges webhook.",
        "source_ticket": "TICKET-006",
    },
    {
        "id": "AUTO-04",
        "title": "Alerte OK quand min_jobs non atteint",
        "roi": "Moyen",
        "effort": "Moyen",
        "description": "Remplacer le retour [] silencieux par une alerte OK explicite quand l'échantillon est insuffisant.",
        "source_ticket": "TICKET-002",
    },
    {
        "id": "AUTO-05",
        "title": "Générateur d'enhancer de coût",
        "roi": "Faible",
        "effort": "Moyen",
        "description": "Générer un Data Enhancer de coût paramétrable à partir des tarifs du client.",
        "source_ticket": "TICKET-004",
    },
]

def main() -> None:
    import sys
    _hitl_warning()
    print(f"{'ID':<10} {'ROI':<10} {'Effort':<10} {'Automatisation'}")
    print("-" * 80)
    for a in AUTOMATIONS:
        print(f"{a['id']:<10} {a['roi']:<10} {a['effort']:<10} {a['title']}")
        print(f"{'':<10} {a['roi']:<10} {a['effort']:<10}  {a['description']}")
        print(f"{'':<10} {a['roi']:<10} {a['effort']:<10}  Source : {a['source_ticket']}\\n")

if __name__ == "__main__":
    main()
