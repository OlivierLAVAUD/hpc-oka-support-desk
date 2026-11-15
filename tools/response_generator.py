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

"""Response generator — génère un brouillon de réponse client à partir du diagnosis."""

import sys
from pathlib import Path

HITL_BANNER = """╔═══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Ce brouillon de réponse doit être relu et modifié avant      ║
║  tout envoi au client. Aucun envoi automatique.              ║
╚═══════════════════════════════════════════════════════════════╝"""


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER, file=sys.stderr)
    print(file=sys.stderr)


def _extract_section(text: str, title: str) -> str:
    """Return the body of a level-2 Markdown section, or an empty string."""
    target = title.strip().lower()
    body: list[str] = []
    collecting = False
    for line in text.splitlines():
        if line.startswith("## "):
            if collecting:
                break
            collecting = line[3:].strip().lower() == target
            continue
        if collecting:
            body.append(line)
    return chr(10).join(body).strip()


def generate(diagnosis_path: str) -> str:
    text = Path(diagnosis_path).read_text(encoding="utf-8")
    cause = _extract_section(text, "Cause racine")
    solution = _extract_section(text, "Solution apportée")

    return f"""# Réponse client — [TICKET-ID]

⚠️ **BROUILLON — À RELIRE ET MODIFIER AVANT ENVOI**

## Destinataire
[CLIENT_NOM] — [CLIENT_ORG]

## Objet
Suite à votre demande — [SUJET]

## Corps du message

Bonjour [CLIENT_PRENOM],

Nous faisons suite à votre demande concernant [SUJET_TICKET].

### Cause identifiée
{cause or "À compléter à partir du diagnostic"}

### Solution apportée
{solution or "À compléter à partir du diagnostic"}

### Preuve de résolution
À documenter (fichiers modifiés, règles republiées, tests effectués).

### Prévention
À compléter (recommandations pour éviter la récurrence).

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : [NOM] | Date : [DATE]
Bandeau BROUILLON supprimé : [OUI/NON]
"""


def main() -> None:
    _hitl_warning()
    if len(sys.argv) > 1:
        draft = generate(sys.argv[1])
        out_path = Path(sys.argv[1]).parent / "response.md"
        out_path.write_text(draft, encoding="utf-8")
        print(f"Brouillon généré : {out_path}")
    else:
        print("Usage: response_generator.py <diagnosis.md>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
