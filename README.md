# oka-support-desk — POC Ingénieur Support UCit

Dépôt de preuve de concept (POC) simulant un portefeuille de 7 tickets clients traités par un ingénieur support UCit sur la plateforme OKA (analytique et supervision HPC).

## 1. Contexte (candidature)

Poste : **Ingénieur Support** — UCit (Montpellier)  
Produit : **OKA** — plateforme Data Science pour environnements HPC  
https://uca.how | https://doc.oka.how

Ce POC démontre la capacité à analyser les dépôts sources d'extensibilité d'OKA, à qualifier/diagnostiquer/résoudre des tickets clients, et à capitaliser sur l'expérience via une méthode reproductible et des outils IA + HITL.

## 2. Ce que j'ai analysé (les 3 dépôts sources)

Les trois dépôts Git ont été lus en intégralité avant tout codage :

| Dépôt | Éléments | Fichiers clés |
|-------|----------|---------------|
| `oka_healthchecks` | 40 règles HealthCheck, 9 domaines | `resources/cores_account_quota_rule.py`, `jobs/failed_jobs_rule.py`, `kpi/high_cost_rule.py`, `load/core_load_rule.py` |
| `oka_dataenhancers` | 7 Data Enhancers, 5 catégories | `costs/costs_demo.py`, `CO2/carbon_cost_RTE.py` |
| `oka_webhooks` | 4 bridges webhook (SES, Slack, Jira, Reporting) | `oka-slack-bridge/app.py`, `oka-slack-bridge/.service` |

Tous sous licence Apache 2.0, version `2026.10.0`, testés contre **OKA 3.3.0**.

## 3. Ce que contient ce POC

```
oka-support-desk/
├── NOTES_ANALYSIS.md       # Preuve d'extraction des 3 dépôts
├── README.md               # Ce fichier
├── METHOD.md               # Méthode de support en 5 étapes
├── AI_METHOD.md            # Approche IA + HITL
├── pyproject.toml          # Dépendances Python
├── Makefile                # Commandes make test / make demo
├── LICENSE / NOTICE        # Apache 2.0 © 2026 UCit
├── .github/workflows/ci.yml# CI GitHub Actions (ruff + pytest)
├── templates/              # 4 templates de ticket
├── tickets/                # 7 tickets clients (7 × 6 fichiers)
├── tools/                  # 8 outils IA + HITL
├── docs/                   # runbook, known_issues, escalation_matrix
└── tests/                  # 3 tests de contrat et de bon fonctionnement
```

## 4. Ce que cela démontre (tableau mission → preuve)

| Mission | Preuve dans le POC |
|---------|-------------------|
| Comprendre le contrat `HealthcheckRule` | `tickets/TICKET-001/.../cores_account_quota_rule.py` — params_model Pydantic, evaluate, _no_data_alert, CRITICAL avant HIGH, min_jobs |
| Comprendre le contrat `DataEnhancer` | `tickets/TICKET-004/.../custom_cost_enhancer.py` — params_model Pydantic, run, préfixe Cust_, noms réservés |
| Comprendre le payload webhook | `tickets/TICKET-006/.../diagnosis.md` — {subject, body}, Bearer token, routes /health + /notify |
| Patterns UCit | `tools/rule_generator.py` — frozenset, _FAILED_STATES, _no_data_alert, CRITICAL avant HIGH |
| Méthode support reproductible | `METHOD.md` — qualifier → diagnostiquer → résoudre → répondre → capitaliser |
| IA + HITL | `tools/*.py` — chaque outil affiche un avertissement "À valider par l'ingénieur" |
| Tests de contrat | `tests/test_resolution_contracts.py` — vérifie params_model, _no_data_alert, CRITICAL avant HIGH |

## 5. Comment exécuter

```bash
# Installation
make install

# Lint
make lint

# Tests
make test

# Démo rapide
make demo
```

## 6. Limites assumées

- Pas d'instance OKA réelle : les règles sont statiques, non exécutées contre une plateforme
- Pas de LLM obligatoire : fallback heuristique déterministe documenté (Ollama optionnel)
- 7 tickets qualitatifs, simulés, pour démontrer la méthode

## 7. Références

- Dépôts sources : `./oka_healthchecks`, `./oka_dataenhancers`, `./oka_webhooks` (racine du workspace)
- Documentation OKA : https://doc.oka.how
- Site UCit : https://uca.how
- URL SSH du dépôt : git@ssh.bitbucket.org:lavaud_olivier/hpc-oka-support-desk.git
