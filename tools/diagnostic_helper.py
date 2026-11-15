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

"""Diagnostic helper — checklist de vérifications par famille de ticket."""

import argparse
import sys

HITL_BANNER = """╔═══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Cette checklist est une proposition. L'ingénieur documente   ║
║  chaque vérification et valide la cause racine.              ║
╚═══════════════════════════════════════════════════════════════╝"""

CHECKLISTS = {
    "configuration": [
        "- [ ] Règle/enhancer existe dans le dépôt source",
        "- [ ] Contrat OKA respecté (params_model, evaluate/run)",
        "- [ ] Tous les champs params ont une valeur default",
        "- [ ] Pattern CRITICAL avant HIGH dans _resolve_alert_level",
        "- [ ] Paramètres du client correctement injectés",
    ],
    "rule-not-firing": [
        "- [ ] Règle publiée sur le workload",
        "- [ ] Nombre de jobs >= min_jobs (guard silencieux)",
        "- [ ] ResultStatus == OK du provider",
        "- [ ] États d'échec présents dans _FAILED_STATES",
        "- [ ] Pas de retour [] silencieux sans alerte OK",
    ],
    "false-positives": [
        "- [ ] Seuils par défaut adaptés à la volumétrie du client",
        "- [ ] Garde-fou min_jobs présent pour lisser les pics",
        "- [ ] CRITICAL vérifié avant HIGH",
        "- [ ] Historique des coûts analysé pour recalibrage",
    ],
    "custom-enhancer": [
        "- [ ] params_model Pydantic avec valeurs default",
        "- [ ] run(self, data, **kwargs) -> pd.DataFrame",
        "- [ ] Colonne réservée 'Cost' utilisée (pas de préfixe Cust_)",
        "- [ ] Pattern de compte avec re.compile() + str.match()",
        "- [ ] Préfixe Cust_ pour colonnes non réservées",
    ],
    "missing-data": [
        "- [ ] Colonne requise présente dans le DataFrame",
        "- [ ] Enhancer dépendant exécuté en amont",
        "- [ ] Ordre d'exécution des enhancers vérifié",
        "- [ ] Dépendances externes installées (pymysql, requests, etc.)",
    ],
    "notification": [
        "- [ ] Bridge opérationnel (GET /health OK)",
        "- [ ] Token Bearer aligné entre OKA et le bridge",
        "- [ ] Routes POST /notify et GET /notify présentes",
        "- [ ] Logs du bridge vérifiés (journalctl, 401)",
        "- [ ] Payload OKA {subject, body} respecté",
    ],
    "training": [
        "- [ ] Nombre d'utilisateurs et niveaux identifiés",
        "- [ ] Besoins métiers recensés (dashboards, rapports, alertes)",
        "- [ ] Parcours en modules progressifs défini",
        "- [ ] Contenu s'appuyant sur les 3 dépôts sources",
    ],
    "remote-visualization": [
        "- [ ] DNS, certificat TLS et chaîne de reverse proxy validés",
        "- [ ] Groupe cible ALB healthy et health check sur /health",
        "- [ ] WebSocket activé : en-têtes Upgrade/Connection et timeout ALB",
        "- [ ] Service TurboVNC actif et port noVNC en écoute locale",
        "- [ ] VirtualGL actif : vglrun glxinfo -B affiche la GPU, pas llvmpipe",
        "- [ ] Pilote GPU et bibliothèques EGL/GLX disponibles (nvidia-smi)",
        "- [ ] Groupes SSO/LDAP et plages IP autorisées vérifiés",
        "- [ ] Client Windows : navigateur à jour, WebGL et proxy compatibles",
    ],
    "ccme": [
        "- [ ] Version CCME et matrice de compatibilité OKA validées",
        "- [ ] Prérequis Linux/Windows, comptes de service et permissions vérifiés",
        "- [ ] Base de données, sauvegarde et procédure de rollback disponibles",
        "- [ ] SSO/LDAP/OIDC, TLS et reverse proxy validés",
        "- [ ] Licence et connectivité OKA/CCME opérationnelles",
        "- [ ] Tests de fumée, supervision et documentation client à jour",
    ],
}

COMPONENT_NOTES = {
    "healthcheck": "Vérifier les providers (self.jobs, self.cluster_load, self.kpi, etc.)",
    "dataenhancer": "Vérifier les colonnes du DataFrame et les dépendances externes",
    "webhook": "Vérifier BRIDGE_BEARER_TOKEN et les routes Flask",
    "formation": "Vérifier les prérequis client et la disponibilité des salles",
    "jobs": "Vérifier self.jobs.scan_jobs(), min_jobs et _FAILED_STATES",
    "resources": "Vérifier self.cores.get_grouped_distribution() et grouping_size",
    "kpi": "Vérifier self.kpi.get_cost_metrics() et ResultStatus",
    "load": "Vérifier self.cluster_load et les seuils de charge",
    "costs": "Vérifier oka_constants.COST, COREHOURS et GPUHOURS",
    "co2": "Vérifier ENERGY, CARBON_FOOTPRINT et l'ordre des enhancers",
    "visualisation": "Vérifier GPU, VirtualGL, TurboVNC, noVNC, WebSocket et timeout ALB",
    "portail": "Vérifier branding, SSO, plages IP, routes et santé du reverse proxy",
    "ccme": "Vérifier version, licence, SSO, base de données et intégration OKA",
    "aws": "Vérifier ALB, groupe cible, WAF, groupes de sécurité et timeout",
}


def _component_note(component: str) -> str:
    lower = component.lower()
    for key, note in COMPONENT_NOTES.items():
        if key in lower:
            return note
    return "Aucune note spécifique"


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER, file=sys.stderr)
    print(file=sys.stderr)


def generate(family: str, component: str) -> str:
    lines = [f"# Checklist de diagnostic — {family} / {component}", ""]
    lines.append("## Vérifications générales (patterns OKA)")
    lines.append("")
    lines.extend(
        CHECKLISTS.get(
            family,
            ["- [ ] Aucune vérification définie pour cette famille"],
        )
    )
    lines.extend(["", f"## Note composant ({component})", ""])
    lines.append(f"- [ ] {_component_note(component)}")
    lines.extend(
        [
            "",
            "## Résultat (à remplir par l'ingénieur)",
            "",
            "- Cause racine : _______________________________________",
            "- Preuves : _____________________________________________",
            "- Solution : ____________________________________________",
            "",
        ]
    )
    return chr(10).join(lines)


def main() -> None:
    _hitl_warning()
    parser = argparse.ArgumentParser(description="Diagnostic helper for OKA support tickets")
    parser.add_argument("--family", required=True, help="Famille de ticket")
    parser.add_argument("--component", required=True, help="Composant OKA")
    args = parser.parse_args()
    print(generate(args.family, args.component))


if __name__ == "__main__":
    main()
