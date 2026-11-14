#!/usr/bin/env python3
"""Diagnostic helper — checklist de vérifications par famille de ticket."""

import argparse

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
}

COMPONENT_NOTES = {
    "HealthCheck": "Vérifier les providers (self.jobs, self.cluster_load, self.kpi, etc.)",
    "DataEnhancer": "Vérifier les colonnes du DataFrame et les dépendances externes",
    "Webhook Bridge": "Vérifier BRIDGE_BEARER_TOKEN et les routes Flask",
    "Formation": "Vérifier les prérequis client et la disponibilité des salles",
}

def generate(family: str, component: str) -> str:
    lines = [f"# Checklist de diagnostic — {family} / {component}\\n"]
    lines.append("## Vérifications générales (patterns OKA)\\n")
    for item in CHECKLISTS.get(family, ["- [ ] Aucune vérification définie pour cette famille"]):
        lines.append(item)
    lines.append(f"\\n## Note composant ({component})\\n")
    lines.append(f"- [ ] {COMPONENT_NOTES.get(component, 'Aucune note spécifique')}\\n")
    lines.append("\\n## Résultat (à remplir par l'ingénieur)\\n")
    lines.append("- Cause racine : _______________________________________\\n")
    lines.append("- Preuves : _____________________________________________\\n")
    lines.append("- Solution : ____________________________________________\\n")
    return "\\n".join(lines)

def main() -> None:
    import sys
    parser = argparse.ArgumentParser(description="Diagnostic helper for OKA support tickets")
    parser.add_argument("--family", required=True, help="Famille de ticket")
    parser.add_argument("--component", required=True, help="Composant OKA")
    args = parser.parse_args()
    print(generate(args.family, args.component))

if __name__ == "__main__":
    main()
