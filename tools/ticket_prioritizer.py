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

"""Ticket prioritizer — classe les tickets par sévérité, impact, ancienneté et similarité."""

import argparse
import re
from datetime import date
from pathlib import Path

HITL_BANNER = """╔═══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Cet ordre de priorité est un conseil, pas une décision.      ║
║  L'ingénieur valide l'ordre final de traitement.              ║
╚═══════════════════════════════════════════════════════════════╝"""

SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}
IMPACT_WEIGHT = {"critique": 4, "élevée": 3, "haute": 3, "moyenne": 2, "basse": 1, "faible": 1}
IMPACT_LABEL = {"critique": "Critique", "élevée": "Élevé", "haute": "Élevé",
                "moyenne": "Moyen", "basse": "Faible", "faible": "Faible"}


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER)
    print()


def _search(text: str, pattern: str, default: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else default


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zà-ÿ]{4,}", text.lower())}


def _read_ticket(ticket_dir: Path) -> dict:
    request_file = ticket_dir / "request.md"
    qualification_file = ticket_dir / "qualification.md"
    request_text = request_file.read_text(encoding="utf-8") if request_file.exists() else ""
    qualification_text = (
        qualification_file.read_text(encoding="utf-8") if qualification_file.exists() else ""
    )

    severity = _search(qualification_text, r"\*\*Niveau\*\*\s*:\s*(\w+)", "low").lower()
    family = _search(qualification_text, r"\*\*Famille\*\*\s*:\s*([\w-]+)", "unknown").lower()
    priority = _search(request_text, r"\*\*Priorité\*\*\s*:\s*(.+)", "Moyenne").lower()
    opened = _search(request_text, r"## Date d'ouverture\s*\n\s*(\d{4}-\d{2}-\d{2})", "")

    try:
        age_days = max(0, (date.today() - date.fromisoformat(opened)).days)
    except ValueError:
        age_days = 0

    return {
        "severity": severity,
        "family": family,
        "priority": priority,
        "impact": IMPACT_WEIGHT.get(priority, 2),
        "impact_label": IMPACT_LABEL.get(priority, "Moyen"),
        "age_days": age_days,
        "tokens": _tokens(request_text),
    }


def _similarity(current: set[str], others: list[set[str]]) -> float:
    best = 0.0
    for other in others:
        union = current | other
        if union:
            best = max(best, len(current & other) / len(union))
    return best


def main() -> None:
    _hitl_warning()
    parser = argparse.ArgumentParser(description="Prioritize OKA support tickets")
    parser.add_argument("--tickets", default="tickets", help="Répertoire des tickets")
    args = parser.parse_args()

    tickets_dir = Path(args.tickets)
    if not tickets_dir.is_dir():
        print(f"❌ Dossier de tickets introuvable : {tickets_dir}")
        return

    tickets = []
    for ticket_dir in sorted(tickets_dir.iterdir()):
        if ticket_dir.is_dir() and (ticket_dir / "request.md").exists():
            tickets.append((ticket_dir.name, _read_ticket(ticket_dir)))

    all_tokens = [info["tokens"] for _, info in tickets]
    rows = []
    for name, info in tickets:
        names = [ticket_name for ticket_name, _ in tickets]
        others = [
            tokens
            for other_name, tokens in zip(names, all_tokens, strict=True)
            if other_name != name
        ]
        similarity = _similarity(info["tokens"], others)
        rows.append((info, name, similarity))

    rows.sort(
        key=lambda row: (
            SEVERITY_WEIGHT.get(row[0]["severity"], 1),
            row[0]["impact"],
            row[0]["age_days"],
            row[2],
        ),
        reverse=True,
    )

    print(
        f"{'Priorité':<10} {'Ticket':<35} {'Sévérité':<10} {'Impact':<10} "
        f"{'Ancienneté':<12} {'Similarité':<11} {'Famille'}"
    )
    print("-" * 115)
    for index, (info, name, similarity) in enumerate(rows, 1):
        print(
            f"{index:<10} {name:<35} {info['severity']:<10} {info['impact_label']:<10} "
            f"{str(info['age_days']) + ' j':<12} {similarity:<11.2f} {info['family']}"
        )


if __name__ == "__main__":
    main()
