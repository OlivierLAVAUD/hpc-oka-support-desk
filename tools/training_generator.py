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

"""Training generator — génère un parcours de formation adapté à un profil client."""

import argparse

HITL_BANNER = """╔══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Ce parcours est un point de départ. L'ingénieur l'adapte     ║
║  au profil et aux besoins réels du client.                   ║
╚══════════════════════════════════════════════════════════════╝"""

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
            "Configurer des règles de santé (HealthcheckRule)",
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


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER)
    print()


def build_modules(level: str, needs: str) -> list[dict]:
    modules = [dict(module) for module in MODULES]
    if "avanc" in level.lower():
        modules[0]["objectifs"] = [
            "Approfondir l'architecture OKA et les providers",
            "Optimiser la lecture des dashboards de cluster",
            "Analyser les métriques de charge et les goulots",
            "Interpréter les états de jobs et les causes d'échec",
        ]
    if needs.strip():
        modules[2]["objectifs"] = [
            *modules[2]["objectifs"],
            f"Appliquer les alertes aux besoins du client : {needs.strip()}",
        ]
    return modules


def main() -> None:
    _hitl_warning()
    parser = argparse.ArgumentParser(description="Generate an OKA training path")
    parser.add_argument("--users", type=int, default=150, help="Nombre d'utilisateurs")
    parser.add_argument(
        "--level",
        default="débutant à intermédiaire",
        help="Niveau du public (débutant, intermédiaire, avancé)",
    )
    parser.add_argument("--needs", default="", help="Besoins métiers spécifiques")
    args = parser.parse_args()

    print(f"=== Parcours de formation OKA — {args.users} utilisateurs ===")
    print(f"Niveau : {args.level}")
    if args.needs:
        print(f"Besoins : {args.needs}")
    print()

    for module in build_modules(args.level, args.needs):
        print(f"## {module['nom']} ({module['duree']})")
        print()
        print(f"Source : {module['source']}")
        print("Objectifs :")
        for objective in module["objectifs"]:
            print(f"  - {objective}")
        print("Exercices :")
        for exercise in module["exercices"]:
            print(f"  - {exercise}")
        print()


if __name__ == "__main__":
    main()
