#!/usr/bin/env python3
"""Response generator — génère un brouillon de réponse client à partir du diagnosis."""

import sys
from pathlib import Path

def _hitl_warning() -> None:
    print(
        "\n╔═══════════════════════════════════════════════════════════════╗\n"
        "║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║\n"
        "║  Ce brouillon de réponse doit être relu et modifié avant      ║\\n"
        "║  tout envoi au client. Aucun envoi automatique.              ║\\n"
        "╚═══════════════════════════════════════════════════════════════╝\\n",
        file=sys.stderr,
    )

def generate(diagnosis_path: str) -> str:
    text = Path(diagnosis_path).read_text(encoding="utf-8")

    cause = ""
    solution = ""
    for line in text.splitlines():
        if line.startswith("## Cause racine"):
            cause = line.split(":", 1)[1].strip() if ":" in line else ""
        if line.startswith("## Solution apportée"):
            solution = line.split(":", 1)[1].strip() if ":" in line else ""

    draft = f"""# Réponse client — [TICKET-ID]

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

    return draft

def main() -> None:
    import sys
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
