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

"""Automation identifier — propose des automatisations classées par ROI."""

import argparse
from pathlib import Path

HITL_BANNER = """╔═══════════════════════════════════════════════════════════════╗
║  HITL WARNING — TO BE VALIDATED BY THE SUPPORT ENGINEER      ║
║  Chaque automatisation est proposée, pas imposée. L'ingénieur ║
║  décide de l'implémenter ou non après analyse du ROI.         ║
╚═══════════════════════════════════════════════════════════════╝"""

AUTOMATIONS = [
    {
        "id": "AUTO-01",
        "title": "Assistant de calibration des seuils",
        "roi": "Élevé",
        "effort": "Moyen",
        "description": (
            "Analyser l'historique des coûts pour proposer des seuils "
            "HIGH/CRITICAL adaptés par client."
        ),
        "source_ticket": "TICKET-003",
        "keywords": ["seuil", "calibration", "bruit", "coût"],
    },
    {
        "id": "AUTO-02",
        "title": "Validateur d'ordre d'exécution des enhancers",
        "roi": "Élevé",
        "effort": "Élevé",
        "description": (
            "Vérifier automatiquement que les colonnes requises (ex: ENERGY) "
            "sont présentes avant d'exécuter un enhancer dépendant."
        ),
        "source_ticket": "TICKET-005",
        "keywords": ["energy", "enhancer", "colonne", "ordre"],
    },
    {
        "id": "AUTO-03",
        "title": "Vérification de token Bearer",
        "roi": "Moyen",
        "effort": "Faible",
        "description": (
            "Détecter automatiquement un mismatch de token Bearer entre OKA "
            "et les bridges webhook."
        ),
        "source_ticket": "TICKET-006",
        "keywords": ["token", "bearer", "401", "bridge"],
    },
    {
        "id": "AUTO-04",
        "title": "Alerte OK quand min_jobs non atteint",
        "roi": "Moyen",
        "effort": "Moyen",
        "description": (
            "Remplacer le retour [] silencieux par une alerte OK explicite "
            "quand l'échantillon est insuffisant."
        ),
        "source_ticket": "TICKET-002",
        "keywords": ["min_jobs", "silencieux", "échantillon", "job"],
    },
    {
        "id": "AUTO-05",
        "title": "Générateur d'enhancer de coût",
        "roi": "Faible",
        "effort": "Moyen",
        "description": (
            "Générer un Data Enhancer de coût paramétrable à partir des tarifs du client."
        ),
        "source_ticket": "TICKET-004",
        "keywords": ["enhancer", "coût", "tarif", "étudiant"],
    },
]


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER)
    print()


def _history_text(tickets_dir: Path) -> tuple[str, int]:
    if not tickets_dir.is_dir():
        return "", 0
    lessons = sorted(tickets_dir.glob("*/lessons.md"))
    return "\n".join(path.read_text(encoding="utf-8") for path in lessons), len(lessons)


def main() -> None:
    _hitl_warning()
    parser = argparse.ArgumentParser(description="Identify automation opportunities")
    parser.add_argument("--tickets", default="tickets", help="Répertoire des tickets")
    args = parser.parse_args()

    history, lesson_count = _history_text(Path(args.tickets))
    print(f"Historique analysé : {lesson_count} fichier(s) lessons.md")
    print()
    print(f"{'ID':<10} {'ROI':<10} {'Effort':<10} {'Preuves':<10} {'Automatisation'}")
    print("-" * 90)
    for item in AUTOMATIONS:
        hits = sum(history.lower().count(keyword.lower()) for keyword in item["keywords"])
        print(
            f"{item['id']:<10} {item['roi']:<10} {item['effort']:<10} "
            f"{hits:<10} {item['title']}"
        )
        print(f"{'':<10} {'':<10} {'':<10} {'':<10} {item['description']}")
        print(f"{'':<10} {'':<10} {'':<10} {'':<10} Source : {item['source_ticket']}")
        print()


if __name__ == "__main__":
    main()
