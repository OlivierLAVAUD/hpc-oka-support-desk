#!/usr/bin/env python3
"""R&D feedback analyzer — identifie les irritants produit récurrents."""

import sys
from pathlib import Path


def _hitl_warning() -> None:
    lines = [
        "\n" + "═" * 80,
        "AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT",
        "Chaque évolution proposée est à valider par la R&D avant",
        "toute remontée formelle.",
        "═" * 80 + "\n",
    ]
    for line in lines:
        print(line)


AUTOMATIONS = [
    {
        "id": "IRR-01",
        "title": "Retour [] silencieux quand min_jobs non atteint",
        "impact": "Élevé",
        "tickets": ["TICKET-002"],
        "proposition": "Émettre une alerte OK explicite 'insufficient sample' au lieu de [].",
    },
    {
        "id": "IRR-02",
        "title": "Pas de vérification d'ordre d'exécution des enhancers",
        "impact": "Élevé",
        "tickets": ["TICKET-005"],
        "proposition": "Vérifier automatiquement que les colonnes requises (ex: ENERGY) sont présentes avant exécution.",
    },
    {
        "id": "IRR-03",
        "title": "Mismatch de token Bearer OKA vs bridge",
        "impact": "Moyen",
        "tickets": ["TICKET-006"],
        "proposition": "Détecter automatiquement un mismatch de token.",
    },
    {
        "id": "IRR-04",
        "title": "Seuils par défaut non adaptés",
        "impact": "Moyen",
        "tickets": ["TICKET-003"],
        "proposition": "Proposer un assistant de calibration basé sur l'historique.",
    },
]

def main() -> None:
    import sys
    _hitl_warning()
    tickets_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tickets")
    id_str = "{:<10}".format("ID")
    impact_fmt = "{:<10}".format("Impact")
    print(id_fmt + "  " + impact_fmt + "  Irritant produit")
    print("-" * 80)
    for a in AUTOMATIONS:
        id_str = "{:<10}".format(a["id"])
        impact_str = "{:<10}".format(a["impact"])
        tickets_str = ", ".join(a["tickets"])
        print(id_str + "  " + impact_str + "  " + a["title"])
        tickets_line = "  Tickets : " + tickets_str + "\n"
        proposition_line = "  Proposition : " + a["proposition"] + "\n"
        print(tickets_line)
        print(proposition_line)


if __name__ == "__main__":
    main()
