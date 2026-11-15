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

"""R&D feedback analyzer — identifie les irritants produit récurrents."""

import argparse
import re
from pathlib import Path

HITL_BANNER = """════════════════════════════════════════════════════════════════════════════════
AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT
Chaque évolution proposée est à valider par la R&D avant
toute remontée formelle.
════════════════════════════════════════════════════════════════════════════════"""

KNOWN_PATTERNS = [
    {
        "id": "IRR-01",
        "title": "Retour [] silencieux quand min_jobs non atteint",
        "impact": "Élevé",
        "proposition": "Émettre une alerte OK explicite 'insufficient sample' au lieu de [].",
    },
    {
        "id": "IRR-02",
        "title": "Pas de vérification d'ordre d'exécution des enhancers",
        "impact": "Élevé",
        "proposition": (
            "Vérifier automatiquement que les colonnes requises (ex: ENERGY) "
            "sont présentes avant exécution."
        ),
    },
    {
        "id": "IRR-03",
        "title": "Mismatch de token Bearer OKA vs bridge",
        "impact": "Moyen",
        "proposition": "Détecter automatiquement un mismatch de token.",
    },
    {
        "id": "IRR-04",
        "title": "Seuils par défaut non adaptés",
        "impact": "Moyen",
        "proposition": "Proposer un assistant de calibration basé sur l'historique.",
    },
]


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER)
    print()


def _extract_irritants(tickets_dir: Path) -> list[tuple[str, str]]:
    if not tickets_dir.is_dir():
        return []
    found = []
    for path in sorted(tickets_dir.glob("*/lessons.md")):
        text = path.read_text(encoding="utf-8")
        match = re.search(
            r"##\s+Irritant produit[^\n]*\n(.*?)(?=\n##\s|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            continue
        body = " ".join(match.group(1).split())
        if body and not body.lower().startswith("aucun"):
            found.append((path.parent.name, body))
    return found


def main() -> None:
    _hitl_warning()
    parser = argparse.ArgumentParser(description="Analyze lessons.md for R&D feedback")
    parser.add_argument("--tickets", default="tickets", help="Répertoire des tickets")
    args = parser.parse_args()

    found = _extract_irritants(Path(args.tickets))
    print(f"Irritants extraits des lessons.md : {len(found)}")
    for ticket, body in found:
        print(f"- {ticket} : {body}")
    print()
    print("Motifs produit connus (classés par impact) :")
    print()
    print(f"{'ID':<10} {'Impact':<10} Irritant produit")
    print("-" * 80)
    for item in KNOWN_PATTERNS:
        print(f"{item['id']:<10} {item['impact']:<10} {item['title']}")
        print(f"  Proposition : {item['proposition']}")
        print()


if __name__ == "__main__":
    main()
