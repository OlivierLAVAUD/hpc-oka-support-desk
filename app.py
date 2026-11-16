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
"""Interface Gradio du POC oka-support-desk."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
TICKETS = ROOT / "tickets"
PROFILE_DOC = ROOT / "docs" / "profile_alignment.md"

TICKET_NAMES = (
    sorted(path.name for path in TICKETS.iterdir() if path.is_dir())
    if TICKETS.is_dir()
    else []
)

FAMILIES = [
    "configuration",
    "rule-not-firing",
    "false-positives",
    "custom-enhancer",
    "missing-data",
    "notification",
    "training",
    "remote-visualization",
    "ccme",
]
COMPONENTS = [
    "HealthCheck",
    "DataEnhancer",
    "Webhook Bridge",
    "Formation",
    "Portail & Visualisation",
    "CCME",
]
DOMAINS = [
    "auto",
    "jobs",
    "kpi",
    "load",
    "resources",
    "congestion",
    "state",
    "throughput",
    "consumers",
    "concurrent_users",
]
CODE_LANGUAGES = {
    ".py": "python",
    ".sh": "bash",
    ".ps1": "powershell",
    ".conf": "nginx",
    ".yaml": "yaml",
    ".yml": "yaml",
}
LEVELS = ["débutant", "intermédiaire", "avancé", "débutant à intermédiaire"]

CSS = """
.gradio-container { max-width: 1280px !important; margin: 0 auto; }
#oka-header h1 { margin-bottom: 0.25rem; }
.oka-muted { color: #64748b; }
"""

HEADER = """
# 🛠️ OKA Support Desk

**POC Ingénieur Support UCit** — plateforme OKA (analytique et supervision HPC).

Cette interface expose les **8 outils IA + HITL** du POC, les **8 tickets** et
la matrice de couverture du profil UCit : classification, diagnostic, réponse
client, génération de règle, priorisation, formation, automatisations et
feedback R&D. Chaque sortie est une **proposition** : l'ingénieur relit, corrige
et valide avant toute action client.
"""

HITL_NOTE = """
> ⚠️ **Human In The Loop** — Aucune action n'est appliquée automatiquement.
> Les réponses client restent des brouillons et les règles générées doivent être
> vérifiées sur les 5 patterns OKA avant publication.
"""

OVERVIEW = """
## Portefeuille de tickets

8 tickets clients couvrent la méthode complète : qualifier → diagnostiquer →
résoudre → répondre → capitaliser. Le ticket 008 ajoute le portail, la
visualisation distante 2D/3D, Linux/Windows et AWS.

| Ticket | Sujet | Composant |
|---|---|---|
| TICKET-001 | Quota de core-hours | HealthCheck / resources |
| TICKET-002 | Règle silencieuse | HealthCheck / jobs |
| TICKET-003 | Faux positifs | HealthCheck / kpi |
| TICKET-004 | Coût personnalisé | Data Enhancer / costs |
| TICKET-005 | Données CO2 manquantes | Data Enhancer / CO2 |
| TICKET-006 | Notification Slack | Webhook Bridge |
| TICKET-007 | Formation de 150 utilisateurs | Formation |
| TICKET-008 | Portail de visualisation 3D | Portail & Visualisation |

Sélectionnez un ticket pour afficher ses livrables, ou lancez la priorisation
pour obtenir un ordre conseillé (sévérité, impact, ancienneté, similarité).
"""


def profile_markdown() -> str:
    """Load the UCit profile coverage matrix for the dedicated tab."""
    if not PROFILE_DOC.is_file():
        return "Matrice de couverture du profil indisponible."
    return PROFILE_DOC.read_text(encoding="utf-8", errors="replace")


def run_tool(
    tool: str, *args: str, stdin_text: str | None = None
) -> tuple[str, str, int]:
    """Run a support tool and capture its output, HITL journal and exit code."""
    try:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / f"{tool}.py"), *args],
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "", f"{tool} a dépassé le délai de 120 secondes.", 1
    return proc.stdout, proc.stderr, proc.returncode


def journal(stderr: str, return_code: int) -> str:
    """Render the HITL journal and any failure as Markdown."""
    sections = []
    if stderr.strip():
        sections.append("### ⚠️ Journal HITL\n```text\n" + stderr.strip() + "\n```")
    if return_code != 0:
        sections.append(f"**Échec de l'outil** — code de sortie `{return_code}`.")
    return "\n\n".join(sections) or "✅ Outil exécuté sans erreur."


def fenced(text: str, language: str = "text") -> str:
    """Wrap plain text in a Markdown code fence."""
    return f"```{language}\n{text.strip()}\n```"


def classify_request(request_text: str, request_file: str | None):
    """Classify a request from pasted text or an uploaded request.md."""
    if isinstance(request_file, list):
        request_file = request_file[0] if request_file else None
    if request_file:
        path = Path(request_file)
        if path.is_file():
            request_text = path.read_text(encoding="utf-8", errors="replace")

    if not request_text.strip():
        return {}, "⚠️ Saisissez une demande ou déposez un fichier `request.md`."

    stdout, stderr, return_code = run_tool("ticket_classifier", stdin_text=request_text)
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        payload = {"raw_output": stdout}
    return payload, journal(stderr, return_code)


def diagnose(family: str, component: str):
    """Generate a diagnostic checklist."""
    stdout, stderr, return_code = run_tool(
        "diagnostic_helper",
        "--family",
        family,
        "--component",
        component,
    )
    return stdout, journal(stderr, return_code)


def generate_response(diagnosis_text: str):
    """Generate a client-response draft from pasted diagnosis content."""
    if not diagnosis_text.strip():
        return "", "⚠️ Collez le contenu d'un `diagnosis.md`."

    with tempfile.TemporaryDirectory() as tmp:
        diagnosis_path = Path(tmp) / "diagnosis.md"
        diagnosis_path.write_text(diagnosis_text, encoding="utf-8")
        stdout, stderr, return_code = run_tool("response_generator", str(diagnosis_path))
        draft_path = Path(tmp) / "response.md"
        draft = (
            draft_path.read_text(encoding="utf-8")
            if draft_path.is_file()
            else stdout
        )
    return draft, journal(stderr, return_code)


def generate_rule(request_text: str, domain: str, rule_name: str, use_llm: bool = False):
    """Generate a HealthcheckRule skeleton from a natural-language request."""
    if not request_text.strip():
        return "⚠️ Décrivez la règle souhaitée.", "", "⚠️ Demande vide."

    args = []
    if domain and domain != "auto":
        args.extend(["--domain", domain])
    if rule_name.strip():
        args.extend(["--name", rule_name.strip()])
    if use_llm:
        args.append("--llm")

    stdout, stderr, return_code = run_tool("rule_generator", request_text, *args)
    marker = stdout.find('"""Rule:')
    if marker >= 0:
        checklist = stdout[:marker].strip()
        code = stdout[marker:].strip()
    else:
        checklist = stdout.strip()
        code = ""
    return checklist, code, journal(stderr, return_code)


def prioritize():
    """Render the ticket prioritization table."""
    stdout, stderr, return_code = run_tool(
        "ticket_prioritizer", "--tickets", str(TICKETS)
    )
    return fenced(stdout), journal(stderr, return_code)


def generate_training(users: int, level: str, needs: str):
    """Generate a training path for a client profile."""
    args = ["--users", str(int(users)), "--level", level]
    if needs.strip():
        args.extend(["--needs", needs])
    stdout, stderr, return_code = run_tool("training_generator", *args)
    return stdout, journal(stderr, return_code)


def automations():
    """Render automation opportunities based on ticket lessons."""
    stdout, stderr, return_code = run_tool(
        "automation_identifier", "--tickets", str(TICKETS)
    )
    return fenced(stdout), journal(stderr, return_code)


def rnd_feedback():
    """Render R&D irritants extracted from ticket lessons."""
    stdout, stderr, return_code = run_tool(
        "rnd_feedback_analyzer", "--tickets", str(TICKETS)
    )
    return fenced(stdout), journal(stderr, return_code)


def ticket_markdown(ticket_name: str) -> str:
    """Render every deliverable of a ticket as one Markdown document."""
    if not ticket_name:
        return "Sélectionnez un ticket."

    ticket_dir = TICKETS / ticket_name
    if not ticket_dir.is_dir():
        return f"Ticket introuvable : `{ticket_name}`."

    ordered = [
        ticket_dir / "request.md",
        ticket_dir / "qualification.md",
        ticket_dir / "diagnosis.md",
    ]
    resolution_dir = ticket_dir / "resolution"
    if resolution_dir.is_dir():
        ordered.extend(sorted(path for path in resolution_dir.iterdir() if path.is_file()))
    ordered.extend([ticket_dir / "response.md", ticket_dir / "lessons.md"])

    parts = [f"# {ticket_name}"]
    for path in ordered:
        if not path.is_file():
            continue
        relative = path.relative_to(ticket_dir)
        content = path.read_text(encoding="utf-8", errors="replace")
        parts.append(f"## `{relative}`")
        language = CODE_LANGUAGES.get(path.suffix.lower())
        if language:
            parts.append(fenced(content, language))
        else:
            parts.append(content)
        parts.append("---")
    return "\n\n".join(parts)


def build_app() -> gr.Blocks:
    """Build the Gradio application without launching a server."""
    with gr.Blocks(title="OKA Support Desk") as demo:
        gr.Markdown(HEADER, elem_id="oka-header")
        gr.Markdown(HITL_NOTE)

        with gr.Tabs():
            with gr.Tab("🏠 Accueil & tickets"):
                gr.Markdown(OVERVIEW)
                with gr.Row():
                    ticket_dropdown = gr.Dropdown(
                        choices=TICKET_NAMES,
                        value=TICKET_NAMES[0] if TICKET_NAMES else None,
                        label="Ticket à consulter",
                    )
                    ticket_button = gr.Button("Afficher le ticket", variant="primary")
                ticket_output = gr.Markdown()
                ticket_button.click(ticket_markdown, ticket_dropdown, ticket_output)

                gr.Markdown("### Priorisation du portefeuille")
                priority_button = gr.Button("Prioriser les tickets")
                priority_output = gr.Markdown()
                priority_journal = gr.Markdown()
                priority_button.click(
                    prioritize, [], [priority_output, priority_journal]
                )

            with gr.Tab("🎯 Profil & preuves"):
                gr.Markdown(profile_markdown())

            with gr.Tab("1 · Qualifier"):
                gr.Markdown(
                    "Collez une demande client ou déposez un `request.md`. "
                    "L'outil propose famille, sévérité, composant et confiance."
                )
                with gr.Row():
                    with gr.Column():
                        request_text = gr.Textbox(
                            label="Demande client",
                            lines=9,
                            placeholder=(
                                "Ex. : nous souhaitons des alertes à 80 % et 90 % "
                                "d'un quota de 10 000 core-hours..."
                            ),
                        )
                        request_file = gr.File(
                            label="ou fichier request.md",
                            file_types=[".md"],
                            file_count="single",
                            type="filepath",
                        )
                        classify_button = gr.Button("Classifier", variant="primary")
                    with gr.Column():
                        classification = gr.JSON(label="Classification proposée")
                        classify_journal = gr.Markdown()
                classify_button.click(
                    classify_request,
                    [request_text, request_file],
                    [classification, classify_journal],
                )

            with gr.Tab("2 · Diagnostiquer"):
                gr.Markdown(
                    "Générez une checklist de vérifications alignée sur les "
                    "patterns OKA (`min_jobs`, `ResultStatus`, `_FAILED_STATES`, "
                    "`BRIDGE_BEARER_TOKEN`, `ENERGY`)."
                )
                with gr.Row():
                    family = gr.Dropdown(
                        choices=FAMILIES, value="rule-not-firing", label="Famille"
                    )
                    component = gr.Dropdown(
                        choices=COMPONENTS, value="HealthCheck", label="Composant"
                    )
                diagnose_button = gr.Button("Générer la checklist", variant="primary")
                diagnose_output = gr.Markdown()
                diagnose_journal = gr.Markdown()
                diagnose_button.click(
                    diagnose,
                    [family, component],
                    [diagnose_output, diagnose_journal],
                )

            with gr.Tab("3 · Répondre"):
                gr.Markdown(
                    "Collez un `diagnosis.md` rempli. L'outil produit un brouillon "
                    "de réponse avec le bandeau **BROUILLON** ; aucune réponse n'est "
                    "envoyée automatiquement."
                )
                diagnosis_text = gr.Textbox(
                    label="Contenu du diagnostic",
                    lines=12,
                    placeholder="## Cause racine\n...\n\n## Solution apportée\n...",
                )
                response_button = gr.Button("Générer le brouillon", variant="primary")
                response_output = gr.Markdown()
                response_journal = gr.Markdown()
                response_button.click(
                    generate_response,
                    diagnosis_text,
                    [response_output, response_journal],
                )

            with gr.Tab("4 · Générer une règle"):
                gr.Markdown(
                    "Décrivez la règle en français. Le générateur produit un "
                    "squelette `HealthcheckRule` avec `params_model`, `evaluate`, "
                    "`_no_data_alert`, `CRITICAL` avant `HIGH` et garde-fou `min_jobs`."
                )
                with gr.Row():
                    with gr.Column():
                        rule_request = gr.Textbox(
                            label="Demande en langage naturel",
                            lines=5,
                            placeholder=(
                                "Alerter si le taux d'échec des jobs dépasse 10 %"
                            ),
                        )
                        rule_domain = gr.Dropdown(
                            choices=DOMAINS, value="auto", label="Domaine"
                        )
                        rule_name = gr.Textbox(
                            label="Nom technique (optionnel)",
                            placeholder="custom_jobs_threshold_rule",
                        )
                        rule_llm = gr.Checkbox(
                            value=False,
                            label="Utiliser Ollama (Qwen) — local et optionnel",
                        )
                        rule_button = gr.Button("Générer la règle", variant="primary")
                    with gr.Column():
                        rule_checklist = gr.Markdown(label="Checklist des 5 patterns")
                        rule_code = gr.Code(
                            label="Règle générée",
                            language="python",
                            lines=24,
                            interactive=False,
                        )
                        rule_journal = gr.Markdown()
                rule_button.click(
                    generate_rule,
                    [rule_request, rule_domain, rule_name, rule_llm],
                    [rule_checklist, rule_code, rule_journal],
                )

            with gr.Tab("5 · Former"):
                gr.Markdown(
                    "Construisez un parcours de formation progressif à partir du "
                    "profil du client."
                )
                with gr.Row():
                    users = gr.Number(value=150, precision=0, label="Utilisateurs")
                    level = gr.Dropdown(
                        choices=LEVELS,
                        value="débutant à intermédiaire",
                        label="Niveau",
                    )
                needs = gr.Textbox(
                    label="Besoins métiers",
                    placeholder="dashboards, chargeback, alertes GPU...",
                )
                training_button = gr.Button("Générer le parcours", variant="primary")
                training_output = gr.Markdown()
                training_journal = gr.Markdown()
                training_button.click(
                    generate_training,
                    [users, level, needs],
                    [training_output, training_journal],
                )

            with gr.Tab("6 · Capitaliser"):
                gr.Markdown(
                    "Analysez les `lessons.md` pour proposer des automatisations "
                    "et remonter les irritants produit à la R&D."
                )
                with gr.Row():
                    with gr.Column():
                        automation_button = gr.Button(
                            "Identifier les automatisations", variant="primary"
                        )
                        automation_output = gr.Markdown()
                        automation_journal = gr.Markdown()
                    with gr.Column():
                        rnd_button = gr.Button("Analyser le feedback R&D")
                        rnd_output = gr.Markdown()
                        rnd_journal = gr.Markdown()
                automation_button.click(
                    automations, [], [automation_output, automation_journal]
                )
                rnd_button.click(rnd_feedback, [], [rnd_output, rnd_journal])

        gr.Markdown(
            "---\n"
            "**Rappel HITL** : l'IA prépare, l'ingénieur valide. "
            "Les fichiers générés restent des propositions révisables."
        )
    return demo


def auth_config() -> tuple[str, str] | None:
    """Read optional basic-auth credentials from GRADIO_AUTH="user:password"."""
    raw = os.getenv("GRADIO_AUTH", "").strip()
    if not raw:
        return None
    user, separator, password = raw.partition(":")
    if not separator or not user or not password:
        raise ValueError("GRADIO_AUTH doit être au format 'utilisateur:motdepasse'.")
    return user, password


def main() -> None:
    """Launch the Gradio server."""
    demo = build_app()
    demo.queue()
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        auth=auth_config(),
        theme=gr.themes.Soft(),
        css=CSS,
    )


if __name__ == "__main__":
    main()
