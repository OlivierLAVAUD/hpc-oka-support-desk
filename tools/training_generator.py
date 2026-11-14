#!/usr/bin/env python3
"""Training generator — génère un parcours de formation en modules."""

import sys


def _hitl_warning() -> None:
    print(
        "\n╔══════════════════════════════════════════════════════════════╗\\n"
        "║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║\\n"
        "║  Ce parcours est un point de départ. L'ingénieur l'adapte     ║\\n"
        "║  au profil et aux besoins réels du client.                   ║\\n"
        "╚═══════════════════════════════════════════════════════════════╝\\n"
    )

MODULES = [
    {
        "nom": "Module 1 — Bases et dashboards",
        "duree": "4 heures",
        "objectifs": [
            "Comprendre l'architecture OKA",
            "Naviguer dans les dashboards de cluster",
            "Lire les métriques de charge (CPU, GPU, mémoire)",
            "Comprendre les états de jobs",
        ],
        "exercices": [
            "Identifier les 5 jobs les plus gourmands en CPU",
            "Détecter un cluster en surcharge",
        ],
        "source": "oka_healthchecks (load, kpi)",
    },
    {
        "nom": "Module 2 — Rapports et chargeback",
        "duree": "4 heures",
        "objectifs": [
            "Utiliser les Data Enhancers pour enrichir les jobs",
            "Calculer les coûts et l'empreinte carbone",
            "Générer des rapports de consommation",
        ],
        "exercices": [
            "Appliquer un enhancer de coût personnalisé",
            "Créer un rapport CO2 par département",
        ],
        "source": "oka_dataenhancers (costs, CO2, EAR)",
    },
    {
        "nom": "Module 3 — Alertes et HealthCheck",
        "duree": "4 heures",
        "objectifs": [
            "Comprendre les niveaux d'alerte (OK → CRITICAL)",
            "Configurer des règles de santé (HealthCheckRule)",
            "Configurer les notifications (bridges)",
            "Diagnostiquer une règle silencieuse",
        ],
        "exercices": [
            "Configurer une règle de quota de core-hours",
            "Tester une notification Slack avec token Bearer",
        ],
        "source": "oka_healthchecks, oka_webhooks",
    },
]

def main() -> None:
    import sys
    _hitl_warning()
    nb_users = sys.argv[1] if len(sys.argv) > 1 else "150"
    print(f"\\n=== Parcours de formation OKA — {nb_users} utilisateurs ===\\n")
    for m in MODULES:
        print(f"## {m['nom']} ({m['duree']})\\n")
        print(f"Source : {m['source']}")
        print("Objectifs :")
        for o in m["objectifs"]:
            print(f"  - {o}")
        print("Exercices :")
        for e in m["exercices"]:
            print(f"  - {e}")
        print("")

if __name__ == "__main__":
    main()
