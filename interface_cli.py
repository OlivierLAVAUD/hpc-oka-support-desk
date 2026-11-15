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

"""Interface CLI pour le POC oka-support-desk."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
TICKETS = ROOT / "tickets"

BANNER = """============================================================
🔧 oka-support-desk - POC Support UCit
============================================================
Interface de gestion des tickets IA + HITL pour OKA
Plateforme : OKA (HPC analytique)"""

MENU = """MENU PRINCIPAL
--------------------------------------------------
1. Classifier un ticket
2. Aide au diagnostic
3. Générer une réponse client
4. Checklist de génération de règle HealthCheck
5. Prioriser les tickets
6. Identifier les automatisations possibles
7. Générer un parcours de formation
8. Analyser le feedback R&D
9. Afficher un ticket
0. Quitter
--------------------------------------------------"""


def ask(prompt: str) -> str:
    return input(prompt).strip()


def run_tool(name: str, *args: str) -> None:
    print(f"\n▶ {name}")
    print("=" * 50)
    try:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / f"{name}.py"), *args],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"❌ {name} a dépassé le délai de 60 secondes.")
        return

    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        print(f"❌ {name} a échoué (code {proc.returncode}).")
    print("=" * 50)


def classify_ticket() -> None:
    path = ask("Chemin du fichier request.md : ")
    if not path:
        print("❌ Chemin requis.")
        return
    run_tool("ticket_classifier", path)


def diagnose() -> None:
    family = ask("Famille (configuration, rule-not-firing, false-positives, ...) : ")
    component = ask("Composant (HealthCheck, DataEnhancer, Webhook Bridge, Formation) : ")
    if not family or not component:
        print("❌ Famille et composant requis.")
        return
    run_tool("diagnostic_helper", "--family", family, "--component", component)


def generate_response() -> None:
    path = ask("Chemin du fichier diagnosis.md : ")
    if not path:
        print("❌ Chemin requis.")
        return
    run_tool("response_generator", path)


def prioritize() -> None:
    run_tool("ticket_prioritizer", str(TICKETS))


def training() -> None:
    users = ask("Nombre d'utilisateurs [150] : ") or "150"
    run_tool("training_generator", users)


def show_ticket() -> None:
    tickets = sorted(path for path in TICKETS.iterdir() if path.is_dir())
    if not tickets:
        print("❌ Aucun ticket trouvé.")
        return

    print("\n📋 Tickets disponibles :")
    for index, ticket in enumerate(tickets, 1):
        print(f"{index}. {ticket.name}")

    choice = ask("\nNuméro du ticket (ou 'q' pour annuler) : ")
    if choice.lower() == "q":
        return

    try:
        ticket = tickets[int(choice) - 1]
    except (ValueError, IndexError):
        print("❌ Numéro invalide.")
        return

    print(f"\n{'=' * 60}\n📋 TICKET : {ticket.name}\n{'=' * 60}")
    for path in sorted(ticket.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ticket)
        content = path.read_text(encoding="utf-8", errors="replace")
        print(f"\n--- {relative} ---")
        for number, line in enumerate(content.splitlines()[:5], 1):
            print(f"  {number}: {line}")
        if len(content) > 100:
            print(f"  ... ({len(content)} caractères au total)")


def main() -> None:
    if not TICKETS.is_dir():
        print("❌ Ce script doit être exécuté depuis le répertoire oka-support-desk.")
        sys.exit(1)

    actions = {
        "1": classify_ticket,
        "2": diagnose,
        "3": generate_response,
        "4": lambda: run_tool("rule_generator"),
        "5": prioritize,
        "6": lambda: run_tool("automation_identifier"),
        "7": training,
        "8": lambda: run_tool("rnd_feedback_analyzer"),
        "9": show_ticket,
    }

    while True:
        print()
        print(BANNER)
        print(MENU)
        try:
            choice = ask("Choisir une option (0-9) : ")
        except EOFError:
            print("\n👋 Au revoir !")
            return

        if choice == "0":
            print("\n👋 Au revoir !")
            return

        action = actions.get(choice)
        if action is None:
            print("\n❌ Option invalide.")
            continue
        action()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption demandée. Au revoir !")
        sys.exit(0)
