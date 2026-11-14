#!/usr/bin/env python3
"""Ticket prioritizer — classe les tickets par sévérité, impact et ancienneté."""

import sys
from pathlib import Path


def _hitl_warning() -> None:
    print(
        "\n╔═══════════════════════════════════════════════════════════════╗\\n"
        "║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║\\n"
        "║  Cet ordre de priorité est un conseil, pas une décision.      ║\\n"
        "║  L'ingénieur valide l'ordre final de traitement.              ║\\n"
        "╚═══════════════════════════════════════════════════════════════╝\\n"
    )

SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}

def _read_qualification(ticket_dir: Path) -> dict:
    q_file = ticket_dir / "qualification.md"
    if not q_file.exists():
        return {"severity": "low", "family": "unknown"}
    text = q_file.read_text(encoding="utf-8")
    sev = "low"
    for s in ["critical", "high", "medium", "low"]:
        if f"**Niveau** : {s}" in text:
            sev = s
            break
    fam = "unknown"
    for f in ["configuration", "rule-not-firing", "false-positives",
              "custom-enhancer", "missing-data", "notification", "training"]:
        if f"**Famille** : {f}" in text:
            fam = f
            break
    return {"severity": sev, "family": fam}

def main() -> None:
    _hitl_warning()
    tickets_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tickets")
    rows = []
    for ticket_dir in sorted(tickets_dir.iterdir()):
        if not ticket_dir.is_dir():
            continue
        info = _read_qualification(ticket_dir)
        weight = SEVERITY_WEIGHT.get(info["severity"], 1)
        rows.append((weight, ticket_dir.name, info["severity"], info["family"]))
    rows.sort(reverse=True)
    print(f"{'Priorité':<10} {'Ticket':<35} {'Sévérité':<10} {'Famille'}")
    print("-" * 70)
    for i, (weight, name, sev, fam) in enumerate(rows, 1):
        print(f"{i:<10} {name:<35} {sev:<10} {fam}")

if __name__ == "__main__":
    main()
